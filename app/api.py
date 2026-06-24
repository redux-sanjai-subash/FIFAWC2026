"""JSON API consumed by the Next.js frontend.

The whole app used to render Jinja templates; it is now an API-only Flask
service. Authentication stays exactly as before: a username-only session
cookie. Because the Next.js dev server proxies ``/api`` to Flask, the browser
sees a single origin and the session cookie just works.
"""

from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, g, jsonify, request, session
import os
import json
from sqlalchemy.exc import IntegrityError, OperationalError

from .db import db
from .models import Match, Prediction, User
from .utils.football_data import (
    FootballDataSyncError,
    fetch_world_cup_scorers,
    fetch_world_cup_squad_players,
    sync_world_cup_matches,
)
from .utils.potm_data import PotmSourceError, fetch_potm_for_matches
from .utils.scoring import build_leaderboard
from .utils.world_cup_data import (
    MVP_PLAYER_OPTIONS,
    QUALIFIED_TEAMS,
    SEEDED_MATCHES,
    TEAM_LOOKUP,
    seed_matches_if_empty,
    team_choices,
)


api_bp = Blueprint("api", __name__, url_prefix="/api")

DEFAULT_FLAG = "\U0001F3F3️"  # 🏳️

# All kickoff times are stored as naive UTC (football-data.org is UTC). India
# has no DST, so a fixed +05:30 offset is exact.
IST = timezone(timedelta(hours=5, minutes=30))
VISIBLE_BEFORE = timedelta(hours=24)   # fixtures appear 24h before kickoff
LOCK_AFTER = timedelta(minutes=15)    # picks close 15 min after kickoff


def _utc_now():
    return datetime.utcnow()


def _utc_iso(naive_utc):
    """ISO 8601 instant (UTC) so the browser can compute countdowns correctly."""
    return naive_utc.replace(tzinfo=timezone.utc).isoformat()


def _ist_string(naive_utc):
    aware = naive_utc.replace(tzinfo=timezone.utc).astimezone(IST)
    return aware.strftime("%d %b %Y · %I:%M %p IST")


_last_football_data_sync = None
_FOOTBALL_DATA_SYNC_THROTTLE_SECONDS = 300
_last_potm_sync = None
_POTM_SYNC_THROTTLE_SECONDS = 300


def _auto_sync_football_data():
    global _last_football_data_sync
    if not current_app.config["FOOTBALL_DATA_API_KEY"]:
        return

    now = datetime.utcnow()
    if _last_football_data_sync and (now - _last_football_data_sync).total_seconds() < _FOOTBALL_DATA_SYNC_THROTTLE_SECONDS:
        return

    try:
        sync_world_cup_matches(
            current_app.config["FOOTBALL_DATA_BASE_URL"],
            current_app.config["FOOTBALL_DATA_API_KEY"],
            current_app.config["FOOTBALL_DATA_COMPETITION_CODE"],
        )
    except FootballDataSyncError:
        pass
    finally:
        _last_football_data_sync = now

    _auto_sync_potm_data()


def _auto_sync_potm_data():
    global _last_potm_sync
    provider = (current_app.config.get("POTM_PROVIDER") or "manual").strip().lower()
    if provider == "manual":
        return

    if not current_app.config.get("POTM_HTTP_ENDPOINT"):
        return

    now = datetime.utcnow()
    throttle_seconds = current_app.config.get("POTM_SYNC_THROTTLE_SECONDS", 300)
    if _last_potm_sync and (now - _last_potm_sync).total_seconds() < throttle_seconds:
        return

    match_ids = [
        match.api_match_id
        for match in Match.query.filter(Match.api_match_id != None, Match.winner != None, Match.potm_winner == None).all()
        if match.api_match_id
    ]

    if not match_ids:
        _last_potm_sync = now
        return

    try:
        potm_mapping = fetch_potm_for_matches(
            provider,
            current_app.config.get("POTM_HTTP_ENDPOINT"),
            current_app.config.get("POTM_HTTP_API_KEY"),
            current_app.config.get("FOOTBALL_DATA_COMPETITION_CODE"),
            match_ids,
        )
        if potm_mapping:
            for match in Match.query.filter(Match.api_match_id.in_(potm_mapping.keys()), Match.potm_winner == None).all():
                potm_name = potm_mapping.get(match.api_match_id)
                if potm_name:
                    match.potm_winner = potm_name
            db.session.commit()
    except PotmSourceError:
        pass
    finally:
        _last_potm_sync = now


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def serialize_user(user):
    if not user:
        return None
    team = TEAM_LOOKUP.get(user.favorite_team or "")
    return {
        "id": user.id,
        "username": user.username,
        "favorite_team": user.favorite_team,
        "favorite_team_flag": team["flag"] if team else None,
        "favorite_team_code": team["code"] if team else None,
    }


def serialize_team(team):
    return {
        "name": team["name"],
        "code": team["code"],
        "flag": team["flag"],
        "confederation": team["confederation"],
    }


def _lock_override_for(match_id):
    raw = _load_lock_overrides().get(str(match_id))
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    return {"lock_extension_minutes": raw}


def serialize_match(match, prediction=None, potm_options=None, now=None):
    now = now or _utc_now()
    team_a = TEAM_LOOKUP.get(match.team_a)
    team_b = TEAM_LOOKUP.get(match.team_b)

    kickoff = match.kickoff_time
    already_picked = prediction is not None
    # Consider per-match lock extension (minutes) and reopen flags from overrides
    override = _lock_override_for(match.id)
    extension_minutes = int(override.get("lock_extension_minutes") or 0)
    reopen_picks = bool(override.get("reopen_picks"))

    visible = now >= kickoff - VISIBLE_BEFORE
    selection_closed = now >= kickoff + LOCK_AFTER + timedelta(minutes=extension_minutes)
    if reopen_picks:
        selection_closed = False
    # A pick is possible only while visible, before the post-kickoff cutoff, not
    # admin-locked, and not already made (picks are final).
    can_pick = visible and not selection_closed and not match.is_locked and not already_picked

    return {
        "id": match.id,
        "team_a": match.team_a,
        "team_b": match.team_b,
        "team_a_flag": team_a["flag"] if team_a else DEFAULT_FLAG,
        "team_b_flag": team_b["flag"] if team_b else DEFAULT_FLAG,
        "team_a_code": team_a["code"] if team_a else "",
        "team_b_code": team_b["code"] if team_b else "",
        "stage": match.stage or "World Cup",
        "venue": match.venue or "Official venue",
        "kickoff_time": _utc_iso(kickoff),
        "kickoff_ist": _ist_string(kickoff),
        "lock_time": _utc_iso(kickoff + LOCK_AFTER + timedelta(minutes=extension_minutes)),
        "winner": match.winner,
        "potm_winner": match.potm_winner,
        "is_locked": match.is_locked,
        "visible": visible,
        "selection_closed": selection_closed,
        "already_picked": already_picked,
        "can_pick": can_pick,
        "prediction": prediction.prediction if prediction else None,
        "potm_prediction": prediction.potm_prediction if prediction else None,
        "potm_options": potm_options or [],
        "lock_extension_minutes": extension_minutes,
        "reopen_picks": reopen_picks,
    }


def _player_options_by_team():
    players = list(MVP_PLAYER_OPTIONS)
    api_debug_teams = set()

    if current_app.config["FOOTBALL_DATA_API_KEY"]:
        try:
            players = fetch_world_cup_squad_players(
                current_app.config["FOOTBALL_DATA_BASE_URL"],
                current_app.config["FOOTBALL_DATA_API_KEY"],
                current_app.config["FOOTBALL_DATA_COMPETITION_CODE"],
            ) or players
        except FootballDataSyncError:
            pass

    grouped = {}
    for player in players:
        grouped.setdefault(player["team"], [])
        if player["team"] not in api_debug_teams:
            api_debug_teams.add(player["team"])
        if player["name"] not in grouped[player["team"]]:
            grouped[player["team"]].append(player["name"])

    for team_name in grouped:
        grouped[team_name].sort()
    
    # Debug: Log all unique team names to help identify format issues
    current_app.logger.info(f"Player teams available: {sorted(grouped.keys())}")
    
    return grouped


# File-backed per-match lock extension overrides (minutes). Stored in instance/lock_overrides.json
def _overrides_path():
    try:
        path = current_app.instance_path
    except Exception:
        path = os.path.join(os.path.dirname(__file__), "..", "instance")
    return os.path.join(path, "lock_overrides.json")


def _load_lock_overrides():
    path = _overrides_path()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except Exception:
        current_app.logger.exception("Failed to read lock overrides")
        return {}


def _save_lock_overrides(mapping):
    path = _overrides_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(mapping, fh)
    except Exception:
        current_app.logger.exception("Failed to write lock overrides")


def _potm_options_for(match, grouped):
    aliases = {
        "Cape Verde Islands": "Cabo Verde",
        "Bosnia-Herzegovina": "Bosnia and Herzegovina",
        "Bosnia & Herzegovina": "Bosnia and Herzegovina",
        "Bosnia": "Bosnia and Herzegovina",
        "BIH": "Bosnia and Herzegovina",
        "Bosnia-H.": "Bosnia and Herzegovina",
    }

    team_a = aliases.get(match.team_a, match.team_a)
    team_b = aliases.get(match.team_b, match.team_b)

    seen = []
    for name in grouped.get(team_a, []) + grouped.get(team_b, []):
        if name not in seen:
            seen.append(name)

    return seen


def _stats():
    return {
        "teams": len(QUALIFIED_TEAMS),
        "matches": Match.query.count() or len(SEEDED_MATCHES),
        "hosts": 3,
    }


def require_login():
    if not g.current_user:
        return jsonify({"ok": False, "message": "Enter a username first."}), 401
    return None


def require_admin():
    # Minimal admin guard: only the user with username 'matchadmin' is allowed.
    if not g.current_user or (g.current_user and g.current_user.username != "matchadmin"):
        return jsonify({"ok": False, "message": "Admin access required."}), 403
    return None


@api_bp.before_app_request
def load_session_user():
    g.current_user = get_current_user()


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
@api_bp.get("/auth/me")
def auth_me():
    return jsonify({"user": serialize_user(g.current_user)})


@api_bp.post("/auth/register")
def auth_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    favorite_team = (data.get("favorite_team") or "").strip() or None

    if not username:
        return jsonify({"ok": False, "message": "Username is required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"ok": False, "message": "That username already exists. Please log in instead."}), 409

    user = User(username=username, favorite_team=favorite_team)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"ok": False, "message": "That username already exists. Please log in instead."}), 409
    except OperationalError:
        db.session.rollback()
        current_app.logger.exception("Database operational error during registration")
        return jsonify({"ok": False, "message": "Registration failed. Please try again."}), 500
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to register user")
        return jsonify({"ok": False, "message": "Registration failed. Please try again."}), 500

    session["user_id"] = user.id
    return jsonify({"ok": True, "user": serialize_user(user)})


@api_bp.post("/auth/login")
def auth_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()

    if not username:
        return jsonify({"ok": False, "message": "Username is required."}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"ok": False, "message": "That username does not exist yet. Please register first."}), 404

    session["user_id"] = user.id
    return jsonify({"ok": True, "user": serialize_user(user)})


@api_bp.post("/auth/logout")
def auth_logout():
    session.clear()
    return jsonify({"ok": True})


@api_bp.get("/users")
def list_users():
    users = User.query.order_by(User.username.asc()).all()
    return jsonify({"users": [serialize_user(user) for user in users]})


# --------------------------------------------------------------------------- #
# Reference data
# --------------------------------------------------------------------------- #
@api_bp.get("/teams")
def list_teams():
    return jsonify({"teams": [serialize_team(team) for team in team_choices()]})


@api_bp.get("/stats")
def stats():
    return jsonify({"stats": _stats()})


# --------------------------------------------------------------------------- #
# Dashboard + predictions
# --------------------------------------------------------------------------- #
@api_bp.get("/dashboard")
def dashboard():
    guard = require_login()
    if guard:
        return guard

    _auto_sync_football_data()
    now = _utc_now()
    matches = Match.query.order_by(Match.kickoff_time.asc()).all()
    grouped = _player_options_by_team()

    predictions = {
        row.match_id: row
        for row in Prediction.query.filter_by(user_id=g.current_user.id).all()
    }

    def pack(match):
        return serialize_match(match, predictions.get(match.id), _potm_options_for(match, grouped), now)

    open_matches = []     # visible & pickable right now
    locked_matches = []   # visible but closed / already picked / admin-locked
    upcoming = []         # not yet visible (more than 24h away)

    for match in matches:
        if now < match.kickoff_time - VISIBLE_BEFORE:
            upcoming.append(match)
            continue
        packed = pack(match)
        (open_matches if packed["can_pick"] else locked_matches).append(packed)

    # Reveal only *when* the next fixture unlocks — never the teams.
    next_unlock = None
    if upcoming:
        soonest = min(upcoming, key=lambda m: m.kickoff_time)
        next_unlock = {
            "unlock_time": _utc_iso(soonest.kickoff_time - VISIBLE_BEFORE),
            "count": len(upcoming),
        }

    return jsonify(
        {
            "open_matches": open_matches,
            "locked_matches": locked_matches,
            "next_unlock": next_unlock,
            "counts": {
                "picks": len(predictions),
                "open": len(open_matches),
                "upcoming": len(upcoming),
                "total": len(matches),
            },
            "stats": _stats(),
        }
    )


@api_bp.post("/predictions/<int:match_id>")
def save_prediction(match_id):
    guard = require_login()
    if guard:
        return guard

    now = _utc_now()
    match = Match.query.get_or_404(match_id)
    data = request.get_json(silent=True) or {}
    choice = (data.get("prediction") or "").strip()
    potm_prediction = (data.get("potm_prediction") or "").strip()
    allowed_choices = {match.team_a, match.team_b, "Draw"}

    existing = Prediction.query.filter_by(user_id=g.current_user.id, match_id=match.id).first()

    # Picks are final — they can never be edited once made.
    if existing:
        return jsonify({"ok": False, "message": "Your pick is locked in and cannot be changed."}), 409

    if now < match.kickoff_time - VISIBLE_BEFORE:
        return jsonify({"ok": False, "message": "This fixture is not open for picks yet."}), 423

    if match.is_locked:
        return jsonify({"ok": False, "message": "That match is locked."}), 423

    # Respect any per-match extension and reopen flag for the lock deadline
    override = _lock_override_for(match.id)
    extension_minutes = int(override.get("lock_extension_minutes") or 0)
    reopen_picks = bool(override.get("reopen_picks"))
    lock_deadline = match.kickoff_time + LOCK_AFTER + timedelta(minutes=extension_minutes)
    if now >= lock_deadline and not reopen_picks:
        return jsonify({"ok": False, "message": "Picks closed (post-deadline)."}), 423

    if choice not in allowed_choices:
        return jsonify({"ok": False, "message": "Pick Team A, Team B, or Draw."}), 400

    if not potm_prediction:
        return jsonify({"ok": False, "message": "Choose a Player of the Match."}), 400

    prediction = Prediction(
        user_id=g.current_user.id,
        match_id=match.id,
        prediction=choice,
        potm_prediction=potm_prediction,
    )
    db.session.add(prediction)
    db.session.commit()

    return jsonify(
        {
            "ok": True,
            "match_id": match.id,
            "prediction": prediction.prediction,
            "potm_prediction": prediction.potm_prediction,
            "saved_count": Prediction.query.filter_by(user_id=g.current_user.id).count(),
            "message": "Pick locked in",
        }
    )


# --------------------------------------------------------------------------- #
# Golden Boot
# --------------------------------------------------------------------------- #
@api_bp.get("/scorers")
def scorers():
    scorer_rows = []
    api_status = None
    api_enabled = bool(current_app.config["FOOTBALL_DATA_API_KEY"])

    if api_enabled:
        try:
            scorer_rows = fetch_world_cup_scorers(
                current_app.config["FOOTBALL_DATA_BASE_URL"],
                current_app.config["FOOTBALL_DATA_API_KEY"],
                current_app.config["FOOTBALL_DATA_COMPETITION_CODE"],
            )
        except FootballDataSyncError as error:
            api_status = str(error)

    for row in scorer_rows:
        team = TEAM_LOOKUP.get(row.get("team", ""))
        row["team_flag"] = team["flag"] if team else None

    return jsonify(
        {
            "scorers": scorer_rows,
            "api_enabled": api_enabled,
            "api_status": api_status,
        }
    )


# --------------------------------------------------------------------------- #
# Leaderboard
# --------------------------------------------------------------------------- #
@api_bp.get("/leaderboard")
def leaderboard():
    _auto_sync_football_data()
    users = User.query.order_by(User.username.asc()).all()
    rows = build_leaderboard(users, current_app.config["MATCH_POINTS"], current_app.config["POTM_POINTS"])

    for index, row in enumerate(rows, start=1):
        row["rank"] = index
        team = TEAM_LOOKUP.get(row["favorite_team"])
        row["favorite_team_flag"] = team["flag"] if team else None

    return jsonify(
        {
            "rows": rows,
            "podium": rows[:3],
            "match_points": current_app.config["MATCH_POINTS"],
            "potm_points": current_app.config["POTM_POINTS"],
            "current_username": g.current_user.username if g.current_user else None,
        }
    )


# --------------------------------------------------------------------------- #
# Admin
# --------------------------------------------------------------------------- #
@api_bp.get("/admin/matches")
def admin_matches():
    guard = require_admin()
    if guard:
        return guard

    matches = Match.query.order_by(Match.kickoff_time.asc()).all()
    grouped = _player_options_by_team()
    return jsonify(
        {
            "matches": [
                serialize_match(match, potm_options=_potm_options_for(match, grouped))
                for match in matches
            ],
            "api_enabled": bool(current_app.config["FOOTBALL_DATA_API_KEY"]),
            "teams": [serialize_team(team) for team in team_choices()],
        }
    )


@api_bp.post("/admin/matches")
def admin_add_match():
    guard = require_admin()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    team_a = (data.get("team_a") or "").strip()
    team_b = (data.get("team_b") or "").strip()
    stage = (data.get("stage") or "").strip() or "Custom Fixture"
    venue = (data.get("venue") or "").strip() or "Tournament Venue"
    kickoff_raw = (data.get("kickoff_time") or "").strip()

    if not team_a or not team_b or not kickoff_raw:
        return jsonify({"ok": False, "message": "Team A, Team B, and kickoff time are required."}), 400

    try:
        kickoff_local = datetime.strptime(kickoff_raw, "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({"ok": False, "message": "Kickoff time must use the datetime picker format."}), 400

    # Admin enters the kickoff in IST; store it as naive UTC for consistency.
    kickoff_time = kickoff_local.replace(tzinfo=IST).astimezone(timezone.utc).replace(tzinfo=None)

    match = Match(team_a=team_a, team_b=team_b, stage=stage, venue=venue, kickoff_time=kickoff_time)
    db.session.add(match)
    db.session.commit()
    return jsonify({"ok": True, "message": "Match added.", "match": serialize_match(match)})


@api_bp.patch("/admin/matches/<int:match_id>")
def admin_update_match(match_id):
    guard = require_admin()
    if guard:
        return guard

    match = Match.query.get_or_404(match_id)
    data = request.get_json(silent=True) or {}
    winner = (data.get("winner") or "").strip() or None
    potm_winner = (data.get("potm_winner") or "").strip() or None
    is_locked = bool(data.get("is_locked"))
    allowed_winners = {match.team_a, match.team_b, "Draw", None}

    if winner not in allowed_winners:
        return jsonify({"ok": False, "message": "Winner must be Team A, Team B, Draw, or blank."}), 400

    match.winner = winner
    match.potm_winner = potm_winner
    match.is_locked = is_locked

    lock_extension = data.get("lock_extension_minutes")
    reopen_picks = data.get("reopen_picks")
    if lock_extension is not None or reopen_picks is not None:
        overrides = _load_lock_overrides()
        entry = overrides.get(str(match.id))
        if isinstance(entry, dict):
            settings = dict(entry)
        elif entry is None:
            settings = {}
        else:
            settings = {"lock_extension_minutes": entry}

        if lock_extension is not None:
            try:
                minutes = int(lock_extension)
            except (TypeError, ValueError):
                return jsonify({"ok": False, "message": "lock_extension_minutes must be an integer."}), 400
            if minutes and minutes > 0:
                settings["lock_extension_minutes"] = minutes
            else:
                settings.pop("lock_extension_minutes", None)

        if reopen_picks is not None:
            settings["reopen_picks"] = bool(reopen_picks)

        if settings:
            overrides[str(match.id)] = settings
        else:
            overrides.pop(str(match.id), None)
        _save_lock_overrides(overrides)
    db.session.commit()
    return jsonify({"ok": True, "message": "Match updated.", "match": serialize_match(match)})


@api_bp.post("/admin/seed")
def admin_seed():
    guard = require_admin()
    if guard:
        return guard

    seed_matches_if_empty()
    return jsonify({"ok": True, "message": "Starter World Cup fixtures are ready."})


@api_bp.post("/admin/sync")
def admin_sync():
    guard = require_admin()
    if guard:
        return guard

    try:
        synced = sync_world_cup_matches(
            current_app.config["FOOTBALL_DATA_BASE_URL"],
            current_app.config["FOOTBALL_DATA_API_KEY"],
            current_app.config["FOOTBALL_DATA_COMPETITION_CODE"],
        )
        _auto_sync_potm_data()
        return jsonify({"ok": True, "message": f"Synced {synced} matches from football-data.org."})
    except FootballDataSyncError as error:
        return jsonify({"ok": False, "message": str(error)}), 502

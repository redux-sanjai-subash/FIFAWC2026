from datetime import datetime
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..db import db
from ..models import Match
from .world_cup_data import normalize_team_name


class FootballDataSyncError(Exception):
    pass


def _safe_team_name(match_payload, side):
    value = ((match_payload.get(side) or {}).get("name")) or ""
    return normalize_team_name(str(value).strip())


def _winner_name(match_payload, team_a, team_b):
    winner_code = ((match_payload.get("score") or {}).get("winner") or "").upper()
    if winner_code == "HOME_TEAM":
        return team_a
    if winner_code == "AWAY_TEAM":
        return team_b
    if winner_code == "DRAW":
        return "Draw"
    return None


def sync_world_cup_matches(base_url, api_key, competition_code="WC", season=2026):
    if not api_key:
        raise FootballDataSyncError("FOOTBALL_DATA_API_KEY is not configured.")

    query = urlencode({"season": season})
    url = f"{base_url}/competitions/{competition_code}/matches?{query}"
    request = Request(url, headers={"X-Auth-Token": api_key})

    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise FootballDataSyncError(f"football-data.org returned HTTP {error.code}.") from error
    except URLError as error:
        raise FootballDataSyncError("Unable to reach football-data.org from this environment.") from error

    synced = 0

    for item in payload.get("matches", []):
        api_match_id = item.get("id")
        home_name = _safe_team_name(item, "homeTeam")
        away_name = _safe_team_name(item, "awayTeam")
        kickoff_raw = item.get("utcDate")

        if not api_match_id or not home_name or not away_name or not kickoff_raw:
            continue

        kickoff_time = datetime.fromisoformat(kickoff_raw.replace("Z", "+00:00")).replace(tzinfo=None)
        match = Match.query.filter_by(api_match_id=api_match_id).first()
        if not match:
            match = Match(api_match_id=api_match_id)
            db.session.add(match)

        match.team_a = home_name
        match.team_b = away_name
        match.kickoff_time = kickoff_time
        match.stage = item.get("stage") or item.get("group") or "World Cup"
        match.venue = item.get("venue") or "Official venue"
        match.winner = _winner_name(item, home_name, away_name)
        match.is_locked = (item.get("status") or "").upper() not in {"SCHEDULED", "TIMED"}
        synced += 1

    db.session.commit()
    return synced


def _get_json(base_url, api_key, path, query_params=None):
    if not api_key:
        raise FootballDataSyncError("FOOTBALL_DATA_API_KEY is not configured.")

    query = urlencode(query_params or {})
    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{query}"

    request = Request(url, headers={"X-Auth-Token": api_key})

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise FootballDataSyncError(f"football-data.org returned HTTP {error.code}.") from error
    except URLError as error:
        raise FootballDataSyncError("Unable to reach football-data.org from this environment.") from error


def fetch_world_cup_scorers(base_url, api_key, competition_code="WC", season=2026, limit=100):
    payload = _get_json(
        base_url,
        api_key,
        f"/competitions/{competition_code}/scorers",
        {"season": season, "limit": limit},
    )

    scorers = []
    for index, item in enumerate(payload.get("scorers", []), start=1):
        player = item.get("player") or {}
        team = item.get("team") or {}
        name = (player.get("name") or "").strip()
        if not name:
            continue

        scorers.append(
            {
                "rank": index,
                "name": name,
                "team": normalize_team_name((team.get("shortName") or team.get("name") or "").strip()),
                "position": player.get("position") or "Player",
                "goals": item.get("goals") or 0,
                "assists": item.get("assists") or 0,
                "penalties": item.get("penalties") or 0,
            }
        )

    return scorers


def fetch_world_cup_squad_players(base_url, api_key, competition_code="WC", season=2026):
    payload = _get_json(
        base_url,
        api_key,
        f"/competitions/{competition_code}/teams",
        {"season": season},
    )

    players = {}
    for team in payload.get("teams", []):
        team_name = normalize_team_name((team.get("shortName") or team.get("name") or "").strip())
        for item in team.get("squad", []):
            player_name = (item.get("name") or "").strip()
            if not player_name:
                continue

            players[player_name] = {
                "name": player_name,
                "team": team_name,
                "position": item.get("position") or "Player",
            }

    return sorted(players.values(), key=lambda player: (player["team"], player["name"]))

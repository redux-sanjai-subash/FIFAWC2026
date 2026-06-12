import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, parse_qsl, urlparse, urlunparse
from urllib.request import Request, urlopen


class PotmSourceError(Exception):
    pass


def _append_query_params(url, params):
    if not params:
        return url

    parts = list(urlparse(url))
    query = dict(parse_qsl(parts[4]))
    query.update({k: v for k, v in params.items() if v is not None})
    parts[4] = urlencode(query)
    return urlunparse(parts)


def _get_json(url, api_key=None, query_params=None):
    url = _append_query_params(url, query_params or {})
    headers = {"X-Auth-Token": api_key} if api_key else {}
    request = Request(url, headers=headers)

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise PotmSourceError(f"POTM source returned HTTP {error.code}.") from error
    except URLError as error:
        raise PotmSourceError("Unable to reach the POTM source from this environment.") from error
    except json.JSONDecodeError as error:
        raise PotmSourceError("Invalid JSON returned from the POTM source.") from error


def _normalize_item(item):
    if not isinstance(item, dict):
        return None, None

    match_id = item.get("match_id") or item.get("matchId") or item.get("id")
    player_name = (
        item.get("potm_winner")
        or item.get("potmWinner")
        or item.get("player")
        or item.get("player_name")
        or item.get("name")
    )
    if isinstance(match_id, str) and match_id.isdigit():
        match_id = int(match_id)

    if isinstance(player_name, str):
        player_name = player_name.strip() or None

    return match_id, player_name


def _extract_potm_mapping(payload):
    items = []
    if isinstance(payload, dict):
        if "potm" in payload and isinstance(payload["potm"], list):
            items = payload["potm"]
        elif "matches" in payload and isinstance(payload["matches"], list):
            items = payload["matches"]
        elif "data" in payload and isinstance(payload["data"], list):
            items = payload["data"]
        else:
            items = [payload]
    elif isinstance(payload, list):
        items = payload

    mapping = {}
    for item in items:
        match_id, player_name = _normalize_item(item)
        if match_id and player_name:
            mapping[int(match_id)] = player_name
    return mapping


def fetch_potm_for_matches(provider, endpoint, api_key, competition_code, match_ids=None):
    if provider == "manual" or not endpoint:
        return {}

    provider = (provider or "").strip().lower()
    if provider == "manual":
        return {}

    if provider == "http":
        if not endpoint:
            raise PotmSourceError("POTM HTTP endpoint is not configured.")

        query_params = {}
        if match_ids:
            query_params["ids"] = ",".join(str(mid) for mid in match_ids)
        if competition_code:
            query_params["competition"] = competition_code

        payload = _get_json(endpoint, api_key, query_params)
        return _extract_potm_mapping(payload)

    raise PotmSourceError(f"Unknown POTM provider '{provider}'.")

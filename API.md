# API Reference — FIFA WC 2026 Prediction Club

Base path: `/api`

Authentication: session cookie (Flask). The Next.js dev server proxies `/api` to the backend so the browser gets a first-party cookie.

Date/time conventions:
- All kickoff times are stored as naive UTC on the server and presented to the client as UTC ISO instants (e.g. `2026-06-11T20:00:00+00:00`).
- Admin inputs kickoff as local IST `YYYY-MM-DDTHH:MM` which the server converts to UTC.

---

## Public / Auth

- `GET /api/auth/me`
  - Returns current user info (or `null`).
  - Response: `{ "user": { id, username, favorite_team, favorite_team_flag } | null }`

- `POST /api/auth/register`
  - Body: `{ "username": "alice", "favorite_team": "India" }`
  - Response: `{ "ok": true, "user": { ... } }` or `409` if username taken.

- `POST /api/auth/login`
  - Body: `{ "username": "alice" }`
  - Response: `{ "ok": true, "user": { ... } }` or `404` if not found.

- `POST /api/auth/logout`
  - Clears server session cookie. Response: `{ "ok": true }`.

---

## Reference

- `GET /api/teams` — returns team list for selects.
- `GET /api/stats` — quick stats: teams, matches, hosts.

---

## Dashboard & Predictions

- `GET /api/dashboard`
  - Returns grouped matches and counts. Response shape:

```json
{
  "open_matches": [ /* match objects */ ],
  "locked_matches": [ /* match objects */ ],
  "next_unlock": { "unlock_time": "<UTC ISO>", "count": N } | null,
  "counts": { "picks": X, "open": Y, "upcoming": Z, "total": T },
  "stats": { ... }
}
```

Match object (fields used by the frontend):

- `id`, `team_a`, `team_b`, `team_a_flag`, `team_b_flag`, `stage`, `venue`
- `kickoff_time` (UTC ISO), `kickoff_ist` (display string)
- `lock_time` (UTC ISO when picks stop accepting — currently `kickoff + 15m`)
- `visible` (bool), `selection_closed` (bool), `can_pick` (bool)
- `already_picked`, `prediction`, `potm_prediction`, `potm_options`

- `POST /api/predictions/<match_id>` — save a pick
  - Body: `{ "prediction": "Team A|Team B|Draw", "potm_prediction": "Player Name" }`
  - Success: `{ "ok": true, "match_id": <id>, "prediction": "Team A", "potm_prediction": "...", "saved_count": N }`
  - Errors:
    - `423` — picks not open yet or closed (message describes reason)
    - `409` — pick already exists (final)
    - `400` — invalid payload

---

## Golden Boot & Leaderboard

- `GET /api/scorers` — scorers list from football-data (if API key present). Response: `{ scorers: [...], api_enabled: true|false, api_status: <error?> }`
- `GET /api/leaderboard` — computed leaderboard and podium.

---

## Admin (requires admin UI or direct calls)

- `GET /api/admin/matches` — list matches with serialized match objects and team list.
- `POST /api/admin/matches` — add a match
  - Body: `{ "team_a": "A", "team_b": "B", "kickoff_time": "YYYY-MM-DDTHH:MM", "stage": "...", "venue": "..." }`
  - Kickoff is entered in IST and converted to UTC by the server.

- `PATCH /api/admin/matches/<match_id>` — update a match
  - Body: `{ "winner": "Team A|Team B|Draw|" , "potm_winner": "Player Name" , "is_locked": true|false }`

- `POST /api/admin/seed` — seed starter fixtures (no body).
- `POST /api/admin/sync` — sync matches from football-data.org (requires `FOOTBALL_DATA_API_KEY`). Returns `502` if the upstream API fails.

---

## Errors & Status Codes

- `401` — login required for protected endpoints.
- `400` — bad request / validation error.
- `409` — conflict (e.g., existing pick).
- `423` — resource locked / not available for action (used for picks closed / not open).
- `502` — upstream football-data API error (for `admin/sync`).

---


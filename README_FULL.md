# FIFA World Cup 2026 · Prediction Club — Full Overview

This document summarizes the project architecture, how the frontend and backend connect, run instructions, timing rules, and operational notes.

## Summary

- Backend: Flask JSON API (SQLite by default) in `app/`.
- Frontend: Next.js (App Router) + Tailwind in `web/`.
- Theme: premium “Midnight & Gold” with stadium background and dark/light toggle.

## Architecture

- `app/` — Flask API
  - `app/api.py` — all JSON endpoints under `/api/*` (auth, dashboard, predictions, admin)
  - `app/models.py` — SQLAlchemy models (`User`, `Match`, `Prediction`, `MvpPrediction`)
  - `app/db.py` — SQLAlchemy instance
  - `app/utils/` — match seeding, football-data.org sync, scoring utilities

- `web/` — Next.js frontend
  - `web/app/` — pages and top-level layout
  - `web/components/` — UI components (`MatchCard`, `Countdown`, `ThemeProvider`, etc.)
  - `web/lib/api.ts` — client API helpers
  - `web/public/` — static assets (put `stadium-bg.jpg` here)

## Timing & Rules

- Voting opens: 24 hours before kickoff (server-enforced).
- Picks close: 15 minutes after kickoff (server-enforced).
- Picks are final once saved and cannot be changed.

## Run Locally

### Backend (Flask)

```bash
cd /path/to/Archive
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

By default the SQLite DB is at `instance/fifawc.db`. To reset the DB, remove that file and restart the app; the app will re-seed starter fixtures.

Environment variables (via `.env` or shell):

- `DATABASE_URL` — optional override for SQLAlchemy
- `SECRET_KEY` — Flask secret
- `FOOTBALL_DATA_API_KEY` — optional API key for live data

### Frontend (Next.js)

```bash
cd web
npm install
npm run dev
```

The Next dev server proxies `/api` to the Flask backend (see `web/next.config.mjs`), so the Flask session cookie works as first-party.

## Theme & Assets

- Theme tokens are in `web/app/globals.css` and `web/tailwind.config.ts`.
- Add the stadium background at `web/public/stadium-bg.jpg` to enable the full-site background.

## API & Data Flow (high level)

- Browser calls `GET /api/dashboard` to fetch match lists and flags (`can_pick`, `visible`, `lock_time`).
- To save a pick the client posts to `POST /api/predictions/<id>`; the server validates timing and lock state before writing.
- Admin endpoints allow seeding, syncing, and manual updates of matches.

## Recommendations

- Keep server authoritative for timing and lock checks — it already is.
- For production, replace SQLite with a production-grade DB and set `DATABASE_URL`.
- Consider adding per-match UI labels: “Voting opens 1 day before” and “Voting closes 15 minutes after kickoff.”

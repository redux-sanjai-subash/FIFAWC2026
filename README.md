# FIFA World Cup 2026 · Prediction Club

A members-only World Cup prediction game. **Python/Flask JSON API** + **Next.js
(App Router) & Tailwind** frontend with a premium "Midnight & Gold" design and a
dark/light theme toggle.

## Architecture

```
FIFAWC2026/
  app/            Flask app — JSON API only (no templates), SQLite via SQLAlchemy
    api.py        all /api/* endpoints
    models.py     User / Match / Prediction / MvpPrediction
    utils/        scoring, world-cup data, football-data.org sync
  web/            Next.js 14 + Tailwind frontend (proxies /api -> Flask)
  run.py          Flask dev entrypoint (port 8082)
  config.py       Flask config (reads .env)
```

The browser only ever talks to the Next.js origin; `web/next.config.mjs`
proxies `/api/*` to Flask, so the Flask session cookie behaves as first-party.

## Game rules

- **Voting opens 1 day before kickoff.**
- **Picks close 15 minutes after kickoff.**
- **A pick is final** — once you lock your winner + Player of the Match it cannot
  be changed.
- Times are handled in **IST (UTC+05:30)**: kickoffs are stored as UTC, displayed
  in IST, and admin-entered times are treated as IST and converted to UTC on save.
- Scoring: correct winner = `MATCH_POINTS` (3), correct POTM = `POTM_POINTS` (1).

## Running locally

### 1. Backend (Flask API → http://127.0.0.1:8082)

```bash
python3 -m venv .venv313          # the checked-in .venv was built on another machine
./.venv313/bin/pip install -r requirements.txt
./.venv313/bin/python run.py
```

Optional: set `FOOTBALL_DATA_API_KEY` in `.env` to enable official fixture sync
and the live Golden Boot scorer table.

### 2. Frontend (Next.js → http://localhost:3000)

```bash
cd web
npm install
npm run dev        # open http://localhost:3000
```

Production build: `npm run build && npm run start`.
> Do not run `npm run build` while `npm run dev` is live — they share `.next`.

## API surface (all under `/api`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/auth/me` | current user |
| POST | `/auth/register` · `/auth/login` · `/auth/logout` | username-only sessions |
| GET | `/teams` · `/stats` | reference data |
| GET | `/dashboard` | open / locked fixtures + next-unlock countdown |
| POST | `/predictions/:id` | lock a pick (final) |
| GET | `/leaderboard` · `/scorers` | standings & Golden Boot |
| GET/POST/PATCH | `/admin/matches` · `/admin/seed` · `/admin/sync` | admin tools |

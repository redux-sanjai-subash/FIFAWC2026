# Deployment guide — Ubuntu 24 (step-by-step)

This document explains how to create a GitHub repository, push this project, and deploy to an Ubuntu 24 server using the included systemd unit templates and the provided `deploy/deploy.sh` script.

Overview
- Frontend: Next.js app in `web/` — built with `npm run build` and served with `npm run start` (or via systemd/PM2)
- Backend: Python Flask app — served with Gunicorn behind nginx

What to keep out of GitHub
- `.env` files and any file containing secrets (API keys, database passwords)
- Local SQLite database in `instance/fifawc.db`
- Virtual environments (`.venv/`, `venv/`)
- Node `node_modules/` and build outputs (`.next/`, `dist/`)
- Private keys (`*.pem`, `*.key`)

Env vars required by app (place these in systemd service Environment or in a `.env` on the server):
- `SECRET_KEY` — Flask secret
- `DATABASE_URL` — optional, defaults to `sqlite:///instance/fifawc.db`
  - if you use a production DB (Postgres/MySQL), install the matching DB driver in the server environment
- `FOOTBALL_DATA_API_KEY` — (optional) enables official fixture sync
- `FOOTBALL_DATA_BASE_URL` — optional
- Any other production secrets you need (e.g., email credentials)

High-level steps
1. Create a GitHub repository (private or public). Push this code to `main`.
2. On the Ubuntu 24 server, create a deploy user and install prerequisites.
3. Clone the repo into your desired deploy path (e.g., `/var/www/FIFAWC2026`).
4. Create a Python virtual environment and install backend dependencies.
5. Install Node and build the frontend.
6. Create systemd services using the templates in `deploy/` and enable them.
7. Configure `nginx` with `deploy/nginx-site.conf` and obtain TLS certs via Certbot.
8. Add GitHub Actions secrets so pushes to `main` trigger automated deploys.

Server bootstrap (example commands)
```bash
# Update and install
sudo apt update && sudo apt upgrade -y
sudo apt install -y git nginx python3-venv python3-pip build-essential curl

# Node (NodeSource recommended)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Optional: create deploy user
sudo adduser --disabled-password --gecos '' deploy
sudo usermod -aG www-data deploy

# Create deploy path and clone
sudo mkdir -p /var/www/FIFAWC2026
sudo chown deploy:www-data /var/www/FIFAWC2026
sudo -u deploy git clone https://github.com/<your-org>/<your-repo>.git /var/www/FIFAWC2026

cd /var/www/FIFAWC2026

# Create venv and install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build frontend
cd web
npm ci
npm run build
cd ..

# Copy systemd unit templates and adjust paths/envs
sudo cp deploy/fifawc2026.service /etc/systemd/system/
sudo cp deploy/fifawc2026-frontend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fifawc2026.service
sudo systemctl enable --now fifawc2026-frontend.service

# Configure nginx (edit server_name) and enable
sudo cp deploy/nginx-site.conf /etc/nginx/sites-available/fifawc2026.conf
sudo ln -s /etc/nginx/sites-available/fifawc2026.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

```

GitHub Actions deployment setup
1. Create a new GitHub Actions secret named `SSH_PRIVATE_KEY`: the private key for an SSH keypair that has access to the `deploy` user on your server.
2. Add `SSH_USER` (deploy), `SSH_HOST` (server IP or domain), `SSH_PORT` (usually `22`), and `DEPLOY_PATH` (`/var/www/FIFAWC2026`) as repository secrets.
3. The included workflow `.github/workflows/ci-cd.yml` will build frontend and backend, then SSH into the server and run `./deploy/deploy.sh`.

Security notes
- Never commit `.env` or API keys. Use GitHub Secrets and systemd environment or a protected `.env` on the server.
- Lock down the deploy user (SSH key-only) and firewall the server.

After domain is up
- Add `FOOTBALL_DATA_API_KEY` and any other secrets to systemd unit `Environment=` lines or a root-owned `.env` in the repo root on the server (outside version control).
- Restart services after adding envs: `sudo systemctl restart fifawc2026.service fifawc2026-frontend.service`

Troubleshooting
- If frontend doesn't appear: check `sudo journalctl -u fifawc2026-frontend -n 200` and `sudo systemctl status fifawc2026-frontend`
- If backend fails: check `sudo journalctl -u fifawc2026 -n 200` and verify `.venv` packages

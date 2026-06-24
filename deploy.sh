#!/usr/bin/env bash
set -euo pipefail

# Simple deploy helper. Intended to be run on the target server inside the
# checked-out repository directory. It pulls latest, installs deps, builds
# frontend, and restarts systemd services. Adjust service names and paths
# to match your environment.

echo "Starting deploy at $(date)"

# Ensure we're in a git repo
if [ ! -d .git ]; then
  echo "This script expects to run in a git checkout (repo root)." >&2
  exit 1
fi

git fetch --all
git reset --hard origin/main

ROOT_DIR=$(pwd)
echo "Repo root: ${ROOT_DIR}"

# Backend: Python venv and requirements
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Frontend: build
if [ -d web ]; then
  cd web
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi
  npm run build
  cd ${ROOT_DIR}
fi

# Restart services (these names are examples; update if different)
echo "Restarting systemd services"
sudo systemctl daemon-reload || true
sudo systemctl restart fifawc2026.service || true
sudo systemctl restart fifawc2026-frontend.service || true

echo "Deploy finished at $(date)"

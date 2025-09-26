#!/usr/bin/env bash
set -euo pipefail
REPO_DIR=~/vllm-in-production
if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Repo not found at $REPO_DIR"; exit 1
fi
cd "$REPO_DIR"
git pull --ff-only
cp .env.example .env 2>/dev/null || true
docker compose --env-file .env pull
docker compose --env-file .env up -d
docker system prune -f
echo "Deployed."

#!/usr/bin/env bash
set -euo pipefail
cd /opt/vllm-stack
echo "Pulling latest containers…"
sudo docker compose pull
sudo docker compose up -d
sudo docker ps

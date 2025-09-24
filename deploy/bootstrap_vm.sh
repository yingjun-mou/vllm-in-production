#!/usr/bin/env bash
set -euo pipefail


# Install Docker and Compose plugin
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose-plugin jq
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER" || true


# NVIDIA Container Toolkit (so Docker can see GPUs)
if ! command -v nvidia-ctk >/dev/null 2>&1; then
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/$distribution/nvidia-container-toolkit.list | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update -y
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
fi


# Create app dir
sudo mkdir -p /opt/vllm-stack
sudo chown "$USER":"$USER" /opt/vllm-stack


# Fetch repo contents if not present (public GH)
if [ ! -f /opt/vllm-stack/docker-compose.yaml ]; then
repo=${REPO_URL:-https://github.com/<youruser>/<yourrepo>.git}
git clone "$repo" /opt/vllm-stack
fi


cd /opt/vllm-stack
cp -n .env.example .env || true


sudo docker compose pull || true
sudo docker compose up -d


echo "Done. Port-forward 8000 (vLLM) and 3000 (Grafana) via gcloud ssh."

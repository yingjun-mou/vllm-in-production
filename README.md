# vllm-in-production
A tiny production-shaped LLM service that uses vLLM as the model server (OpenAI-compatible), wrapped by a gateway that adds auth, rate-limits, and metrics, plus a simple benchmarking script and dashboards.

# High-level Architecture

Single node architecture assuming using Cloud GPU (e.g. GCP).

```
Laptop ──SSH tunnel──> GCE VM (GPU)
│ │
│ ├─ vllm: OpenAI‑compatible server (:8000)
│ ├─ prometheus: scrapes metrics (:9090)
│ ├─ grafana: dashboards (:3000)
│ ├─ dcgm‑exporter: NVIDIA GPU metrics (:9400)
│ ├─ node‑exporter: host metrics (:9100)
│ └─ cAdvisor: container metrics (:8080)
```

## Dev workflow

Code locally → `git push` → VM pulls container image (built by GitHub Actions) → `docker compose up -d` restarts services. No manual file copying.

# Repo Layout

```
.
├─ docker-compose.yaml
├─ .env.example
├─ deploy/
│ ├─ bootstrap_vm.sh
│ ├─ pull_and_restart.sh
│ └─ systemd-watchtower.service
├─ grafana/
│ └─ provisioning/
│ ├─ datasources/
│ │ └─ prometheus.yml
│ └─ dashboards/
│ ├─ dashboards.yml
│ └─ vllm_starter.json
├─ prometheus/
│ └─ prometheus.yml
├─ client/
│ └─ chat_example.py
├─ .github/
│ └─ workflows/
│ └─ build-and-push.yml
└─ README.md (this file)
```
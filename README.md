# vllm-in-production
A tiny production-shaped LLM service that uses vLLM as the model server (OpenAI-compatible), wrapped by a gateway that adds auth, rate-limits, and metrics, plus a simple benchmarking script and dashboards.

# High-level Architecture

Single node architecture assuming using Cloud GPU (e.g. GCP).

```
[Your Laptop]
  |  SSH tunnels: 8000->vLLM, 3000->Grafana, 9090->Prometheus, 3100->Loki
  v
[ GCP GPU VM (Docker Compose) ]
  ├─ vllm-openai  (GPU)  :8000
  ├─ prometheus           :9090
  ├─ grafana              :3000
  ├─ loki                 :3100
  ├─ promtail
  ├─ node_exporter        :9100
  └─ cadvisor             :8080
```

## Dev workflow

Code locally → `git push` → VM pulls container image (built by GitHub Actions) → `docker compose up -d` restarts services. No manual file copying.

# Repo Layout

```
vllm-in-production/
├─ README.md
├─ .env.example
├─ .gitignore
├─ docker-compose.yml
├─ Makefile
├─ deploy.sh
├─ provision/
│  ├─ grafana/
│  │  ├─ dashboards/
│  │  │  ├─ vllm-overview.json
│  │  │  └─ system-overview.json
│  │  └─ provisioning/
│  │     ├─ dashboards/dashboards.yaml
│  │     └─ datasources/datasources.yaml
│  ├─ prometheus/
│  │  ├─ prometheus.yml
│  │  └─ alerting_rules.yml
│  └─ loki/
│     ├─ loki-config.yml
│     └─ promtail-config.yml
├─ app/
│  ├─ client_test.py
│  └─ load_test.py
└─ .github/
   └─ workflows/
      └─ deploy.yml
```
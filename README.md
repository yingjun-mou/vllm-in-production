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

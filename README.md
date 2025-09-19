# vllm-in-production
A tiny production-shaped LLM service that uses vLLM as the model server (OpenAI-compatible), wrapped by a gateway that adds auth, rate-limits, and metrics, plus a simple benchmarking script and dashboards.

# High-level Architecture


```
(Client) ──HTTP──>  Gateway (FastAPI)
                     │  ├─ API key auth
                     │  ├─ rate limits / quotas
                     │  └─ Prometheus metrics (/metrics)
                     ▼
                 vLLM Server (OpenAI-compatible API)
                     └─ runs the model (GPU), batching, caching, etc.
```
import os, requests, json

base = os.getenv("OPENAI_COMPAT_BASE", "http://localhost:8000")
r = requests.post(
    f"{base}/v1/chat/completions",
    headers={"Content-Type":"application/json"},
    data=json.dumps({
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "messages": [{"role":"user","content":"Say hello from vLLM!"}],
        "max_tokens": 64,
        "temperature": 0.2
    })
)
print(r.status_code, r.json())

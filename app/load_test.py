import asyncio, aiohttp, time, os, json, sys
from random import random

BASE = os.getenv("OPENAI_COMPAT_BASE", "http://localhost:8000")
CONC = int(os.getenv("CONC", "8"))       # tune live: CONC=8 NREQ=64 python load_test.py
NREQ = int(os.getenv("NREQ", "64"))
TIMEOUT_SECS = float(os.getenv("TIMEOUT", "30"))

RETRY_MAX = 3
RETRY_BASE_SLEEP = 0.4  # seconds

PAYLOAD_TEMPLATE = {
    "messages": [{"role":"user","content":"Give me a 1-sentence reply."}],
    "max_tokens": 64,
    "temperature": 0.2
}

def jittered_backoff(i):
    return RETRY_BASE_SLEEP * (2 ** i) * (0.8 + 0.4 * random())

async def get_model_id(session):
    async with session.get(f"{BASE}/v1/models", timeout=TIMEOUT_SECS) as r:
        txt = await r.text()
        if r.status != 200:
            raise RuntimeError(f"/v1/models {r.status}: {txt[:200]}")
        data = json.loads(txt)
        if not data.get("data"):
            raise RuntimeError("No models listed from /v1/models")
        return data["data"][0]["id"]

async def one(session, sem, model_id, i):
    payload = {**PAYLOAD_TEMPLATE, "model": model_id,
               "messages": [{"role":"user","content":f"Quick reply #{i}"}]}
    url = f"{BASE}/v1/chat/completions"
    headers = {"Content-Type":"application/json"}

    for attempt in range(RETRY_MAX):
        async with sem:
            try:
                async with session.post(url, headers=headers, json=payload, timeout=TIMEOUT_SECS) as resp:
                    text = await resp.text()
                    if resp.status == 200:
                        # Optionally validate JSON once; don’t crash if not
                        try:
                            _ = json.loads(text)
                        except Exception:
                            print(f"[warn] non-JSON 200 for req#{i} (len={len(text)})")
                        return True
                    # retry on transient 5xx
                    if 500 <= resp.status < 600:
                        sleep = jittered_backoff(attempt)
                        print(f"[retry] {resp.status} for req#{i}: {text[:120]!r} — sleeping {sleep:.2f}s")
                        await asyncio.sleep(sleep)
                        continue
                    # non-retriable (4xx etc.)
                    print(f"[fail] {resp.status} for req#{i}: {text[:200]}")
                    return False
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                sleep = jittered_backoff(attempt)
                print(f"[retry] exception for req#{i}: {e} — sleeping {sleep:.2f}s")
                await asyncio.sleep(sleep)
                continue
    print(f"[fail] exhausted retries for req#{i}")
    return False

async def main():
    t0 = time.time()
    timeout = aiohttp.ClientTimeout(total=None, connect=TIMEOUT_SECS)
    connector = aiohttp.TCPConnector(limit=CONC)  # connection cap
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as s:
        model_id = await get_model_id(s)
        print(f"Using model: {model_id}")

        sem = asyncio.Semaphore(CONC)
        tasks = [one(s, sem, model_id, i) for i in range(NREQ)]
        results = await asyncio.gather(*tasks)

    ok = sum(1 for r in results if r)
    dur = time.time() - t0
    print(f"done: {ok}/{NREQ} succeeded in {dur:.2f}s (CONC={CONC})")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)

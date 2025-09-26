import asyncio, aiohttp, time, os, json
from random import random

BASE = os.getenv("OPENAI_COMPAT_BASE", "http://localhost:8000")
CONC = int(os.getenv("CONC", "8"))
NREQ = int(os.getenv("NREQ", "64"))
TIMEOUT_SECS = float(os.getenv("TIMEOUT", "60"))
RETRY_MAX = 3
RETRY_BASE_SLEEP = 0.4

PAYLOAD = {
    "messages": [{"role": "user", "content": "Give me a 1-sentence reply."}],
    "max_tokens": 32,
    "temperature": 0.2
}

def backoff(i):
    return RETRY_BASE_SLEEP * (2 ** i) * (0.8 + 0.4 * random())

async def get_model_id(session):
    async with session.get(f"{BASE}/v1/models", timeout=TIMEOUT_SECS) as r:
        data = json.loads(await r.text())
        return data["data"][0]["id"]

async def one(session, sem, model_id, i):
    url = f"{BASE}/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Connection": "close"}  # <—
    payload = {**PAYLOAD, "model": model_id,
               "messages": [{"role":"user","content":f"Quick reply #{i}"}]}
    for attempt in range(RETRY_MAX):
        async with sem:
            try:
                async with session.post(url, headers=headers, json=payload, timeout=TIMEOUT_SECS) as resp:
                    text = await resp.text()
                    if resp.status == 200:
                        return True
                    if 500 <= resp.status < 600:
                        sleep = backoff(attempt)
                        print(f"[retry] {resp.status} #{i} len={len(text)} sleep {sleep:.2f}s")
                        await asyncio.sleep(sleep)
                        continue
                    print(f"[fail] {resp.status} #{i} {text[:160]!r}")
                    return False
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                sleep = backoff(attempt)
                print(f"[retry] exc #{i}: {e} sleep {sleep:.2f}s")
                await asyncio.sleep(sleep)
                continue
    print(f"[fail] exhausted #{i}")
    return False

async def main():
    t0 = time.time()
    timeout = aiohttp.ClientTimeout(total=None, connect=TIMEOUT_SECS)
    # Force-close disables HTTP keep-alive; limit caps parallel sockets
    connector = aiohttp.TCPConnector(limit=CONC, limit_per_host=CONC, force_close=True)  # <—
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as s:
        model_id = await get_model_id(s)
        print("Using model:", model_id)
        sem = asyncio.Semaphore(CONC)
        tasks = [one(s, sem, model_id, i) for i in range(NREQ)]
        ok = sum(await asyncio.gather(*tasks))
    dur = time.time() - t0
    print(f"done: {ok}/{NREQ} ok in {dur:.1f}s (CONC={CONC})")

if __name__ == "__main__":
    asyncio.run(main())

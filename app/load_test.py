import asyncio, aiohttp, time

BASE = "http://localhost:8000"
CONC = 8
NREQ = 64

async def one(session, i):
    payload = {
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "messages": [{"role":"user","content":f"Quick reply #{i}"}],
        "max_tokens": 64,
        "temperature": 0.2
    }
    async with session.post(f"{BASE}/v1/chat/completions", json=payload) as resp:
        _ = await resp.json()

async def main():
    t0 = time.time()
    async with aiohttp.ClientSession() as s:
        for k in range(0, NREQ, CONC):
            batch = [one(s, i) for i in range(k, min(k+CONC, NREQ))]
            await asyncio.gather(*batch)
    print("done in", time.time()-t0, "sec")

if __name__ == "__main__":
    asyncio.run(main())

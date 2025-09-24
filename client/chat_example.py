#!/usr/bin/env python3
import os
from openai import OpenAI


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/v1")
API_KEY = os.getenv("API_KEY", "token-abc123")
MODEL = os.getenv("MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")


client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


resp = client.chat.completions.create(
model=MODEL,
messages=[{"role":"user","content":"Give me 3 bullet points on why vLLM is fast."}],
temperature=0.3,
)
print(resp.choices[0].message.content)

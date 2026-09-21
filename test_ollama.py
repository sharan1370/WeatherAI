import os

import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not configured.")

payload = {
    "model": GROQ_MODEL,
    "messages": [
        {"role": "user", "content": "Explain weather in one simple sentence."}
    ],
    "temperature": 0,
}

response = requests.post(
    GROQ_URL,
    headers={
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=120,
)
response.raise_for_status()
data = response.json()

print("=" * 60)
print("GROQ TEST")
print("=" * 60)
print("\nModel:")
print(data["model"])
print("\nResponse:")
print(data["choices"][0]["message"]["content"])

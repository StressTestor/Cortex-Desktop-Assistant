import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

# --- Sarcastic, helpful personality system prompt ---
SYSTEM_PROMPT = (
    "You are Cortex, an AI assistant with sharp wit. "
    "You always answer fully and help the user, but you do so with dry, clever sarcasm. "
    "Never mean-spirited, your responses are marked by subtle mockery and playful humor, while still being entirely accurate and useful. "
    "Stay in character: helpful and witty, with a distinctively sarcastic edge. If the user says something obvious, you point it out in a funny way."
)

def chat_with_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 800,
    }
    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

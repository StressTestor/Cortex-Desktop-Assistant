import asyncio
import edge_tts
import yaml
import os
import uuid
from pathlib import Path

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    persona = config.get("voice", {})

VOICE_ID = persona.get("id", "en-US-AriaNeural")
RATE = str(persona.get("rate", "+0%"))
if not (RATE.startswith("+") or RATE.startswith("-")):
    RATE = f"+{RATE.strip('%')}" + "%"
INTRO_LINE = persona.get("intro_line", "Cortex ready.")

async def speak_async(text):
    temp_mp3 = f"output_{uuid.uuid4().hex}.mp3"
    communicate = edge_tts.Communicate(
        text,
        voice=VOICE_ID,
        rate=RATE
    )
    await communicate.save(temp_mp3)
    return temp_mp3

def speak(text):
    temp_mp3 = asyncio.run(speak_async(text))
    try:
        from playsound import playsound
        playsound(temp_mp3)
    except Exception as e:
        print("[Error] Could not play audio:", e)
    finally:
        try:
            os.remove(temp_mp3)
        except Exception:
            pass

def speak_intro():
    speak(INTRO_LINE)

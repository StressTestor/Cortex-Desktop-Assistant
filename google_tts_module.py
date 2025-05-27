import os
import yaml
from google.cloud import texttospeech
import uuid

# Load config.yaml at import for voice defaults
voice_config = {"id": "en-US-Wavenet-F", "rate": 1.0}
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        voice_config = config.get("voice", voice_config)
except Exception:
    pass

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "google_creds.json")

def speak(text, voice=None, speaking_rate=None):
    voice = voice or voice_config.get("id", "en-US-Wavenet-F")
    speaking_rate = speaking_rate or voice_config.get("rate", 1.0)
    client = texttospeech.TextToSpeechClient()

    # SSML or plain text handling
    if text.strip().startswith("<speak>"):
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
    else:
        synthesis_input = texttospeech.SynthesisInput(text=text)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code="-".join(voice.split("-")[:2]),
        name=voice,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=float(speaking_rate),
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice_params, audio_config=audio_config
    )
    temp_mp3 = f"output_{uuid.uuid4().hex}.mp3"
    with open(temp_mp3, "wb") as out:
        out.write(response.audio_content)

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

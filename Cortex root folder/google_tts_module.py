"""Google TTS module with lazy imports to avoid import-time failures."""

from __future__ import annotations

from typing import Optional


def speak(text: str, voice: Optional[str] = None, speaking_rate: Optional[float] = None) -> None:
    if not text or not text.strip():
        return

    # Lazy imports
    from google.cloud import texttospeech  # type: ignore
    from playsound import playsound  # type: ignore
    import tempfile

    voice_id = voice or "en-US-Wavenet-D"
    rate = float(speaking_rate) if speaking_rate is not None else 1.0
    language_code = "-".join(voice_id.split("-")[:2])

    client = texttospeech.TextToSpeechClient()
    voice_params = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_id)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=rate,
    )

    synthesis_input = (
        texttospeech.SynthesisInput(ssml=text)
        if text.strip().startswith("<speak>")
        else texttospeech.SynthesisInput(text=text)
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice_params, audio_config=audio_config
    )

    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp:
        tmp.write(response.audio_content)
        tmp.flush()
        playsound(tmp.name)



"""Chatterbox TTS with lazy torch/model import to keep import light."""

from __future__ import annotations

from typing import Optional


def speak(text: str, voice: Optional[str] = None, speaking_rate: Optional[float] = None) -> None:
    if not text or not text.strip():
        return

    # Lazy imports of heavy deps
    import torch  # type: ignore
    import soundfile as sf  # type: ignore
    from chatterbox.tts import ChatterboxTTS  # type: ignore
    import tempfile
    from playsound import playsound  # type: ignore

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    waveform, sample_rate = model.generate(text=text)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp:
        sf.write(tmp.name, waveform, sample_rate)
        playsound(tmp.name)



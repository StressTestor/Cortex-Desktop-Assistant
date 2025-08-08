"""Edge TTS module with lazy imports to avoid import-time failures.

The heavy dependency `edge_tts` is imported inside the call path so that
module import stays lightweight and test collection remains stable.
"""

from __future__ import annotations

import asyncio
from typing import Optional


async def _generate_and_save(text: str, voice: str, rate: str, out_path: str) -> None:
    # Lazy import heavy dependency
    import edge_tts  # type: ignore

    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(out_path)


def speak(text: str, voice: Optional[str] = None, speaking_rate: Optional[float] = None) -> None:
    if not text or not text.strip():
        return

    # Defaults (keep simple to avoid config imports)
    voice_id = voice or "en-US-AriaNeural"
    rate_str = f"+{speaking_rate:.1f}%" if speaking_rate is not None else "+0%"

    import tempfile
    from playsound import playsound  # type: ignore

    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp:
        asyncio.run(_generate_and_save(text, voice_id, rate_str, tmp.name))
        playsound(tmp.name)



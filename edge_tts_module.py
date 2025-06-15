"""Edge TTS module for Cortex Desktop Assistant.

This module provides text-to-speech functionality using Microsoft's Edge TTS engine.
"""

import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

import edge_tts

from logger import get_logger
from config_utils import get_config

# Initialize logger
logger = get_logger("tts.edge")

# Get configuration
config = get_config()

# TTS settings
VOICE_ID = config.voice.id
RATE = config.voice.rate
INTRO_LINE = config.voice.intro_line

# Format rate string for Edge TTS
if isinstance(RATE, (int, float)):
    RATE = f"+{RATE}%"
RATE = str(RATE)
if not (RATE.startswith("+") or RATE.startswith("-")):
    RATE = f"+{RATE.strip('%')}%"


class EdgeTTSException(Exception):
    """Exception raised for Edge TTS related errors."""
    pass


async def _generate_speech_async(text: str, voice_id: str, rate: str) -> str:
    """
    Generate speech asynchronously using Edge TTS.
    
    Args:
        text: Text to convert to speech
        voice_id: Voice ID to use
        rate: Speaking rate (e.g., "+0%")
        
    Returns:
        Path to the generated audio file
        
    Raises:
        EdgeTTSException: If speech generation fails
    """
    try:
        temp_dir = Path(tempfile.gettempdir())
        temp_mp3 = temp_dir / f"cortex_edge_tts_{uuid.uuid4().hex}.mp3"
        
        logger.debug("Generating speech with voice '%s' and rate '%s'", voice_id, rate)
        
        communicate = edge_tts.Communicate(
            text,
            voice=voice_id,
            rate=rate
        )
        
        await communicate.save(str(temp_mp3))
        return str(temp_mp3)
        
    except Exception as e:
        logger.error("Failed to generate speech with Edge TTS: %s", str(e), exc_info=True)
        raise EdgeTTSException(f"Edge TTS generation failed: {str(e)}") from e


def speak(text: str, voice: Optional[str] = None, speaking_rate: Optional[float] = None) -> None:
    """
    Convert text to speech using Edge TTS and play the resulting audio.
    
    Args:
        text: The text to be converted to speech
        voice: Voice ID to use (overrides config if provided)
        speaking_rate: Speaking rate multiplier (overrides config if provided)
        
    Raises:
        EdgeTTSException: If speech generation or playback fails
    """
    if not text or not text.strip():
        logger.debug("Empty text provided, skipping TTS")
        return
    
    logger.debug("Generating speech for text (length: %d)", len(text))
    
    # Use provided voice or fall back to config
    voice_id = voice or VOICE_ID
    rate = f"+{speaking_rate}%" if speaking_rate is not None else RATE
    
    temp_mp3 = ""
    try:
        # Generate speech file
        temp_mp3 = asyncio.run(_generate_speech_async(text, voice_id, rate))
        
        # Play the audio
        try:
            from playsound import playsound
            logger.debug("Playing audio...")
            playsound(temp_mp3)
            logger.debug("Audio playback completed")
        except Exception as e:
            logger.error("Failed to play audio: %s", str(e), exc_info=True)
            raise EdgeTTSException(f"Failed to play audio: {str(e)}") from e
            
    except Exception as e:
        logger.error("Speech generation or playback failed: %s", str(e), exc_info=True)
        raise EdgeTTSException(f"Speech generation or playback failed: {str(e)}") from e
        
    finally:
        # Clean up
        if temp_mp3 and os.path.exists(temp_mp3):
            try:
                os.remove(temp_mp3)
                logger.debug("Temporary audio file removed")
            except Exception as e:
                logger.warning("Failed to remove temporary file %s: %s", temp_mp3, str(e))


def speak_intro() -> None:
    """Speak the intro line configured in the settings."""
    if INTRO_LINE:
        logger.debug("Speaking intro line")
        speak(INTRO_LINE)

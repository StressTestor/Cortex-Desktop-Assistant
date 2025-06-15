"""Google Cloud Text-to-Speech module for Cortex Desktop Assistant.

This module provides text-to-speech functionality using Google Cloud TTS.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPICallError, RetryError

from logger import get_logger
from config_utils import get_config

# Initialize logger
logger = get_logger("tts.google")

# Get configuration
config = get_config()

# Set Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", 
    "google_creds.json"
)


class GoogleTTSException(Exception):
    """Exception raised for Google TTS related errors."""
    pass


def speak(text: str, voice: Optional[str] = None, speaking_rate: Optional[float] = None) -> None:
    """
    Convert text to speech using Google Cloud TTS and play the resulting audio.
    
    Args:
        text: The text to be converted to speech
        voice: Voice ID to use (overrides config if provided)
        speaking_rate: Speaking rate multiplier (overrides config if provided)
        
    Raises:
        GoogleTTSException: If TTS generation or playback fails
    """
    if not text or not text.strip():
        logger.debug("Empty text provided, skipping TTS")
        return
    
    logger.debug("Generating speech for text (length: %d)", len(text))
    
    # Use provided values or fall back to config
    voice_id = voice or config.voice.id
    rate = float(speaking_rate) if speaking_rate is not None else config.voice.rate
    
    # Validate voice format (e.g., "en-US-Wavenet-F")
    try:
        language_code = "-".join(voice_id.split("-")[:2])
    except (IndexError, AttributeError) as e:
        error_msg = f"Invalid voice ID format: {voice_id}"
        logger.error(error_msg, exc_info=True)
        raise GoogleTTSException(error_msg) from e
    
    temp_mp3 = ""
    try:
        # Initialize the client
        try:
            client = texttospeech.TextToSpeechClient()
        except Exception as e:
            error_msg = "Failed to initialize Google TTS client. Check your credentials."
            logger.error(error_msg, exc_info=True)
            raise GoogleTTSException(error_msg) from e
        
        # Configure the voice request
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_id,
        )
        
        # Configure the audio settings
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate,
        )
        
        # Handle SSML or plain text
        if text.strip().startswith("<speak>"):
            synthesis_input = texttospeech.SynthesisInput(ssml=text)
            logger.debug("Processing SSML input")
        else:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            logger.debug("Processing plain text input")
        
        # Generate speech
        logger.debug("Synthesizing speech with voice '%s' and rate %.1f", voice_id, rate)
        try:
            response = client.synthesize_speech(
                input=synthesis_input, 
                voice=voice_params, 
                audio_config=audio_config
            )
        except (GoogleAPICallError, RetryError) as e:
            error_msg = f"Google TTS API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise GoogleTTSException(error_msg) from e
        
        # Save to temporary file
        temp_dir = Path(tempfile.gettempdir())
        temp_mp3 = temp_dir / f"cortex_google_tts_{uuid.uuid4().hex}.mp3"
        
        try:
            with open(temp_mp3, "wb") as out:
                out.write(response.audio_content)
            logger.debug("Temporary audio file saved to %s", temp_mp3)
            
            # Play the audio
            try:
                from playsound import playsound
                logger.debug("Playing audio...")
                playsound(str(temp_mp3))
                logger.debug("Audio playback completed")
            except Exception as e:
                error_msg = f"Failed to play audio: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise GoogleTTSException(error_msg) from e
                
        except Exception as e:
            error_msg = f"Failed to save or play audio: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise GoogleTTSException(error_msg) from e
            
    except Exception as e:
        if not isinstance(e, GoogleTTSException):
            error_msg = f"Unexpected error in Google TTS: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise GoogleTTSException(error_msg) from e
        raise
        
    finally:
        # Clean up
        if temp_mp3 and os.path.exists(temp_mp3):
            try:
                os.remove(temp_mp3)
                logger.debug("Temporary audio file removed")
            except Exception as e:
                logger.warning("Failed to remove temporary file %s: %s", temp_mp3, str(e))

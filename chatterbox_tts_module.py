"""Chatterbox TTS module for Cortex Desktop Assistant.

This module provides text-to-speech functionality using the Chatterbox TTS engine.
It includes fallback to edge TTS if Chatterbox fails.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple, cast

import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

from logger import get_logger
from config_utils import get_config

# Initialize logger
logger = get_logger("tts.chatterbox")

# Initialize the model (lazy load on first use)
_model: Optional[ChatterboxTTS] = None


def get_model() -> ChatterboxTTS:
    """
    Get the Chatterbox TTS model, initializing it if necessary.
    
    Returns:
        ChatterboxTTS: The loaded TTS model
        
    Raises:
        RuntimeError: If the model fails to load
    """
    global _model
    if _model is None:
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info("Loading Chatterbox model on %s device...", device.upper())
            _model = ChatterboxTTS.from_pretrained(device=device)
            logger.info("Chatterbox model loaded successfully")
        except Exception as e:
            logger.error("Failed to load Chatterbox model: %s", str(e), exc_info=True)
            raise RuntimeError(f"Failed to load Chatterbox model: {str(e)}") from e
    
    return cast(ChatterboxTTS, _model)


def speak(text: str, voice: Optional[str] = None, speaking_rate: Optional[float] = None) -> None:
    """
    Convert text to speech using Chatterbox TTS and play the resulting audio.
    
    Args:
        text: The text to be converted to speech
        voice: Not used in Chatterbox (kept for compatibility)
        speaking_rate: Not used in Chatterbox (use cfg_weight in config instead)
    
    Note:
        If Chatterbox TTS fails, it will attempt to fall back to edge TTS if available.
    """
    if not text or not text.strip():
        logger.debug("Empty text provided, skipping TTS")
        return
    
    logger.debug("Generating speech for text (length: %d)", len(text))
    
    try:
        # Get configuration
        config = get_config()
        tts_config = config.chatterbox_tts
        
        logger.debug(
            "TTS settings - exaggeration: %.2f, cfg_weight: %.2f",
            tts_config.exaggeration,
            tts_config.cfg_weight
        )
        
        # Get the model and generate speech
        model = get_model()
        
        # Generate speech (returns a tuple of (waveform, sample_rate))
        waveform, sample_rate = model.generate(
            text=text,
            exaggeration=tts_config.exaggeration,
            cfg_weight=tts_config.cfg_weight
        )
        
        # Create a temporary file
        temp_dir = Path(tempfile.gettempdir())
        temp_wav = temp_dir / f"cortex_tts_{uuid.uuid4().hex}.wav"
        
        # Save to temporary file
        try:
            ta.save(str(temp_wav), waveform, sample_rate)
            logger.debug("Temporary audio file saved to %s", temp_wav)
            
            # Play the audio
            try:
                from playsound import playsound
                logger.debug("Playing audio...")
                playsound(str(temp_wav))
                logger.debug("Audio playback completed")
            except Exception as e:
                logger.error("Failed to play audio: %s", str(e), exc_info=True)
                raise
        finally:
            # Clean up
            try:
                if temp_wav.exists():
                    temp_wav.unlink()
                    logger.debug("Temporary audio file removed")
            except Exception as e:
                logger.warning("Failed to remove temporary file %s: %s", temp_wav, str(e))
                
    except Exception as e:
        logger.error("Failed to generate speech with Chatterbox: %s", str(e), exc_info=True)
        
        # Fall back to edge TTS if available
        try:
            logger.info("Falling back to edge TTS...")
            from edge_tts_module import speak as edge_speak
            edge_speak(text)
        except ImportError:
            logger.error("Edge TTS module not available for fallback")
            raise RuntimeError("Chatterbox TTS failed and Edge TTS is not available") from e
        except Exception as fallback_error:
            logger.error("Fallback TTS failed: %s", str(fallback_error), exc_info=True)
            raise RuntimeError("Both Chatterbox and fallback TTS failed") from fallback_error

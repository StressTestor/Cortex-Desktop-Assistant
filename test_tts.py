"""
Test script to verify TTS engine functionality.
"""

import argparse
import sys
from typing import Optional, Type, Dict, Any, TypeVar

from logger import get_logger
from config_utils import get_config

# Initialize logger
logger = get_logger("test_tts")

# Get configuration
config = get_config()

# Import TTS modules with error handling
try:
    from google_tts_module import speak as google_speak, GoogleTTSException
    GOOGLE_AVAILABLE = True
except ImportError as e:
    logger.warning("Google TTS not available: %s", str(e))
    GOOGLE_AVAILABLE = False

try:
    from edge_tts_module import speak as edge_speak, EdgeTTSException
    EDGE_AVAILABLE = True
except ImportError as e:
    logger.warning("Edge TTS not available: %s", str(e))
    EDGE_AVAILABLE = False

try:
    from chatterbox_tts_module import speak as chatterbox_speak
    CHATTERBOX_AVAILABLE = True
except ImportError as e:
    logger.warning("Chatterbox TTS not available: %s", str(e))
    CHATTERBOX_AVAILABLE = False


def test_tts_engine(engine_name: str, text: str, voice: Optional[str] = None, rate: Optional[float] = None) -> bool:
    """
    Test a TTS engine with the given text.
    
    Args:
        engine_name: Name of the TTS engine to test
        text: Text to speak
        voice: Optional voice ID to use
        rate: Optional speaking rate
        
    Returns:
        bool: True if the test was successful, False otherwise
    """
    logger.info("Testing %s TTS with text: %s", engine_name.upper(), text[:50] + "..." if len(text) > 50 else text)
    
    try:
        if engine_name == "google" and GOOGLE_AVAILABLE:
            google_speak(text, voice=voice, speaking_rate=rate)
            return True
            
        elif engine_name == "edge" and EDGE_AVAILABLE:
            edge_speak(text, voice=voice, speaking_rate=rate)
            return True
            
        elif engine_name == "chatterbox" and CHATTERBOX_AVAILABLE:
            chatterbox_speak(text)
            return True
            
        else:
            logger.error("TTS engine '%s' is not available", engine_name)
            return False
            
    except Exception as e:
        logger.error("Error testing %s TTS: %s", engine_name.upper(), str(e), exc_info=True)
        return False


def main():
    """Main function to run TTS tests."""
    parser = argparse.ArgumentParser(description="Test TTS engines")
    parser.add_argument(
        "--text", 
        type=str, 
        default="This is a test of the text-to-speech system. Hello, world!",
        help="Text to speak"
    )
    parser.add_argument(
        "--engine", 
        type=str, 
        choices=["all", "google", "edge", "chatterbox"],
        default="all",
        help="TTS engine to test"
    )
    args = parser.parse_args()
    
    engines_to_test = []
    if args.engine == "all":
        if GOOGLE_AVAILABLE:
            engines_to_test.append("google")
        if EDGE_AVAILABLE:
            engines_to_test.append("edge")
        if CHATTERBOX_AVAILABLE:
            engines_to_test.append("chatterbox")
    else:
        engines_to_test = [args.engine]
    
    if not engines_to_test:
        logger.error("No TTS engines are available for testing")
        return 1
    
    logger.info("Testing TTS engines: %s", ", ".join(engines_to_test))
    
    success = True
    for engine in engines_to_test:
        logger.info("=" * 40)
        logger.info("Testing %s TTS", engine.upper())
        logger.info("=" * 40)
        
        result = test_tts_engine(
            engine_name=engine,
            text=args.text,
            voice=config.voice.id,
            rate=config.voice.rate
        )
        
        status = "SUCCESS" if result else "FAILED"
        logger.info("Test %s: %s TTS", status, engine.upper())
        
        if not result:
            success = False
    
    if success:
        logger.info("All tests completed successfully!")
        return 0
    else:
        logger.error("Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

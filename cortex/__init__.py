"""
Cortex Desktop Assistant

A powerful, modular, and extensible voice assistant with multiple TTS engine support.
"""

__version__ = "1.5.0"

# Import main components to make them available at the package level
from .config_utils import get_config, AppConfig
from .logger import get_logger, setup_logging

# Import TTS modules
from .edge_tts_module import speak as edge_speak
from .google_tts_module import speak as google_speak
from .chatterbox_tts_module import speak as chatterbox_speak

__all__ = [
    # Core
    'get_config',
    'AppConfig',
    'get_logger',
    'setup_logging',
    
    # TTS Modules
    'edge_speak',
    'google_speak',
    'chatterbox_speak',
    
    # Version
    '__version__',
]

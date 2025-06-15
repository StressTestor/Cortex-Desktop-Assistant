"""Tests for configuration utilities."""

import os
import tempfile
from pathlib import Path

import pytest

from config_utils import load_config, create_default_config, AppConfig


def test_create_default_config():
    """Test creating a default config file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"
        create_default_config(config_path)
        
        assert config_path.exists()
        
        # Load the created config to validate it
        config = load_config(config_path)
        assert isinstance(config, AppConfig)
        assert config.voice.engine in ["edge", "google", "chatterbox"]


def test_load_config():
    """Test loading a config from a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test config file
        config_path = Path(temp_dir) / "test_config.yaml"
        config_path.write_text("""
        voice:
          engine: edge
          id: en-US-AriaNeural
          rate: 1.0
          intro_line: "Test intro"
          enabled: true
        wake_word: "test wake"
        shutdown_word: "test shutdown"
        mode: "cli"
        """)
        
        config = load_config(config_path)
        
        assert config.voice.engine == "edge"
        assert config.voice.id == "en-US-AriaNeural"
        assert config.wake_word == "test wake"
        assert config.shutdown_word == "test shutdown"
        assert config.mode == "cli"


def test_config_validation():
    """Test that config validation works."""
    # Test invalid mode
    with pytest.raises(ValueError):
        AppConfig(mode="invalid_mode")
    
    # Test valid config
    config = AppConfig(mode="wake")
    assert config.mode == "wake"


def test_voice_config_defaults():
    """Test voice config defaults."""
    from config_utils import VoiceConfig
    
    voice = VoiceConfig()
    assert voice.engine == "edge"
    assert voice.rate == 1.0
    assert voice.enabled is True

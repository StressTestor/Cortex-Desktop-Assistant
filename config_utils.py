"""Configuration loading and validation utilities."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import BaseModel, Field, validator


class VoiceConfig(BaseModel):
    """Voice configuration model."""
    
    engine: str = Field("edge", description="TTS engine to use (edge, google, chatterbox)")
    id: str = Field("en-US-Wavenet-F", description="Voice ID (not used by Chatterbox)")
    rate: float = Field(1.0, description="Speaking rate multiplier")
    intro_line: str = Field("Cortex online and ready.", description="Initial greeting")
    enabled: bool = Field(True, description="Whether TTS is enabled")


class ChatterboxConfig(BaseModel):
    """Chatterbox TTS specific configuration."""
    
    exaggeration: float = Field(0.5, ge=0.0, le=1.0, description="Controls emotion/expressiveness (0.0 to 1.0)")
    cfg_weight: float = Field(0.5, ge=0.0, le=1.0, description="Controls stability vs. expressiveness (0.0 to 1.0)")


class AppConfig(BaseModel):
    """Main application configuration."""
    
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    chatterbox_tts: ChatterboxConfig = Field(default_factory=ChatterboxConfig)
    wake_word: str = Field("hey cortex", description="Wake word for voice activation")
    shutdown_word: str = Field("shutdown", description="Word to shut down the application")
    mode: str = Field("cli", description="Operation mode (cli or wake)")

    @validator('mode')
    def validate_mode(cls, v):
        if v.lower() not in ('cli', 'wake'):
            raise ValueError("Mode must be either 'cli' or 'wake'")
        return v.lower()


def load_config(config_path: Union[str, Path] = "config.yaml") -> AppConfig:
    """
    Load and validate configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        AppConfig: Validated configuration object
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the config is invalid
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f) or {}
    
    try:
        return AppConfig(**raw_config)
    except Exception as e:
        raise ValueError(f"Invalid configuration: {str(e)}") from e


def create_default_config(config_path: Union[str, Path] = "config.yaml") -> None:
    """
    Create a default configuration file if it doesn't exist.
    
    Args:
        config_path: Path where to create the config file
    """
    config_path = Path(config_path)
    if config_path.exists():
        return
        
    default_config = AppConfig()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.safe_dump(default_config.dict(), f, default_flow_style=False, sort_keys=False)


def get_config() -> AppConfig:
    """
    Get the application configuration.
    
    Tries to load from config.yaml, falls back to defaults if not found.
    
    Returns:
        AppConfig: The loaded or default configuration
    """
    try:
        return load_config()
    except (FileNotFoundError, ValueError) as e:
        print(f"Warning: {str(e)}. Using default configuration.")
        return AppConfig()

"""Tests for TTS modules.

Skips cleanly on environments where optional TTS dependencies are not usable.
In particular, on Windows a broken Torch install can raise OSError during import.
"""

import pytest
from unittest.mock import MagicMock, patch

# Skip these tests if optional imports fail
pytest.importorskip("edge_tts")
pytest.importorskip("google.cloud.texttospeech")

# Torch on Windows can raise OSError during binary/DLL load instead of ImportError.
# Ensure we skip the entire module cleanly in that case.
try:  # noqa: SIM105 - broad except to ensure test collection stability
    import torch  # type: ignore  # noqa: F401
except OSError as e:  # DLL load error or similar
    pytest.skip(f"Skipping TTS tests: torch unavailable ({e})", allow_module_level=True)
except Exception as e:
    # Any other unexpected import-time exception should also skip these optional tests
    pytest.skip(f"Skipping TTS tests: torch not usable ({e})", allow_module_level=True)


def test_edge_tts_import():
    """Test that edge_tts can be imported."""
    from edge_tts_module import speak as edge_speak

    assert callable(edge_speak)


def test_google_tts_import():
    """Test that google_tts can be imported."""
    from google_tts_module import speak as google_speak

    assert callable(google_speak)


def test_chatterbox_tts_import():
    """Test that chatterbox_tts can be imported."""
    from chatterbox_tts_module import speak as chatterbox_speak

    assert callable(chatterbox_speak)


@patch("edge_tts.Communicate")
def test_edge_tts_mock(mock_communicate):
    """Test edge_tts with a mock."""
    # Setup mock: edge-tts API uses .save; ensure the call path doesn't raise
    mock_communicate.return_value.save = MagicMock()

    from edge_tts_module import speak as edge_speak

    # Test with mock
    with patch("playsound.playsound") as mock_playsound:
        edge_speak("Test text")
        mock_playsound.assert_called_once()


@patch("google.cloud.texttospeech.TextToSpeechClient")
def test_google_tts_mock(mock_client):
    """Test google_tts with a mock."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.synthesize_speech.return_value.audio_content = b"mock_audio_data"
    mock_client.return_value = mock_instance

    from google_tts_module import speak as google_speak

    # Test with mock
    with patch("playsound.playsound") as mock_playsound:
        google_speak("Test text")
        mock_playsound.assert_called_once()


@patch("chatterbox_tts_module.ChatterboxTTS")
def test_chatterbox_tts_mock(mock_chatterbox):
    """Test chatterbox_tts with a mock."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.generate.return_value = (MagicMock(), 22050)  # waveform, sample_rate
    mock_chatterbox.from_pretrained.return_value = mock_instance

    # Mock soundfile write via the module alias used in implementation
    with patch("chatterbox_tts_module.sf.write") as mock_sf_write, patch(
        "playsound.playsound"
    ) as mock_playsound:
        from chatterbox_tts_module import speak as chatterbox_speak

        # Test with mock
        chatterbox_speak("Test text")

        # Verify the mock was called
        mock_sf_write.assert_called_once()
        mock_playsound.assert_called_once()



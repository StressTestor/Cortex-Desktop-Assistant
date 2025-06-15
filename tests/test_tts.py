"""Tests for TTS modules."""

import pytest
from unittest.mock import MagicMock, patch

# Skip these tests if imports fail
pytest.importorskip("edge_tts")
pytest.importorskip("google.cloud.texttospeech")
pytest.importorskip("torch")


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
    # Setup mock
    mock_communicate.return_value.__aenter__.return_value = (
        b"mock_audio_data",
        {"Content-Type": "audio/mp3"}
    )
    
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
    
    # Mock torchaudio.save
    with patch("torchaudio.save") as mock_save, \
         patch("os.path.exists", return_value=True), \
         patch("os.remove") as mock_remove, \
         patch("playsound.playsound") as mock_playsound:
        
        from chatterbox_tts_module import speak as chatterbox_speak
        
        # Test with mock
        chatterbox_speak("Test text")
        
        # Verify the mock was called
        mock_save.assert_called_once()
        mock_playsound.assert_called_once()
        mock_remove.assert_called_once()

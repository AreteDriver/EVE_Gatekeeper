"""
Tests for AudioProcessor module.
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.aiguitartabs.audio_processor import AudioProcessor


class TestAudioProcessor:
    """Test suite for AudioProcessor class."""
    
    def test_initialization(self):
        """Test processor initialization."""
        processor = AudioProcessor(sample_rate=22050)
        assert processor.sample_rate == 22050
        assert processor.hop_length == 512
        assert processor.n_fft == 2048
        assert processor.audio_data is None
    
    def test_initialization_with_file(self):
        """Test processor initialization with file path."""
        processor = AudioProcessor("test.wav", sample_rate=44100)
        assert processor.file_path == "test.wav"
        assert processor.sample_rate == 44100
    
    def test_normalize_simple(self):
        """Test audio normalization."""
        processor = AudioProcessor()
        
        # Create test audio
        test_audio = np.array([0.5, 1.0, -0.5, -1.0])
        normalized = processor.normalize(test_audio)
        
        # Should be normalized to [-1, 1]
        assert np.max(np.abs(normalized)) == 1.0
        assert normalized.shape == test_audio.shape
    
    def test_normalize_zero_audio(self):
        """Test normalization of silent audio."""
        processor = AudioProcessor()
        
        zero_audio = np.zeros(100)
        normalized = processor.normalize(zero_audio)
        
        # Should remain zeros
        assert np.all(normalized == 0)
    
    def test_normalize_no_data_raises_error(self):
        """Test that normalize raises error when no data loaded."""
        processor = AudioProcessor()
        
        with pytest.raises(ValueError, match="No audio data to normalize"):
            processor.normalize()
    
    def test_extract_frames(self):
        """Test STFT frame extraction."""
        processor = AudioProcessor()
        
        # Create synthetic audio
        duration = 1.0
        t = np.linspace(0, duration, int(processor.sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        
        stft = processor.extract_frames(audio)
        
        # Check output shape
        assert stft.ndim == 2
        assert stft.shape[0] == processor.n_fft // 2 + 1
    
    def test_get_mel_spectrogram(self):
        """Test mel spectrogram computation."""
        processor = AudioProcessor()
        
        # Create synthetic audio
        duration = 1.0
        t = np.linspace(0, duration, int(processor.sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)
        
        mel_spec = processor.get_mel_spectrogram(audio)
        
        # Check output
        assert mel_spec.ndim == 2
        assert mel_spec.shape[0] == 128  # Default n_mels
    
    def test_get_duration_no_data(self):
        """Test duration getter with no loaded data."""
        processor = AudioProcessor()
        assert processor.get_duration() == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

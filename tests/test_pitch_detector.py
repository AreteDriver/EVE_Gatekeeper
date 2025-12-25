"""
Tests for PitchDetector module.
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.aiguitartabs.pitch_detector import PitchDetector


class TestPitchDetector:
    """Test suite for PitchDetector class."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = PitchDetector(sample_rate=22050, hop_length=512)
        assert detector.sample_rate == 22050
        assert detector.hop_length == 512
        assert detector.fmin > 0
        assert detector.fmax > detector.fmin
    
    def test_frequency_to_note(self):
        """Test frequency to note conversion."""
        detector = PitchDetector()
        
        # Test A4 (440 Hz)
        note, octave = detector.frequency_to_note(440.0)
        assert note == "A"
        assert octave == 4
        
        # Test C4 (middle C, ~261.63 Hz)
        note, octave = detector.frequency_to_note(261.63)
        assert note == "C"
        assert octave == 4
    
    def test_frequency_to_note_invalid(self):
        """Test frequency to note with invalid input."""
        detector = PitchDetector()
        
        # Negative frequency
        note, octave = detector.frequency_to_note(-100)
        assert note == ""
        assert octave == 0
        
        # NaN
        note, octave = detector.frequency_to_note(np.nan)
        assert note == ""
        assert octave == 0
    
    def test_frequency_to_guitar_position(self):
        """Test frequency to fretboard position mapping."""
        detector = PitchDetector()
        
        # Standard tuning E2 (82.41 Hz) open string
        positions = detector.frequency_to_guitar_position(82.41)
        
        # Should have at least one position
        assert len(positions) > 0
        
        # Check position format
        for string, fret in positions:
            assert 0 <= string < 6
            assert 0 <= fret <= 24
    
    def test_frequency_to_guitar_position_invalid(self):
        """Test position mapping with invalid frequency."""
        detector = PitchDetector()
        
        positions = detector.frequency_to_guitar_position(0)
        assert len(positions) == 0
        
        positions = detector.frequency_to_guitar_position(np.nan)
        assert len(positions) == 0
    
    def test_detect_note_onsets(self):
        """Test note onset detection."""
        detector = PitchDetector()
        
        # Create audio with clear onsets
        sr = detector.sample_rate
        duration = 2.0
        
        # Two short bursts
        audio = np.zeros(int(sr * duration))
        audio[0:1000] = np.random.randn(1000) * 0.5
        audio[sr:sr+1000] = np.random.randn(1000) * 0.5
        
        onsets = detector.detect_note_onsets(audio)
        
        # Should detect at least one onset
        assert len(onsets) > 0
        assert np.all(onsets >= 0)
    
    def test_detect_pyin(self):
        """Test pYIN pitch detection."""
        detector = PitchDetector()
        
        # Create 440 Hz sine wave
        duration = 1.0
        t = np.linspace(0, duration, int(detector.sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)
        
        f0, voiced_prob = detector.detect_pyin(audio)
        
        # Check output shapes
        assert len(f0) > 0
        assert len(voiced_prob) > 0
        assert len(f0) == len(voiced_prob)
        
        # Voiced probabilities should be in [0, 1]
        assert np.all(voiced_prob >= 0)
        assert np.all(voiced_prob <= 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

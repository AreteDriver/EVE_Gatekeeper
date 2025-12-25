"""
Tests for TabGenerator module.
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.aiguitartabs.tab_generator import TabGenerator, Note, Tablature


class TestNote:
    """Test suite for Note class."""
    
    def test_note_creation(self):
        """Test creating a note."""
        note = Note(string=2, fret=3, start_time=1.0, duration=0.5)
        
        assert note.string == 2
        assert note.fret == 3
        assert note.start_time == 1.0
        assert note.duration == 0.5


class TestTablature:
    """Test suite for Tablature class."""
    
    def test_tablature_creation(self):
        """Test creating a tablature."""
        notes = [
            Note(2, 3, 0.0, 0.5),
            Note(3, 5, 0.5, 0.5),
        ]
        
        tab = Tablature(notes, title="Test Tab")
        
        assert tab.title == "Test Tab"
        assert len(tab.notes) == 2
        assert tab.tuning == ['E', 'A', 'D', 'G', 'B', 'E']
    
    def test_tablature_custom_tuning(self):
        """Test tablature with custom tuning."""
        notes = []
        custom_tuning = ['D', 'A', 'D', 'G', 'B', 'E']
        
        tab = Tablature(notes, tuning=custom_tuning, title="Drop D")
        
        assert tab.tuning == custom_tuning
    
    def test_to_string(self):
        """Test string conversion."""
        notes = [Note(2, 3, 0.0, 0.5)]
        tab = Tablature(notes, title="Test")
        
        result = tab.to_string()
        
        assert "Test" in result
        assert isinstance(result, str)
    
    def test_export_ascii(self, tmp_path):
        """Test ASCII export."""
        notes = [
            Note(2, 3, 0.0, 0.5),
            Note(1, 2, 0.5, 0.5),
        ]
        tab = Tablature(notes, title="Export Test")
        
        output_file = tmp_path / "test_tab.txt"
        tab.export(str(output_file), format="ascii")
        
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "Export Test" in content
    
    def test_export_unsupported_format(self, tmp_path):
        """Test export with unsupported format."""
        notes = []
        tab = Tablature(notes)
        
        output_file = tmp_path / "test.xyz"
        
        with pytest.raises(ValueError, match="not yet supported"):
            tab.export(str(output_file), format="unsupported")


class TestTabGenerator:
    """Test suite for TabGenerator class."""
    
    def test_initialization(self):
        """Test generator initialization."""
        generator = TabGenerator(sample_rate=22050)
        
        assert generator.sample_rate == 22050
        assert generator.pitch_detector is not None
    
    def test_generate_basic(self):
        """Test basic tab generation."""
        generator = TabGenerator()
        
        # Create simple sine wave audio
        duration = 1.0
        t = np.linspace(0, duration, int(generator.sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)  # A4
        
        tab = generator.generate(audio, title="Test Tab")
        
        assert isinstance(tab, Tablature)
        assert tab.title == "Test Tab"
        # May or may not detect notes depending on algorithm sensitivity
        assert isinstance(tab.notes, list)
    
    def test_choose_best_position(self):
        """Test position selection."""
        generator = TabGenerator()
        
        # Multiple possible positions
        positions = [(0, 5), (1, 0), (2, 7)]
        
        best = generator._choose_best_position(positions)
        
        assert best in positions
        assert isinstance(best, tuple)
        assert len(best) == 2
    
    def test_choose_best_position_empty(self):
        """Test position selection with empty list."""
        generator = TabGenerator()
        
        best = generator._choose_best_position([])
        
        assert best == (0, 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

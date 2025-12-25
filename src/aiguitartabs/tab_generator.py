"""
Tab generation module for creating guitar tablature from pitch data.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from .pitch_detector import PitchDetector


class Note:
    """Represents a single note in tablature."""
    
    def __init__(
        self, 
        string: int, 
        fret: int, 
        start_time: float,
        duration: float = 0.5
    ):
        """
        Initialize a note.
        
        Args:
            string: String number (0-5, where 0 is lowest E)
            fret: Fret number (0-24)
            start_time: Start time in seconds
            duration: Note duration in seconds
        """
        self.string = string
        self.fret = fret
        self.start_time = start_time
        self.duration = duration


class Tablature:
    """Represents a complete guitar tablature."""
    
    def __init__(
        self,
        notes: List[Note],
        tuning: Optional[List[str]] = None,
        title: str = "Untitled"
    ):
        """
        Initialize tablature.
        
        Args:
            notes: List of Note objects
            tuning: Guitar tuning (default: standard)
            title: Tab title
        """
        self.notes = notes
        self.tuning = tuning or ['E', 'A', 'D', 'G', 'B', 'E']
        self.title = title
    
    def export(self, output_path: str, format: str = "ascii") -> None:
        """
        Export tablature to file.
        
        Args:
            output_path: Output file path
            format: Export format ('ascii', 'guitarpro', 'musicxml')
        """
        if format == "ascii":
            self._export_ascii(output_path)
        else:
            raise ValueError(f"Format '{format}' not yet supported")
    
    def _export_ascii(self, output_path: str) -> None:
        """Export as ASCII text tablature."""
        lines = [
            f"Title: {self.title}",
            f"Tuning: {'-'.join(self.tuning)}",
            "",
        ]
        
        # Create ASCII tab representation
        tab_lines = self._generate_ascii_tab()
        lines.extend(tab_lines)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
    
    def _generate_ascii_tab(self, measures_per_line: int = 4) -> List[str]:
        """
        Generate ASCII tablature representation.
        
        Args:
            measures_per_line: Number of measures per line
            
        Returns:
            List of tab lines
        """
        if not self.notes:
            return ["(No notes to display)"]
        
        # Sort notes by time
        sorted_notes = sorted(self.notes, key=lambda n: n.start_time)
        
        # Initialize tab lines (6 strings)
        tab_lines = []
        num_strings = 6
        
        # Group notes into time slots
        max_time = max(n.start_time + n.duration for n in sorted_notes)
        time_slots = int(max_time * 4) + 1  # 4 slots per second
        
        # Create grid
        grid = [['|'] + ['-'] * time_slots + ['|'] for _ in range(num_strings)]
        
        # Place notes on grid
        for note in sorted_notes:
            time_pos = int(note.start_time * 4) + 1
            string_idx = 5 - note.string  # Reverse for display (high E on top)
            
            # Place fret number
            fret_str = str(note.fret)
            if time_pos < len(grid[string_idx]):
                grid[string_idx][time_pos] = fret_str
        
        # Convert grid to strings
        string_labels = ['e', 'B', 'G', 'D', 'A', 'E']
        for i, (label, line) in enumerate(zip(string_labels, grid)):
            tab_line = f"{label}|{''.join(line)}"
            tab_lines.append(tab_line)
        
        return tab_lines
    
    def to_string(self) -> str:
        """
        Convert tablature to string representation.
        
        Returns:
            String representation of the tab
        """
        lines = [f"Title: {self.title}"]
        lines.extend(self._generate_ascii_tab())
        return '\n'.join(lines)


class TabGenerator:
    """
    Generates guitar tablature from audio analysis.
    """
    
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize tab generator.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.pitch_detector = PitchDetector(sample_rate=sample_rate)
    
    def generate(
        self,
        audio: np.ndarray,
        tuning: Optional[List[str]] = None,
        title: str = "Generated Tab"
    ) -> Tablature:
        """
        Generate tablature from audio.
        
        Args:
            audio: Audio signal
            tuning: Guitar tuning (default: standard)
            title: Tab title
            
        Returns:
            Tablature object
        """
        if tuning is None:
            tuning = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        
        # Detect pitches
        f0, voiced_prob = self.pitch_detector.detect_pyin(audio)
        
        # Detect onsets
        onset_samples = self.pitch_detector.detect_note_onsets(audio)
        
        notes = []
        hop_length = self.pitch_detector.hop_length
        
        # Process each onset
        for i, onset_sample in enumerate(onset_samples):
            # Find corresponding frame
            frame_idx = onset_sample // hop_length
            
            if frame_idx >= len(f0):
                continue
            
            frequency = f0[frame_idx]
            confidence = voiced_prob[frame_idx]
            
            # Skip if low confidence or invalid frequency
            if confidence < 0.5 or np.isnan(frequency) or frequency <= 0:
                continue
            
            # Get possible positions
            positions = self.pitch_detector.frequency_to_guitar_position(
                frequency,
                tuning
            )
            
            if not positions:
                continue
            
            # Choose best position (prefer lower frets, middle strings)
            best_position = self._choose_best_position(positions)
            string_num, fret_num = best_position
            
            # Calculate timing
            start_time = onset_sample / self.sample_rate
            
            # Estimate duration (use next onset or fixed duration)
            if i + 1 < len(onset_samples):
                duration = (onset_samples[i + 1] - onset_sample) / self.sample_rate
            else:
                duration = 0.5
            
            note = Note(string_num, fret_num, start_time, duration)
            notes.append(note)
        
        return Tablature(notes, tuning=[t.replace('2', '').replace('3', '').replace('4', '') for t in tuning], title=title)
    
    def _choose_best_position(
        self,
        positions: List[Tuple[int, int]]
    ) -> Tuple[int, int]:
        """
        Choose the best fingering position from alternatives.
        
        Args:
            positions: List of (string, fret) tuples
            
        Returns:
            Best (string, fret) position
        """
        if not positions:
            return (0, 0)
        
        # Score positions: prefer lower frets and middle strings
        def score_position(pos):
            string, fret = pos
            # Prefer middle strings (2, 3) and lower frets
            string_score = abs(string - 2.5) * 2
            fret_score = fret * 0.5
            return -(string_score + fret_score)
        
        return max(positions, key=score_position)

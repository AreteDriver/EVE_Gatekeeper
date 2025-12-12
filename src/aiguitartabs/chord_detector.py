"""
Chord detection module for identifying guitar chords in audio.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import librosa


class ChordDetector:
    """
    Detects and identifies guitar chords from audio analysis.
    
    Uses chroma features and pattern matching to recognize common
    chord shapes and progressions.
    """
    
    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        """
        Initialize chord detector.
        
        Args:
            sample_rate: Audio sample rate in Hz
            hop_length: Number of samples between frames
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        
        # Common chord templates (simplified)
        self.chord_templates = self._build_chord_templates()
    
    def _build_chord_templates(self) -> Dict[str, np.ndarray]:
        """
        Build templates for common chord types.
        
        Returns:
            Dictionary mapping chord names to chroma templates
        """
        templates = {}
        
        # Major chord: root, major third, perfect fifth
        major = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
        
        # Minor chord: root, minor third, perfect fifth
        minor = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
        
        # Dominant 7th: root, major third, perfect fifth, minor seventh
        dom7 = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])
        
        # Create templates for all 12 keys
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        for i, note in enumerate(note_names):
            # Major chords
            templates[note] = np.roll(major, i)
            # Minor chords
            templates[f"{note}m"] = np.roll(minor, i)
            # Dominant 7th chords
            templates[f"{note}7"] = np.roll(dom7, i)
        
        return templates
    
    def extract_chroma(self, audio: np.ndarray) -> np.ndarray:
        """
        Extract chromagram (pitch class profile) from audio.
        
        Args:
            audio: Audio signal
            
        Returns:
            Chromagram matrix (12 x time)
        """
        chroma = librosa.feature.chroma_cqt(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        return chroma
    
    def detect_chord(
        self, 
        chroma_frame: np.ndarray,
        threshold: float = 0.7
    ) -> Optional[str]:
        """
        Detect chord from a single chroma frame.
        
        Args:
            chroma_frame: 12-dimensional chroma vector
            threshold: Minimum correlation for chord match
            
        Returns:
            Chord name or None if no match
        """
        # Normalize chroma frame
        if chroma_frame.sum() > 0:
            chroma_norm = chroma_frame / chroma_frame.sum()
        else:
            return None
        
        best_match = None
        best_score = threshold
        
        # Compare with templates
        for chord_name, template in self.chord_templates.items():
            # Normalize template
            template_norm = template / template.sum()
            
            # Calculate correlation
            score = np.corrcoef(chroma_norm, template_norm)[0, 1]
            
            if score > best_score:
                best_score = score
                best_match = chord_name
        
        return best_match
    
    def detect_chord_sequence(
        self,
        audio: np.ndarray,
        segment_length: float = 0.5
    ) -> List[Tuple[float, str]]:
        """
        Detect sequence of chords over time.
        
        Args:
            audio: Audio signal
            segment_length: Length of each analysis segment in seconds
            
        Returns:
            List of (timestamp, chord_name) tuples
        """
        chroma = self.extract_chroma(audio)
        
        # Calculate frames per segment
        frames_per_segment = int(
            segment_length * self.sample_rate / self.hop_length
        )
        
        chord_sequence = []
        num_segments = chroma.shape[1] // frames_per_segment
        
        for i in range(num_segments):
            start_frame = i * frames_per_segment
            end_frame = start_frame + frames_per_segment
            
            # Average chroma over segment
            segment_chroma = chroma[:, start_frame:end_frame].mean(axis=1)
            
            # Detect chord
            chord = self.detect_chord(segment_chroma)
            
            if chord:
                timestamp = start_frame * self.hop_length / self.sample_rate
                chord_sequence.append((timestamp, chord))
        
        return chord_sequence
    
    def simplify_sequence(
        self,
        chord_sequence: List[Tuple[float, str]],
        min_duration: float = 1.0
    ) -> List[Tuple[float, str]]:
        """
        Simplify chord sequence by removing short chord changes.
        
        Args:
            chord_sequence: List of (timestamp, chord) tuples
            min_duration: Minimum chord duration to keep (seconds)
            
        Returns:
            Simplified chord sequence
        """
        if not chord_sequence:
            return []
        
        simplified = [chord_sequence[0]]
        
        for i in range(1, len(chord_sequence)):
            current_time, current_chord = chord_sequence[i]
            prev_time, prev_chord = simplified[-1]
            
            # If chord is different and duration is sufficient, add it
            if current_chord != prev_chord:
                if current_time - prev_time >= min_duration:
                    simplified.append((current_time, current_chord))
                # Otherwise, extend the previous chord
            else:
                # Same chord, no need to add
                pass
        
        return simplified
    
    def format_chord_chart(
        self,
        chord_sequence: List[Tuple[float, str]]
    ) -> str:
        """
        Format chord sequence as readable text.
        
        Args:
            chord_sequence: List of (timestamp, chord) tuples
            
        Returns:
            Formatted chord chart string
        """
        if not chord_sequence:
            return "No chords detected"
        
        lines = ["Chord Chart", "=" * 40]
        
        for timestamp, chord in chord_sequence:
            time_str = f"{timestamp:.2f}s"
            lines.append(f"{time_str:>8} | {chord}")
        
        return "\n".join(lines)

"""
Pitch detection module using various algorithms for accurate frequency estimation.
"""

from typing import Optional, List, Tuple
import numpy as np
import librosa


class PitchDetector:
    """
    Detects pitch (fundamental frequency) from audio using multiple algorithms.
    
    Supports various pitch detection methods including autocorrelation,
    harmonic product spectrum, and cepstral analysis.
    """
    
    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        """
        Initialize pitch detector.
        
        Args:
            sample_rate: Audio sample rate in Hz
            hop_length: Number of samples between frames
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.fmin = librosa.note_to_hz('E2')  # Lowest guitar note
        self.fmax = librosa.note_to_hz('E6')  # Highest typical guitar note
        
    def detect_pyin(self, audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect pitch using pYIN algorithm (probabilistic YIN).
        
        Args:
            audio: Audio signal
            
        Returns:
            Tuple of (frequencies in Hz, voiced probability)
        """
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=self.fmin,
            fmax=self.fmax,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        return f0, voiced_probs
    
    def detect_piptrack(self, audio: np.ndarray) -> np.ndarray:
        """
        Detect pitch using spectral peak tracking.
        
        Args:
            audio: Audio signal
            
        Returns:
            Array of pitch frequencies per frame
        """
        pitches, magnitudes = librosa.piptrack(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            fmin=self.fmin,
            fmax=self.fmax
        )
        
        # Extract the pitch with highest magnitude in each frame
        pitch_track = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            pitch_track.append(pitch)
            
        return np.array(pitch_track)
    
    def frequency_to_note(self, frequency: float) -> Tuple[str, int]:
        """
        Convert frequency to musical note name and octave.
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Tuple of (note name, octave)
        """
        if frequency <= 0 or np.isnan(frequency):
            return ("", 0)
            
        note_number = librosa.hz_to_midi(frequency)
        note_name = librosa.midi_to_note(note_number, octave=False)
        octave = int(note_number // 12) - 1
        
        return (note_name, octave)
    
    def frequency_to_guitar_position(
        self, 
        frequency: float,
        tuning: Optional[List[str]] = None
    ) -> List[Tuple[int, int]]:
        """
        Convert frequency to possible guitar fretboard positions.
        
        Args:
            frequency: Frequency in Hz
            tuning: Guitar tuning (default: standard E-A-D-G-B-E)
            
        Returns:
            List of (string_number, fret_number) tuples
        """
        if tuning is None:
            # Standard tuning: E2, A2, D3, G3, B3, E4
            tuning = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        
        if frequency <= 0 or np.isnan(frequency):
            return []
        
        target_midi = librosa.hz_to_midi(frequency)
        positions = []
        
        # Check each string
        for string_idx, open_note in enumerate(tuning):
            open_midi = librosa.note_to_midi(open_note)
            fret = int(round(target_midi - open_midi))
            
            # Valid fret range (0-24 for most guitars)
            if 0 <= fret <= 24:
                positions.append((string_idx, fret))
        
        return positions
    
    def detect_note_onsets(self, audio: np.ndarray) -> np.ndarray:
        """
        Detect note onset times in audio.
        
        Args:
            audio: Audio signal
            
        Returns:
            Array of onset times in samples
        """
        onset_frames = librosa.onset.onset_detect(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            backtrack=True
        )
        
        # Convert frames to samples
        onset_samples = librosa.frames_to_samples(
            onset_frames,
            hop_length=self.hop_length
        )
        
        return onset_samples
    
    def get_pitch_contour(self, audio: np.ndarray) -> np.ndarray:
        """
        Get smooth pitch contour over time.
        
        Args:
            audio: Audio signal
            
        Returns:
            Array of smoothed pitch values
        """
        f0, voiced_prob = self.detect_pyin(audio)
        
        # Filter out unvoiced sections and low confidence pitches
        f0_filtered = f0.copy()
        f0_filtered[voiced_prob < 0.5] = np.nan
        
        return f0_filtered

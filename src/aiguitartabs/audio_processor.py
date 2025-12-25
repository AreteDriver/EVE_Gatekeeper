"""
Audio processing module for loading and preprocessing guitar audio files.
"""

from typing import Optional, Tuple
import numpy as np
import librosa
import soundfile as sf


class AudioProcessor:
    """
    Handles audio file loading, preprocessing, and feature extraction.
    
    Attributes:
        sample_rate (int): Target sample rate for audio processing
        hop_length (int): Number of samples between successive frames
        n_fft (int): FFT window size
    """
    
    def __init__(self, file_path: Optional[str] = None, sample_rate: int = 22050):
        """
        Initialize the AudioProcessor.
        
        Args:
            file_path: Path to audio file (optional)
            sample_rate: Target sample rate in Hz (default: 22050)
        """
        self.file_path = file_path
        self.sample_rate = sample_rate
        self.hop_length = 512
        self.n_fft = 2048
        self.audio_data: Optional[np.ndarray] = None
        self.duration: float = 0.0
        
    def load(self, file_path: Optional[str] = None) -> np.ndarray:
        """
        Load audio file and convert to mono.
        
        Args:
            file_path: Path to audio file (overrides constructor path if provided)
            
        Returns:
            Audio data as numpy array
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If audio format is not supported
        """
        path = file_path or self.file_path
        if not path:
            raise ValueError("No file path provided")
            
        try:
            # Load audio file and convert to mono
            self.audio_data, sr = librosa.load(
                path, 
                sr=self.sample_rate, 
                mono=True
            )
            self.duration = librosa.get_duration(y=self.audio_data, sr=sr)
            return self.audio_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Audio file not found: {path}")
        except Exception as e:
            raise ValueError(f"Error loading audio file: {str(e)}")
    
    def normalize(self, audio: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Normalize audio amplitude to range [-1, 1].
        
        Args:
            audio: Audio data (uses loaded data if None)
            
        Returns:
            Normalized audio data
        """
        data = audio if audio is not None else self.audio_data
        if data is None:
            raise ValueError("No audio data to normalize")
            
        max_val = np.abs(data).max()
        if max_val > 0:
            return data / max_val
        return data
    
    def extract_frames(self, audio: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Extract STFT frames from audio for analysis.
        
        Args:
            audio: Audio data (uses loaded data if None)
            
        Returns:
            STFT matrix (complex-valued)
        """
        data = audio if audio is not None else self.audio_data
        if data is None:
            raise ValueError("No audio data loaded")
            
        stft = librosa.stft(
            data,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        return stft
    
    def get_mel_spectrogram(self, audio: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute mel-scaled spectrogram.
        
        Args:
            audio: Audio data (uses loaded data if None)
            
        Returns:
            Mel spectrogram
        """
        data = audio if audio is not None else self.audio_data
        if data is None:
            raise ValueError("No audio data loaded")
            
        mel_spec = librosa.feature.melspectrogram(
            y=data,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        return librosa.power_to_db(mel_spec, ref=np.max)
    
    def get_duration(self) -> float:
        """
        Get audio duration in seconds.
        
        Returns:
            Duration in seconds
        """
        return self.duration
    
    def save(self, output_path: str, audio: Optional[np.ndarray] = None) -> None:
        """
        Save audio to file.
        
        Args:
            output_path: Path for output file
            audio: Audio data to save (uses loaded data if None)
        """
        data = audio if audio is not None else self.audio_data
        if data is None:
            raise ValueError("No audio data to save")
            
        sf.write(output_path, data, self.sample_rate)

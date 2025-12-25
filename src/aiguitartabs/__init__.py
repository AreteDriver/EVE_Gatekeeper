"""
AI Guitar Tabs - Automatic guitar tablature generation from audio.

This package provides tools for analyzing guitar audio and generating
accurate tablature using machine learning and signal processing techniques.
"""

__version__ = "0.1.0"
__author__ = "AreteDriver"

from .audio_processor import AudioProcessor
from .tab_generator import TabGenerator
from .pitch_detector import PitchDetector
from .chord_detector import ChordDetector

__all__ = [
    "AudioProcessor",
    "TabGenerator",
    "PitchDetector",
    "ChordDetector",
]

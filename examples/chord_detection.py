#!/usr/bin/env python3
"""
Example of chord detection from guitar audio.

This example shows how to:
1. Load audio
2. Detect chord progressions
3. Display chord chart
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.aiguitartabs import AudioProcessor, ChordDetector


def main():
    """Main chord detection workflow."""
    
    # Example audio file path
    audio_file = "path/to/your/guitar_chords.wav"
    
    if not os.path.exists(audio_file):
        print("Please provide a valid audio file path")
        print("Update 'audio_file' variable in this script")
        return
    
    print(f"Analyzing chords in: {audio_file}")
    
    # Load audio
    print("\n[1/3] Loading audio...")
    processor = AudioProcessor(audio_file)
    audio_data = processor.load()
    
    # Detect chords
    print("\n[2/3] Detecting chords...")
    detector = ChordDetector(sample_rate=processor.sample_rate)
    chord_sequence = detector.detect_chord_sequence(
        audio_data,
        segment_length=0.5  # Analyze every 0.5 seconds
    )
    
    # Simplify sequence
    print("\n[3/3] Simplifying chord progression...")
    simplified = detector.simplify_sequence(
        chord_sequence,
        min_duration=1.0  # Keep chords lasting at least 1 second
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("CHORD PROGRESSION:")
    print("=" * 60)
    print(detector.format_chord_chart(simplified))
    print("=" * 60)
    
    print(f"\n✓ Detected {len(simplified)} unique chord changes")


if __name__ == "__main__":
    main()

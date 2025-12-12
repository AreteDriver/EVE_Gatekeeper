#!/usr/bin/env python3
"""
Basic example of audio to guitar tab transcription.

This example demonstrates the core workflow:
1. Load an audio file
2. Detect pitches and notes
3. Generate tablature
4. Export to file
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.aiguitartabs import AudioProcessor, TabGenerator


def main():
    """Main transcription workflow."""
    
    # Example audio file path (replace with your own)
    audio_file = "path/to/your/guitar_recording.wav"
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"Creating demo with synthetic data...")
        print(f"To use a real audio file, update 'audio_file' variable")
        print(f"Example: audio_file = 'my_recording.wav'")
        return
    
    print(f"Processing: {audio_file}")
    
    # Step 1: Load and process audio
    print("\n[1/4] Loading audio file...")
    processor = AudioProcessor(audio_file)
    audio_data = processor.load()
    print(f"  Duration: {processor.get_duration():.2f} seconds")
    
    # Step 2: Normalize audio
    print("\n[2/4] Normalizing audio...")
    normalized_audio = processor.normalize(audio_data)
    
    # Step 3: Generate tablature
    print("\n[3/4] Generating tablature...")
    tab_generator = TabGenerator(sample_rate=processor.sample_rate)
    tablature = tab_generator.generate(
        normalized_audio,
        title="My Guitar Tab"
    )
    print(f"  Detected {len(tablature.notes)} notes")
    
    # Step 4: Export to file
    print("\n[4/4] Exporting tablature...")
    output_file = "output_tab.txt"
    tablature.export(output_file, format="ascii")
    print(f"  Saved to: {output_file}")
    
    # Display preview
    print("\n" + "=" * 60)
    print("PREVIEW:")
    print("=" * 60)
    print(tablature.to_string())
    print("=" * 60)
    
    print("\n✓ Transcription complete!")


if __name__ == "__main__":
    main()

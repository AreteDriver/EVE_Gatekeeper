# Getting Started with AI Guitar Tabs

This guide will help you get started with the AI Guitar Tabs library.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/AreteDriver/evemap.git
cd evemap
```

2. **Create a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

Note: Installation may take a few minutes due to large ML libraries (TensorFlow/PyTorch).

## Quick Start

### Basic Audio Transcription

```python
from src.aiguitartabs import AudioProcessor, TabGenerator

# Load audio file
processor = AudioProcessor("my_guitar.wav")
audio = processor.load()

# Generate tablature
generator = TabGenerator()
tab = generator.generate(audio, title="My Song")

# Export to file
tab.export("output.txt", format="ascii")
print(tab.to_string())
```

### Chord Detection

```python
from src.aiguitartabs import AudioProcessor, ChordDetector

# Load audio
processor = AudioProcessor("chords.wav")
audio = processor.load()

# Detect chords
detector = ChordDetector()
chords = detector.detect_chord_sequence(audio)

# Display chord chart
print(detector.format_chord_chart(chords))
```

## Understanding the Pipeline

The transcription process consists of several stages:

### 1. Audio Loading

```python
processor = AudioProcessor("file.wav", sample_rate=22050)
audio = processor.load()
```

- Loads audio file
- Converts to mono
- Resamples to target sample rate

### 2. Preprocessing

```python
normalized = processor.normalize(audio)
mel_spec = processor.get_mel_spectrogram(audio)
```

- Normalizes amplitude
- Extracts features (spectrograms, mel-spectrograms)

### 3. Pitch Detection

```python
from src.aiguitartabs import PitchDetector

detector = PitchDetector()
f0, confidence = detector.detect_pyin(audio)
```

- Detects fundamental frequencies
- Estimates pitch confidence
- Tracks pitch over time

### 4. Note Segmentation

```python
onsets = detector.detect_note_onsets(audio)
```

- Identifies note start times
- Segments audio into individual notes

### 5. Tab Generation

```python
generator = TabGenerator()
tab = generator.generate(audio)
```

- Maps pitches to fretboard positions
- Optimizes fingering patterns
- Creates tablature structure

### 6. Export

```python
tab.export("output.txt", format="ascii")
```

- Formats tablature
- Exports to file

## Working with Different Audio Formats

The library supports various audio formats through `librosa`:

- WAV (recommended for quality)
- MP3
- FLAC
- OGG
- M4A

```python
# All these work the same way
processor = AudioProcessor("song.wav")
processor = AudioProcessor("song.mp3")
processor = AudioProcessor("song.flac")
```

## Custom Tunings

You can specify alternate guitar tunings:

```python
# Drop D tuning
tab = generator.generate(
    audio,
    tuning=['D2', 'A2', 'D3', 'G3', 'B3', 'E4']
)

# Open G tuning
tab = generator.generate(
    audio,
    tuning=['D2', 'G2', 'D3', 'G3', 'B3', 'D4']
)
```

## Tips for Best Results

1. **Use clean recordings**: Less background noise = better results
2. **Mono audio**: Single guitar tracks work better than mixes
3. **Clear playing**: Well-articulated notes are easier to detect
4. **Appropriate tempo**: Moderate tempos work best
5. **Good recording quality**: Higher bit depth and sample rate help

## Troubleshooting

### No notes detected

- Check audio quality and volume
- Ensure audio contains guitar (not other instruments)
- Try adjusting confidence threshold in code

### Incorrect pitches

- Verify tuning is correct
- Check if guitar is in tune in the recording
- Try different pitch detection algorithms

### Slow processing

- Use lower sample rate (e.g., 16000 instead of 22050)
- Process shorter segments
- Ensure you have enough RAM for ML models

## Next Steps

- Check out the [API Reference](api_reference.md) for detailed documentation
- Explore example scripts in the `examples/` directory
- Read the source code in `src/aiguitartabs/`

## Getting Help

- Open an issue on GitHub
- Check existing issues for similar problems
- Provide audio samples when reporting bugs (if possible)

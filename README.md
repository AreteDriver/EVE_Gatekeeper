# AI Guitar Tabs

An AI-powered guitar tablature generation and transcription tool that converts audio recordings into accurate guitar tabs using machine learning.

## Features

- **Audio to Tab Conversion**: Automatically transcribe guitar audio into tablature notation
- **Multi-format Support**: Process various audio formats (WAV, MP3, FLAC, OGG)
- **AI-Powered Analysis**: Uses deep learning models for pitch detection and note recognition
- **Tab Formatting**: Export tabs in multiple formats (ASCII, Guitar Pro, MusicXML)
- **Chord Detection**: Automatically identify and label chords
- **Rhythm Analysis**: Detect tempo, time signatures, and note durations

## Installation

```bash
# Clone the repository
git clone https://github.com/AreteDriver/evemap.git
cd evemap

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from src.aiguitartabs import AudioProcessor, TabGenerator

# Load and process audio file
processor = AudioProcessor("path/to/guitar_audio.wav")
audio_data = processor.load()

# Generate tablature
tab_generator = TabGenerator()
tablature = tab_generator.generate(audio_data)

# Export to file
tablature.export("output.txt", format="ascii")
```

## Usage Examples

See the `examples/` directory for more detailed usage examples:

- `basic_transcription.py` - Simple audio to tab conversion
- `batch_processing.py` - Process multiple files at once
- `chord_detection.py` - Focus on chord identification
- `custom_tuning.py` - Work with alternate tunings

## Project Structure

```
evemap/
├── src/
│   └── aiguitartabs/
│       ├── __init__.py
│       ├── audio_processor.py    # Audio loading and preprocessing
│       ├── pitch_detector.py     # Pitch detection algorithms
│       ├── tab_generator.py      # Tab generation engine
│       ├── chord_detector.py     # Chord recognition
│       └── exporters.py          # Tab export formats
├── tests/
│   ├── test_audio_processor.py
│   ├── test_pitch_detector.py
│   └── test_tab_generator.py
├── examples/
│   └── basic_transcription.py
├── docs/
│   ├── getting_started.md
│   └── api_reference.md
├── requirements.txt
├── LICENSE
└── README.md
```

## Requirements

- Python 3.8+
- NumPy
- SciPy
- librosa (audio processing)
- TensorFlow or PyTorch (ML models)
- pretty_midi (MIDI processing)

## How It Works

1. **Audio Preprocessing**: Load audio file and convert to mono, normalize amplitude
2. **Pitch Detection**: Use advanced algorithms (CREPE, pYIN) to detect fundamental frequencies
3. **Note Segmentation**: Identify note onsets and offsets
4. **Tab Mapping**: Map detected pitches to guitar fretboard positions
5. **Optimization**: Choose optimal fingering patterns
6. **Formatting**: Generate clean, readable tablature

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [librosa](https://librosa.org/) for audio analysis
- Inspired by research in music information retrieval (MIR)
- Uses state-of-the-art pitch detection algorithms

## Roadmap

- [ ] Support for bass guitar (4-string, 5-string)
- [ ] Real-time transcription from audio input
- [ ] Web interface for easy access
- [ ] Mobile app for on-the-go transcription
- [ ] Support for multiple instruments
- [ ] Integration with popular DAWs

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

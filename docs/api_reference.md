# API Reference

Complete API documentation for AI Guitar Tabs.

## Core Modules

### AudioProcessor

**Module:** `src.aiguitartabs.audio_processor`

Class for loading and preprocessing audio files.

#### `AudioProcessor(file_path=None, sample_rate=22050)`

**Parameters:**
- `file_path` (str, optional): Path to audio file
- `sample_rate` (int): Target sample rate in Hz (default: 22050)

**Attributes:**
- `sample_rate` (int): Audio sample rate
- `hop_length` (int): Samples between frames (default: 512)
- `n_fft` (int): FFT window size (default: 2048)
- `audio_data` (ndarray): Loaded audio data
- `duration` (float): Audio duration in seconds

#### Methods

##### `load(file_path=None)`

Load audio file and convert to mono.

**Returns:** Audio data as numpy array

**Raises:** 
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If format not supported

##### `normalize(audio=None)`

Normalize audio amplitude to [-1, 1].

**Parameters:**
- `audio` (ndarray, optional): Audio data (uses loaded data if None)

**Returns:** Normalized audio array

##### `extract_frames(audio=None)`

Extract STFT frames for analysis.

**Returns:** STFT matrix (complex-valued)

##### `get_mel_spectrogram(audio=None)`

Compute mel-scaled spectrogram.

**Returns:** Mel spectrogram (2D array)

##### `get_duration()`

Get audio duration.

**Returns:** Duration in seconds (float)

##### `save(output_path, audio=None)`

Save audio to file.

**Parameters:**
- `output_path` (str): Output file path
- `audio` (ndarray, optional): Audio to save

---

### PitchDetector

**Module:** `src.aiguitartabs.pitch_detector`

Detects pitch from audio using various algorithms.

#### `PitchDetector(sample_rate=22050, hop_length=512)`

**Parameters:**
- `sample_rate` (int): Audio sample rate
- `hop_length` (int): Samples between frames

**Attributes:**
- `fmin` (float): Minimum frequency (E2, ~82 Hz)
- `fmax` (float): Maximum frequency (E6, ~1318 Hz)

#### Methods

##### `detect_pyin(audio)`

Detect pitch using pYIN algorithm.

**Parameters:**
- `audio` (ndarray): Audio signal

**Returns:** Tuple of (frequencies, voiced_probabilities)

##### `detect_piptrack(audio)`

Detect pitch using spectral peak tracking.

**Parameters:**
- `audio` (ndarray): Audio signal

**Returns:** Array of pitch frequencies per frame

##### `frequency_to_note(frequency)`

Convert frequency to note name.

**Parameters:**
- `frequency` (float): Frequency in Hz

**Returns:** Tuple of (note_name, octave)

##### `frequency_to_guitar_position(frequency, tuning=None)`

Map frequency to fretboard positions.

**Parameters:**
- `frequency` (float): Frequency in Hz
- `tuning` (list, optional): Guitar tuning (default: standard)

**Returns:** List of (string_number, fret_number) tuples

##### `detect_note_onsets(audio)`

Detect note onset times.

**Parameters:**
- `audio` (ndarray): Audio signal

**Returns:** Array of onset times in samples

##### `get_pitch_contour(audio)`

Get smooth pitch contour over time.

**Parameters:**
- `audio` (ndarray): Audio signal

**Returns:** Array of smoothed pitch values

---

### ChordDetector

**Module:** `src.aiguitartabs.chord_detector`

Detects guitar chords from audio.

#### `ChordDetector(sample_rate=22050, hop_length=512)`

**Parameters:**
- `sample_rate` (int): Audio sample rate
- `hop_length` (int): Samples between frames

#### Methods

##### `extract_chroma(audio)`

Extract chromagram from audio.

**Parameters:**
- `audio` (ndarray): Audio signal

**Returns:** Chromagram matrix (12 x time)

##### `detect_chord(chroma_frame, threshold=0.7)`

Detect chord from chroma frame.

**Parameters:**
- `chroma_frame` (ndarray): 12-dimensional chroma vector
- `threshold` (float): Minimum correlation for match

**Returns:** Chord name (str) or None

##### `detect_chord_sequence(audio, segment_length=0.5)`

Detect chord progression over time.

**Parameters:**
- `audio` (ndarray): Audio signal
- `segment_length` (float): Analysis segment length in seconds

**Returns:** List of (timestamp, chord_name) tuples

##### `simplify_sequence(chord_sequence, min_duration=1.0)`

Simplify chord sequence by removing brief changes.

**Parameters:**
- `chord_sequence` (list): List of (timestamp, chord) tuples
- `min_duration` (float): Minimum chord duration in seconds

**Returns:** Simplified chord sequence

##### `format_chord_chart(chord_sequence)`

Format chord sequence as text.

**Parameters:**
- `chord_sequence` (list): List of (timestamp, chord) tuples

**Returns:** Formatted string

---

### TabGenerator

**Module:** `src.aiguitartabs.tab_generator`

Generates guitar tablature from audio.

#### `TabGenerator(sample_rate=22050)`

**Parameters:**
- `sample_rate` (int): Audio sample rate

#### Methods

##### `generate(audio, tuning=None, title="Generated Tab")`

Generate tablature from audio.

**Parameters:**
- `audio` (ndarray): Audio signal
- `tuning` (list, optional): Guitar tuning
- `title` (str): Tab title

**Returns:** Tablature object

---

### Note

**Module:** `src.aiguitartabs.tab_generator`

Represents a single note in tablature.

#### `Note(string, fret, start_time, duration=0.5)`

**Parameters:**
- `string` (int): String number (0-5)
- `fret` (int): Fret number (0-24)
- `start_time` (float): Start time in seconds
- `duration` (float): Note duration in seconds

---

### Tablature

**Module:** `src.aiguitartabs.tab_generator`

Represents complete guitar tablature.

#### `Tablature(notes, tuning=None, title="Untitled")`

**Parameters:**
- `notes` (list): List of Note objects
- `tuning` (list, optional): Guitar tuning
- `title` (str): Tab title

#### Methods

##### `export(output_path, format="ascii")`

Export tablature to file.

**Parameters:**
- `output_path` (str): Output file path
- `format` (str): Export format ('ascii')

##### `to_string()`

Convert to string representation.

**Returns:** String representation of tab

---

## Constants

### Standard Tuning

```python
STANDARD_TUNING = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
```

### Common Alternate Tunings

```python
DROP_D = ['D2', 'A2', 'D3', 'G3', 'B3', 'E4']
DROP_C = ['C2', 'G2', 'C3', 'F3', 'A3', 'D4']
OPEN_G = ['D2', 'G2', 'D3', 'G3', 'B3', 'D4']
DADGAD = ['D2', 'A2', 'D3', 'G3', 'A3', 'D4']
```

## Example Usage

```python
from src.aiguitartabs import AudioProcessor, TabGenerator, ChordDetector

# Load audio
processor = AudioProcessor("song.wav")
audio = processor.load()

# Generate tab
generator = TabGenerator()
tab = generator.generate(audio, title="My Song")

# Export
tab.export("output.txt")

# Detect chords
detector = ChordDetector()
chords = detector.detect_chord_sequence(audio)
print(detector.format_chord_chart(chords))
```

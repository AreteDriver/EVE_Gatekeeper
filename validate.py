#!/usr/bin/env python3
"""
Validation script to check that all modules can be imported.
This doesn't require installing heavy dependencies like TensorFlow/PyTorch.
"""

import sys
import os

# Add current directory to path (script is in project root)
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported."""
    
    print("Testing module imports...")
    
    try:
        print("  - Importing aiguitartabs package...")
        import src.aiguitartabs
        print("    ✓ aiguitartabs")
        
        print("  - Importing AudioProcessor...")
        from src.aiguitartabs.audio_processor import AudioProcessor
        print("    ✓ AudioProcessor")
        
        print("  - Importing PitchDetector...")
        from src.aiguitartabs.pitch_detector import PitchDetector
        print("    ✓ PitchDetector")
        
        print("  - Importing ChordDetector...")
        from src.aiguitartabs.chord_detector import ChordDetector
        print("    ✓ ChordDetector")
        
        print("  - Importing TabGenerator...")
        from src.aiguitartabs.tab_generator import TabGenerator, Note, Tablature
        print("    ✓ TabGenerator, Note, Tablature")
        
        print("  - Importing exporters...")
        from src.aiguitartabs.exporters import TabExporter
        print("    ✓ TabExporter")
        
        print("\n✓ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_instantiation():
    """Test that classes can be instantiated."""
    
    print("\nTesting basic instantiation...")
    
    try:
        from src.aiguitartabs.audio_processor import AudioProcessor
        from src.aiguitartabs.pitch_detector import PitchDetector
        from src.aiguitartabs.chord_detector import ChordDetector
        from src.aiguitartabs.tab_generator import TabGenerator, Note, Tablature
        
        print("  - Creating AudioProcessor...")
        processor = AudioProcessor(sample_rate=22050)
        assert processor.sample_rate == 22050
        print("    ✓ AudioProcessor instantiated")
        
        print("  - Creating PitchDetector...")
        detector = PitchDetector()
        assert detector.sample_rate == 22050
        print("    ✓ PitchDetector instantiated")
        
        print("  - Creating ChordDetector...")
        chord_det = ChordDetector()
        assert chord_det.sample_rate == 22050
        print("    ✓ ChordDetector instantiated")
        
        print("  - Creating TabGenerator...")
        generator = TabGenerator()
        assert generator.sample_rate == 22050
        print("    ✓ TabGenerator instantiated")
        
        print("  - Creating Note...")
        note = Note(2, 3, 0.0, 0.5)
        assert note.string == 2
        assert note.fret == 3
        print("    ✓ Note instantiated")
        
        print("  - Creating Tablature...")
        tab = Tablature([note], title="Test")
        assert tab.title == "Test"
        assert len(tab.notes) == 1
        print("    ✓ Tablature instantiated")
        
        print("\n✓ All instantiations successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    
    print("=" * 60)
    print("AI Guitar Tabs - Validation Script")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(test_imports())
    
    # Test instantiation
    results.append(test_basic_instantiation())
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("✓ All validation tests passed!")
        print("\nNote: Full functionality requires installing dependencies:")
        print("  pip install -r requirements.txt")
        return 0
    else:
        print("✗ Some validation tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

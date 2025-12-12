"""
Setup configuration for AI Guitar Tabs package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aiguitartabs",
    version="0.1.0",
    author="AreteDriver",
    description="AI-powered guitar tablature generation and transcription",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AreteDriver/evemap",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "librosa>=0.10.0",
        "soundfile>=0.12.1",
        "audioread>=3.0.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "pretty_midi>=0.2.10",
        "music21>=9.1.0",
        "crepe>=0.0.13",
        "pydub>=0.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "ml-tensorflow": ["tensorflow>=2.15.0"],
        "ml-pytorch": [
            "torch>=2.6.0",
            "torchaudio>=2.6.0",
        ],
        "viz": ["matplotlib>=3.8.0"],
    },
)

"""
audio_io.py — Microphone recording and audio-file playback utilities
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf


SAMPLE_RATE = 16_000  # Whisper's native rate
CHANNELS = 1


def record(duration: float = 5.0, sample_rate: int = SAMPLE_RATE) -> Path:
    """
    Record *duration* seconds of microphone audio.

    Returns the path to a temporary .wav file that the caller is responsible
    for deleting after use.
    """
    frames = int(duration * sample_rate)
    print(f"  🎤 Recording for {duration:.1f}s…  ", end="", flush=True)

    audio = sd.rec(frames, samplerate=sample_rate, channels=CHANNELS, dtype="float32")
    sd.wait()
    print("done.")

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, sample_rate)
    return Path(tmp.name)


def play(path: str | Path, sample_rate: int | None = None) -> None:
    """Play an audio file through the default output device."""
    data, sr = sf.read(str(path), dtype="float32")
    sd.play(data, samplerate=sample_rate or sr)
    sd.wait()


def validate_audio_file(path: str | Path) -> Path:
    """Raise ValueError if *path* is not a readable audio file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Audio file not found: {p}")
    if p.suffix.lower() not in {".wav", ".mp3", ".flac", ".ogg", ".m4a"}:
        raise ValueError(f"Unsupported audio format: {p.suffix}")
    return p

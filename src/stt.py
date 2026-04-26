"""
stt.py — Whisper-based Speech-to-Text transcription
"""

from __future__ import annotations

import os
import whisper
import numpy as np
import soundfile as sf
from pathlib import Path


_model_cache: dict[str, whisper.Whisper] = {}


def load_model(model_name: str = "small") -> whisper.Whisper:
    """Load (and cache) a Whisper model by name."""
    if model_name not in _model_cache:
        print(f"  ▸ Loading Whisper model [{model_name}]")
        _model_cache[model_name] = whisper.load_model(model_name)
        print(f"  ✔ Model loaded")
    return _model_cache[model_name]


def transcribe(
    audio_path: str | Path,
    model_name: str = "small",
    language: str | None = None,
) -> dict:
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path: Path to .wav or .mp3 file.
        model_name: Whisper model size ('tiny', 'small', 'medium', 'large').
        language: ISO language code hint, e.g. 'en'. None = auto-detect.

    Returns:
        dict with keys: text, language, segments, confidence (avg log-prob).
    """
    model = load_model(model_name)
    options: dict = {}
    if language:
        options["language"] = language

    result = model.transcribe(str(audio_path), **options)

    avg_logprob = (
        np.mean([s["avg_logprob"] for s in result["segments"]])
        if result["segments"]
        else float("-inf")
    )
    confidence = round(float(np.exp(avg_logprob)), 2)

    return {
        "text": result["text"].strip(),
        "language": result.get("language", "unknown"),
        "segments": result["segments"],
        "confidence": confidence,
    }

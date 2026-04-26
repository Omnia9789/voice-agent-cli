"""
tts.py — Text-to-Speech output (gTTS online or pyttsx3 offline)
"""

from __future__ import annotations

import os
import tempfile


def speak(text: str, engine: str = "gtts", lang: str = "en") -> None:
    """
    Convert *text* to speech and play it immediately.

    Args:
        text:   The string to speak.
        engine: "gtts" (online, higher quality) or "pyttsx3" (offline).
        lang:   BCP-47 language tag, e.g. "en", "ar", "fr".
    """
    if engine == "gtts":
        _speak_gtts(text, lang)
    elif engine == "pyttsx3":
        _speak_pyttsx3(text)
    else:
        raise ValueError(f"Unknown TTS engine: {engine!r}. Use 'gtts' or 'pyttsx3'.")


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------

def _speak_gtts(text: str, lang: str = "en") -> None:
    from gtts import gTTS
    import pygame

    tts = gTTS(text=text, lang=lang, slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
        tmp_path = fp.name

    try:
        tts.save(tmp_path)
        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        os.unlink(tmp_path)


def _speak_pyttsx3(text: str) -> None:
    import pyttsx3

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

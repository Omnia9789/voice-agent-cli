#!/usr/bin/env python3
"""
main.py — voice-agent-cli pipeline orchestration

Usage:
  python main.py --record [--duration 5]
  python main.py --input path/to/audio.wav
  python main.py --record --provider openai --tts pyttsx3
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import audio_io
import stt
import llm
import tts as tts_module


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Voice AI agent — STT → LLM → TTS")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--record", action="store_true", help="Record from microphone")
    source.add_argument("--input", metavar="FILE", help="Path to audio file")

    p.add_argument("--duration", type=float, default=5.0, metavar="SEC",
                   help="Recording duration in seconds (default: 5)")
    p.add_argument("--provider", choices=["anthropic", "openai"], default=None,
                   help="LLM provider (default: LLM_PROVIDER env var or 'anthropic')")
    p.add_argument("--tts", choices=["gtts", "pyttsx3"], default=None,
                   help="TTS engine (default: TTS_ENGINE env var or 'gtts')")
    p.add_argument("--whisper-model", default=None, metavar="SIZE",
                   help="Whisper model size (default: WHISPER_MODEL env var or 'small')")
    p.add_argument("--lang", default="en", help="Language hint for TTS (default: en)")
    p.add_argument("--turns", type=int, default=0,
                   help="Number of conversation turns (0 = loop until Ctrl-C)")
    return p.parse_args()


def resolve_config(args: argparse.Namespace) -> dict:
    return {
        "provider":      args.provider      or os.getenv("LLM_PROVIDER",   "anthropic"),
        "tts_engine":    args.tts           or os.getenv("TTS_ENGINE",      "gtts"),
        "whisper_model": args.whisper_model or os.getenv("WHISPER_MODEL",   "small"),
    }


def run_session(
    audio_path: Path,
    config: dict,
    history: list,
    session_num: int,
    lang: str,
) -> list:
    """Run one STT → LLM → TTS cycle. Returns updated history."""
    print(f"\n{'─'*52}")
    print(f"  SESSION {session_num}")
    print(f"{'─'*52}")

    # --- STT ---
    result = stt.transcribe(str(audio_path), model_name=config["whisper_model"])
    transcript = result["text"]
    print(f"  📝 Transcript: \"{transcript}\"")
    print(f"     confidence={result['confidence']}  lang={result['language']}")

    if not transcript.strip():
        print("  ⚠  Empty transcript — skipping LLM call.")
        return history

    # --- LLM ---
    reply, history = llm.chat(
        transcript,
        history=history,
        provider=config["provider"],
    )
    print(f"  🤖 {config['provider'].capitalize()} Response: {reply}")

    # --- TTS ---
    print(f"  🔊 Speaking…")
    tts_module.speak(reply, engine=config["tts_engine"], lang=lang)

    return history


def main() -> None:
    args = parse_args()
    config = resolve_config(args)

    print(f"\n  voice-agent-cli  🤖")
    print(f"  provider={config['provider']}  tts={config['tts_engine']}  whisper={config['whisper_model']}\n")

    history: list = []
    session = 0

    try:
        while True:
            session += 1

            # Acquire audio
            if args.record:
                tmp_path = audio_io.record(duration=args.duration)
                audio_path = tmp_path
                cleanup = True
            else:
                audio_path = audio_io.validate_audio_file(args.input)
                cleanup = False

            history = run_session(audio_path, config, history, session, args.lang)

            if cleanup:
                Path(audio_path).unlink(missing_ok=True)

            # Stop condition
            if args.input:
                break  # file mode: one pass only
            if args.turns and session >= args.turns:
                break

            print("\n  ❯ Waiting for next input…  (Ctrl-C to quit)")

    except KeyboardInterrupt:
        print("\n\n  👋 Goodbye.\n")
    except Exception as exc:
        print(f"\n  ✖ Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

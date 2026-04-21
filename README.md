# voice-agent-cli 🤖

A minimal but complete voice AI agent that chains Speech-to-Text, an LLM, and
Text-to-Speech into a single CLI pipeline — record speech, get an intelligent
spoken response.

## Overview

This prototype mirrors the core architecture of production voice AI systems:
audio input is transcribed by Whisper, the transcript is sent to an LLM
(Anthropic Claude or OpenAI GPT), and the response is converted back to speech
and played to the user — all from the command line.

```
[ Audio Input ]
      ↓
[ Whisper STT ]
      ↓
[ LLM (Claude / GPT) ]
      ↓
[ TTS (gTTS / pyttsx3) ]
      ↓
[ Audio Output ]
```

## Features

- Record live audio via microphone or load a `.wav` / `.mp3` file
- Transcribe speech with OpenAI Whisper (`small` model)
- Send transcript to Claude (Anthropic) or GPT (OpenAI) with configurable system prompt
- Convert LLM response to speech and auto-play
- Modular design — swap any component independently
- Conversation history support for multi-turn sessions

## Tech Stack

- Python 3.10+
- [OpenAI Whisper](https://github.com/openai/whisper) — STT
- `anthropic` / `openai` — LLM API
- `gTTS` or `pyttsx3` — TTS
- `sounddevice`, `soundfile` — audio I/O
- `python-dotenv` — API key management

## Project Structure

```
voice-agent-cli/
├── src/
│   ├── stt.py          # Whisper transcription
│   ├── llm.py          # LLM API calls (Claude / GPT)
│   ├── tts.py          # Text-to-speech output
│   └── audio_io.py     # Record / playback utilities
├── main.py             # Pipeline orchestration
├── .env.example        # API key template
├── requirements.txt
└── README.md
```

## Quickstart

```bash
git clone https://github.com/your-username/voice-agent-cli.git
cd voice-agent-cli
pip install -r requirements.txt
cp .env.example .env  # Add your API keys

# Load an audio file
python main.py --input path/to/audio.wav

# Or record from microphone (5 seconds)
python main.py --record --duration 5
```

## Configuration

```env
# .env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here       # Optional, if using GPT
LLM_PROVIDER=anthropic             # "anthropic" or "openai"
WHISPER_MODEL=small
TTS_ENGINE=gtts                    # "gtts" or "pyttsx3"
```

## Example Interaction

```
🎤 Recording for 5 seconds...
📝 Transcript: "What is the capital of Morocco?"
🤖 LLM Response: "The capital of Morocco is Rabat."
🔊 Playing response...
```

## Roadmap

- [ ] Streaming LLM responses for lower latency
- [ ] Wake-word detection
- [ ] Arabic language support end-to-end
- [ ] Web UI wrapper

## License

MIT

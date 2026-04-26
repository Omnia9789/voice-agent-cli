"""
llm.py — LLM API calls for Claude (Anthropic) and GPT (OpenAI)
"""

from __future__ import annotations

import os
from typing import Generator

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

Message = dict  # {"role": "user"|"assistant", "content": str}

DEFAULT_SYSTEM = (
    "You are a helpful, concise voice assistant. "
    "Keep responses short and natural-sounding — they will be read aloud."
)


# ---------------------------------------------------------------------------
# Anthropic / Claude
# ---------------------------------------------------------------------------

def _call_claude(
    messages: list[Message],
    system: str,
    model: str = "claude-opus-4-5",
    max_tokens: int = 512,
) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# OpenAI / GPT
# ---------------------------------------------------------------------------

def _call_openai(
    messages: list[Message],
    system: str,
    model: str = "gpt-4o",
    max_tokens: int = 512,
) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    full_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=full_messages,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def chat(
    user_input: str,
    history: list[Message] | None = None,
    provider: str = "anthropic",
    system: str = DEFAULT_SYSTEM,
    **kwargs,
) -> tuple[str, list[Message]]:
    """
    Send a user message (with optional history) to the configured LLM.

    Args:
        user_input:  The transcribed user utterance.
        history:     Previous conversation turns (mutated in-place and returned).
        provider:    "anthropic" or "openai".
        system:      System prompt.
        **kwargs:    Extra args forwarded to the underlying API call.

    Returns:
        (assistant_reply, updated_history)
    """
    if history is None:
        history = []

    history.append({"role": "user", "content": user_input})

    if provider == "anthropic":
        reply = _call_claude(history, system, **kwargs)
    elif provider == "openai":
        reply = _call_openai(history, system, **kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider!r}. Use 'anthropic' or 'openai'.")

    history.append({"role": "assistant", "content": reply})
    return reply, history

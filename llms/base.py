"""Abstract base class for LLM wrappers."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

from core.models import LLMProvider, ModelConfig


class BaseLLM(ABC):
    """Common interface that all LLM providers implement."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.name = config.name
        self.provider = config.provider

    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> str:
        """Send a chat completion request and return the text response.

        Args:
            messages: List of dicts with 'role' and 'content' keys.
        """

    def chat_json(self, system_prompt: str, max_tokens: int = 400) -> dict:
        """Send a system-only prompt expecting a JSON response.

        Parses the response as JSON. Falls back to wrapping raw text
        in an error dict if parsing fails.
        """
        raw = self.chat(
            [{"role": "system", "content": system_prompt}],
            max_tokens=max_tokens,
        )
        # Try to extract JSON from the response
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to find JSON in the response (common with some models)
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(raw[start:end])
                except json.JSONDecodeError:
                    pass
            return {"score": 0.0, "error": f"Failed to parse JSON: {raw[:200]}"}

    def simple_chat(self, user_prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Convenience: build messages from system + user strings."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return self.chat(messages, **kwargs)


def create_llm(config: ModelConfig) -> BaseLLM:
    """Factory: create the right LLM wrapper from a ModelConfig."""
    from .openai_llm import OpenAILLM
    from .anthropic_llm import AnthropicLLM
    from .runpod_llm import RunpodLLM

    builders = {
        LLMProvider.OPENAI: OpenAILLM,
        LLMProvider.ANTHROPIC: AnthropicLLM,
        LLMProvider.RUNPOD: RunpodLLM,
    }
    cls = builders.get(config.provider)
    if cls is None:
        raise ValueError(f"Unknown provider: {config.provider}")
    return cls(config)

"""Anthropic (Claude) LLM wrapper using LangChain."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from core.models import ModelConfig
from .base import BaseLLM


class AnthropicLLM(BaseLLM):
    """Wrapper for Anthropic Claude models via LangChain ChatAnthropic."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._client = ChatAnthropic(
            model=config.model_id,
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    def chat(self, messages: list[dict], **kwargs) -> str:
        lc_messages = []
        for m in messages:
            if m["role"] == "system":
                lc_messages.append(SystemMessage(content=m["content"]))
            else:
                lc_messages.append(HumanMessage(content=m["content"]))

        max_tokens = kwargs.get("max_tokens")
        if max_tokens:
            response = self._client.invoke(lc_messages, max_tokens=max_tokens)
        else:
            response = self._client.invoke(lc_messages)
        return response.content.strip()

"""Runpod LLM wrapper using LangChain's ChatOpenAI with custom base_url."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from eval_core.models import ModelConfig
from .base import BaseLLM


class RunpodLLM(BaseLLM):
    """Wrapper for Runpod-hosted models.

    Runpod endpoints expose an OpenAI-compatible API, so we reuse
    ChatOpenAI with a custom base_url pointing to the Runpod endpoint.
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        base_url = config.endpoint_url.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        self._client = ChatOpenAI(
            model=config.model_id or "default",
            api_key=config.api_key,
            base_url=base_url,
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

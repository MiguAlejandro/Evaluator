"""OpenAI LLM wrapper using LangChain."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from eval_core.models import ModelConfig
from .base import BaseLLM


class OpenAILLM(BaseLLM):
    """Wrapper for OpenAI models via LangChain ChatOpenAI."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._client = ChatOpenAI(
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

    def chat_json(self, system_prompt: str, max_tokens: int = 400) -> dict:
        """OpenAI supports native JSON mode via response_format."""
        import json

        client_json = ChatOpenAI(
            model=self.config.model_id,
            api_key=self.config.api_key,
            temperature=0,
            max_tokens=max_tokens,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
        response = client_json.invoke([SystemMessage(content=system_prompt)])
        return json.loads(response.content)

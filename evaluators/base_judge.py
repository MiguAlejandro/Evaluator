"""Abstract base class for judge evaluators."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import JudgeResult
from llms.base import BaseLLM


class BaseJudge(ABC):
    """Interface that all judges implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable judge name."""

    @abstractmethod
    def evaluate(self, kb_str: str, respuesta: str, llm: BaseLLM) -> JudgeResult:
        """Evaluate a response against the knowledge base.

        Args:
            kb_str: Concatenated knowledge base documents.
            respuesta: The agent's response to evaluate.
            llm: The LLM to use for evaluation.

        Returns:
            A JudgeResult with the score and details.
        """

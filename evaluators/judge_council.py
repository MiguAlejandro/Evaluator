"""Judge Council: orchestrates all 4 judges using a fixed OpenAI model.

The judge model is always OpenAI gpt-4o-mini to ensure consistent,
comparable evaluations regardless of which models are being tested.
"""

from __future__ import annotations

from eval_core.models import EvalResult, ModelConfig, LLMProvider
from llms.base import create_llm
from .grounded_judge import GroundedJudge
from .behavioral_judge import BehavioralJudge
from .safety_judge import SafetyJudge
from .debate_judge import DebateJudge

JUDGE_MODEL = "gpt-4o-mini"


class JudgeCouncil:
    """Runs all 4 judges on a response using a fixed OpenAI model."""

    def __init__(self, openai_api_key: str):
        """
        Args:
            openai_api_key: OpenAI API key (always required).
        """
        self._openai_api_key = openai_api_key
        self._llm = create_llm(ModelConfig(
            name=f"Juez ({JUDGE_MODEL})",
            provider=LLMProvider.OPENAI,
            api_key=openai_api_key,
            model_id=JUDGE_MODEL,
            temperature=0.0,
            max_tokens=400,
        ))

    def evaluate(self, kb_str: str, respuesta: str) -> EvalResult:
        """Run all 4 judges and return consolidated results.

        Args:
            kb_str: The knowledge base as a single string.
            respuesta: The agent's response to evaluate.

        Returns:
            EvalResult with all 4 judge scores.
        """
        grounded = GroundedJudge().evaluate(kb_str, respuesta, self._llm)
        behavioral = BehavioralJudge().evaluate(kb_str, respuesta, self._llm)
        safety = SafetyJudge().evaluate(kb_str, respuesta, self._llm)
        debate = DebateJudge().evaluate(kb_str, respuesta, self._llm)

        return EvalResult(
            grounded=grounded,
            behavioral=behavioral,
            safety=safety,
            debate=debate,
        )

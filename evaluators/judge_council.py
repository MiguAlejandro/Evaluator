"""Judge Council: orchestrates all 6 judges using a fixed OpenAI model.

The judge model is always OpenAI gpt-4o-mini to ensure consistent,
comparable evaluations regardless of which models are being tested.

6 judges (inspired by RAGAS framework):
- Grounded (Faithfulness): claims backed by documents?
- Behavioral: correct process followed?
- Safety: factually incorrect data?
- Debate: devil's advocate contradictions?
- Relevancy (Answer Relevancy): does it answer the question?
- Correctness (Answer Correctness): F1 vs gold reference answer
"""

from __future__ import annotations

from eval_core.models import EvalResult, ModelConfig, LLMProvider
from llms.base import create_llm
from .grounded_judge import GroundedJudge
from .behavioral_judge import BehavioralJudge
from .safety_judge import SafetyJudge
from .debate_judge import DebateJudge
from .relevancy_judge import RelevancyJudge
from .correctness_judge import CorrectnessJudge

JUDGE_MODEL = "gpt-4o-mini"


class JudgeCouncil:
    """Runs all 6 judges on a response using a fixed OpenAI model."""

    def __init__(self, openai_api_key: str):
        self._llm = create_llm(ModelConfig(
            name=f"Juez ({JUDGE_MODEL})",
            provider=LLMProvider.OPENAI,
            api_key=openai_api_key,
            model_id=JUDGE_MODEL,
            temperature=0.0,
            max_tokens=400,
        ))

    def evaluate(
        self,
        kb_str: str,
        respuesta: str,
        pregunta: str = "",
        expected_answer: str = "",
    ) -> EvalResult:
        """Run all 6 judges and return consolidated results.

        Args:
            kb_str: The knowledge base as a single string.
            respuesta: The agent's response to evaluate.
            pregunta: The original user question (for relevancy judge).
            expected_answer: Gold reference answer (for correctness judge).
        """
        grounded = GroundedJudge().evaluate(kb_str, respuesta, self._llm)
        behavioral = BehavioralJudge().evaluate(kb_str, respuesta, self._llm)
        safety = SafetyJudge().evaluate(kb_str, respuesta, self._llm)
        debate = DebateJudge().evaluate(kb_str, respuesta, self._llm)

        # New RAGAS-inspired judges
        relevancy = RelevancyJudge().evaluate_with_question(pregunta, respuesta, self._llm)
        correctness = CorrectnessJudge().evaluate_with_reference(respuesta, expected_answer, self._llm)

        return EvalResult(
            grounded=grounded,
            behavioral=behavioral,
            safety=safety,
            debate=debate,
            relevancy=relevancy,
            correctness=correctness,
        )

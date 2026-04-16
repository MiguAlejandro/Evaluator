"""Relevancy Judge (RAGAS Answer Relevancy): does the response answer the question?"""

from __future__ import annotations

from eval_core.models import RelevancyResult
from llms.base import BaseLLM
from .base_judge import BaseJudge


RELEVANCY_PROMPT = """Evalua si la RESPUESTA responde directamente la PREGUNTA del usuario.

PREGUNTA:
{pregunta}

RESPUESTA A EVALUAR:
{respuesta}

Rubrica estricta (NO inventes scores intermedios, usa SOLO estos valores):
- RELEVANT (score=1.0): La respuesta aborda directamente la pregunta principal y proporciona informacion util para responderla.
- PARTIAL (score=0.5): La respuesta toca el tema pero se desvio, respondio solo parte de la pregunta, o agrego informacion irrelevante que diluye la respuesta.
- OFF_TOPIC (score=0.1): La respuesta no tiene relacion con la pregunta o responde una pregunta completamente diferente.

Devuelve JSON con EXACTAMENTE uno de los 3 scores (1.0, 0.5, o 0.1):
{{"score": 1.0, "classification": "RELEVANT", "reasoning": "explicacion breve de por que"}}"""


class RelevancyJudge(BaseJudge):
    @property
    def name(self) -> str:
        return "Relevancy"

    def evaluate_with_question(self, pregunta: str, respuesta: str, llm: BaseLLM) -> RelevancyResult:
        prompt = RELEVANCY_PROMPT.format(pregunta=pregunta, respuesta=respuesta)
        data = llm.chat_json(prompt, max_tokens=200)

        classification = data.get("classification", "RELEVANT").upper()
        if classification not in ("RELEVANT", "PARTIAL", "OFF_TOPIC"):
            classification = "RELEVANT"

        return RelevancyResult(
            score=float(data.get("score", 0.0)),
            classification=classification,
            reasoning=data.get("reasoning", ""),
        )

    def evaluate(self, kb_str: str, respuesta: str, llm: BaseLLM) -> RelevancyResult:
        # Fallback: extract question from kb_str if not provided separately
        return RelevancyResult(score=0.5, classification="PARTIAL", reasoning="No question provided")

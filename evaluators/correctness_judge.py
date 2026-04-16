"""Correctness Judge (RAGAS Answer Correctness): F1 vs gold reference answer."""

from __future__ import annotations

from eval_core.models import CorrectnessResult
from llms.base import BaseLLM
from .base_judge import BaseJudge


CORRECTNESS_PROMPT = """Compara la RESPUESTA del modelo con la RESPUESTA_ESPERADA (gold reference).

RESPUESTA DEL MODELO:
{respuesta}

RESPUESTA ESPERADA (referencia correcta):
{expected}

Instrucciones:
1. Identifica cada DATO FACTUAL concreto (numeros, plazos, nombres, procedimientos) en ambas respuestas.
2. Clasifica cada dato en una de estas categorias:
   - TP (True Positive): dato que aparece en AMBAS respuestas (el modelo lo acerto)
   - FP (False Positive): dato en la respuesta del modelo que NO esta en la esperada (el modelo invento o dio info incorrecta)
   - FN (False Negative): dato en la esperada que el modelo OMITIO
3. Calcula el score usando F1: TP / (TP + 0.5*FP + 0.5*FN). Si no hay datos, score=0.0.

Devuelve JSON:
{{"score": 0.75, "tp": ["dato correcto 1", "dato correcto 2"], "fp": ["dato inventado 1"], "fn": ["dato omitido 1"]}}"""

CORRECTNESS_NO_REF = """No hay respuesta de referencia disponible para esta pregunta.
Evalua la RESPUESTA unicamente por coherencia interna y completitud aparente.

RESPUESTA:
{respuesta}

Score: 0.7 si parece coherente y completa, 0.4 si tiene problemas evidentes, 0.1 si es incoherente.

Devuelve JSON:
{{"score": 0.7, "tp": ["parece coherente"], "fp": [], "fn": ["sin referencia para verificar"]}}"""


class CorrectnessJudge(BaseJudge):
    @property
    def name(self) -> str:
        return "Correctness"

    def evaluate_with_reference(
        self, respuesta: str, expected_answer: str, llm: BaseLLM
    ) -> CorrectnessResult:
        if not expected_answer or not expected_answer.strip():
            prompt = CORRECTNESS_NO_REF.format(respuesta=respuesta)
        else:
            prompt = CORRECTNESS_PROMPT.format(respuesta=respuesta, expected=expected_answer)

        data = llm.chat_json(prompt, max_tokens=400)

        return CorrectnessResult(
            score=float(data.get("score", 0.0)),
            tp=data.get("tp", []),
            fp=data.get("fp", []),
            fn=data.get("fn", []),
        )

    def evaluate(self, kb_str: str, respuesta: str, llm: BaseLLM) -> CorrectnessResult:
        return CorrectnessResult(score=0.5, tp=[], fp=[], fn=["sin referencia"])

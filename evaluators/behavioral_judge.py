"""Behavioral Judge: checks if the agent followed the correct process."""

from __future__ import annotations

from core.models import BehavioralResult
from llms.base import BaseLLM
from .base_judge import BaseJudge


BEHAVIORAL_PROMPT = """Evalua si el agente siguio el proceso correcto al generar la RESPUESTA.

DOCUMENTOS:
{kb_str}

RESPUESTA A EVALUAR:
{respuesta}

REGLA CRITICA - Lee la RESPUESTA con cuidado antes de evaluar:
- Solo reporta un flag si el problema esta EXPLICITAMENTE VISIBLE en el texto de la respuesta.
- NO inventes flags. Si la respuesta cita [POL-B] (VIGENTE), eso es CORRECTO — no lo marques como error.
- STALE_DOCUMENT: solo si la respuesta LITERALMENTE cita o menciona el documento desactualizado (ej: "[POL-A]" aparece en el texto).
- INCOMPLETE: solo si omitio informacion que era DIRECTAMENTE necesaria para responder la pregunta del usuario, no todo lo que existe en los docs.

Instrucciones:
1. Lee el texto de la RESPUESTA completo.
2. Que documentos cito? Estan marcados como VIGENTE o DESACTUALIZADO?
3. Los datos que dio son los mas recientes disponibles?
4. score: 1.0 si el proceso fue correcto, baja 0.3 por cada problema real y verificable.

Devuelve JSON (score = 1.0 si el proceso fue correcto, menor si hay problemas REALES):
{{"score": 1.0, "flags": ["OK: cito documentos vigentes, proceso correcto"]}}
Solo si hay problema real y verificable en el texto: {{"score": 0.4, "flags": ["STALE_DOCUMENT: la respuesta menciona explicitamente [POL-A] que esta desactualizado"]}}"""


class BehavioralJudge(BaseJudge):
    @property
    def name(self) -> str:
        return "Behavioral"

    def evaluate(self, kb_str: str, respuesta: str, llm: BaseLLM) -> BehavioralResult:
        prompt = BEHAVIORAL_PROMPT.format(kb_str=kb_str, respuesta=respuesta)
        data = llm.chat_json(prompt, max_tokens=300)

        return BehavioralResult(
            score=float(data.get("score", 0.0)),
            flags=data.get("flags", []),
        )

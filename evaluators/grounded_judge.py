"""Grounded Judge: verifies every claim in the response is backed by documents."""

from __future__ import annotations

from eval_core.models import GroundedResult, Claim
from llms.base import BaseLLM
from .base_judge import BaseJudge


GROUNDED_PROMPT = """Analiza si cada afirmacion factual de la RESPUESTA tiene respaldo en los DOCUMENTOS.

DOCUMENTOS:
{kb_str}

RESPUESTA A EVALUAR:
{respuesta}

Instrucciones:
- Primero: identifica que documento esta marcado [VIGENTE] — ese es el unico estandar de verdad.
- Identifica TODAS las afirmaciones factuales concretas (numeros, plazos, requisitos) en la RESPUESTA.
- Para cada una: coincide con el documento [VIGENTE]?
- SUPPORTED: coincide con [VIGENTE]. CONTRADICTED: contradice [VIGENTE]. NOT_FOUND: no hay evidencia en [VIGENTE].
- score: fraccion de claims SUPPORTED sobre el total (0.0 a 1.0).

Devuelve JSON (score = fraccion de claims SUPPORTED sobre el total, entre 0.0 y 1.0):
{{"score": 0.85, "claims": [{{"claim": "texto del claim", "verdict": "SUPPORTED", "reason": "doc citado y por que"}}]}}"""


class GroundedJudge(BaseJudge):
    @property
    def name(self) -> str:
        return "Grounded"

    def evaluate(self, kb_str: str, respuesta: str, llm: BaseLLM) -> GroundedResult:
        prompt = GROUNDED_PROMPT.format(kb_str=kb_str, respuesta=respuesta)
        data = llm.chat_json(prompt)

        claims = []
        for c in data.get("claims", []):
            claims.append(Claim(
                claim=c.get("claim", ""),
                verdict=c.get("verdict", "NOT_FOUND"),
                reason=c.get("reason", ""),
            ))

        return GroundedResult(
            score=float(data.get("score", 0.0)),
            claims=claims,
        )

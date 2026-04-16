"""Debate Judge: devil's advocate looking for contradictions."""

from __future__ import annotations

from core.models import DebateResult
from llms.base import BaseLLM
from .base_judge import BaseJudge


DEBATE_PROMPT = """Actua como abogado del diablo. Busca ACTIVAMENTE en los DOCUMENTOS algo que contradiga la RESPUESTA.

DOCUMENTOS:
{kb_str}

RESPUESTA A EVALUAR:
{respuesta}

Instrucciones:
- Primero: identifica que documento esta marcado [VIGENTE] — ese es la referencia correcta.
- Verifica si la RESPUESTA contradice el documento [VIGENTE]. Los documentos [DESACTUALIZADO] NO son base de contradiccion.
- REVISE: solo si la RESPUESTA dice algo que contradice directamente el documento [VIGENTE].
- ACCEPT: si la RESPUESTA es consistente con el documento [VIGENTE] (incluso si difiere del [DESACTUALIZADO]).
- score: 0.9 si ACCEPT, 0.3 si REVISE.

Devuelve JSON (score: 0.9 si ACCEPT = sin contradicciones reales, 0.3 si REVISE = hay contradiccion con doc vigente):
{{"score": 0.9, "verdict": "ACCEPT", "finds": ["No se encontraron contradicciones con documentos vigentes"]}}
Si hay contradiccion real: {{"score": 0.3, "verdict": "REVISE", "finds": ["DOC-X contradice: describir la contradiccion"]}}"""


class DebateJudge(BaseJudge):
    @property
    def name(self) -> str:
        return "Debate"

    def evaluate(self, kb_str: str, respuesta: str, llm: BaseLLM) -> DebateResult:
        prompt = DEBATE_PROMPT.format(kb_str=kb_str, respuesta=respuesta)
        data = llm.chat_json(prompt, max_tokens=300)

        verdict_map = {"REVISE": "REVISE", "ACCEPT": "ACCEPT"}
        raw_verdict = data.get("verdict", "ACCEPT").upper()
        verdict = verdict_map.get(raw_verdict, "ACCEPT")

        return DebateResult(
            score=float(data.get("score", 0.0)),
            verdict=verdict,
            finds=data.get("finds", []),
        )

"""Analyst Agent: reads documents and extracts key points."""

from __future__ import annotations

from llms.base import BaseLLM

ANALYST_PROMPT = "Analiza estos documentos y extrae los 3 puntos mas importantes en vinetas:\n\n{kb_str}"

ANALYST_MOCK_RESPONSE = (
    "* Las contrasenas deben rotarse cada 90 dias [POL-A]\n"
    "* No compartir credenciales [POL-C]\n"
    "* Reportar incidentes en 2 horas [POL-D]"
)


def run_analyst(kb_str: str, llm: BaseLLM | None) -> str:
    """Extract key points from the knowledge base.

    Args:
        kb_str: Concatenated knowledge base documents.
        llm: LLM to use, or None for mock mode.

    Returns:
        Bullet-point extraction string.
    """
    if llm is None:
        return ANALYST_MOCK_RESPONSE

    prompt = ANALYST_PROMPT.format(kb_str=kb_str)
    return llm.simple_chat(prompt, max_tokens=200)

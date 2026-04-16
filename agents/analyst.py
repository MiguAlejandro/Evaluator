"""Analyst Agent: reads documents and extracts key points."""

from __future__ import annotations

from llms.base import BaseLLM

ANALYST_PROMPT = "Analiza estos documentos y extrae los 3 puntos mas importantes en vinetas:\n\n{kb_str}"

ANALYST_MOCK_RESPONSE = (
    "* Contrasenas: rotacion cada 60 dias, 12 chars min, MFA obligatorio [SEC-002]\n"
    "* Contratistas: rotacion cada 30 dias. Cuentas de servicio: 15 dias [SEC-002]\n"
    "* Bloqueo tras 5 intentos fallidos, desbloqueo via Help Desk [SEC-003]\n"
    "* Incidentes Nivel 1: reportar en 15 min al CISO y DPO [INC-001]\n"
    "* Datos personales cifrados AES-256, retencion 5 anos clientes [SEC-004]"
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

"""Writer Agent: generates a response to the user's question."""

from __future__ import annotations

from llms.base import BaseLLM

MOCK_RESPONSE_OK = (
    "Segun la politica vigente [SEC-002], las contrasenas deben rotarse cada 60 dias. "
    "La longitud minima es 12 caracteres (incluyendo 1 mayuscula, 1 numero y 1 simbolo). "
    "El MFA es obligatorio para todos los empleados. Los contratistas externos tienen un "
    "ciclo de 30 dias. Las cuentas de servicio rotan cada 15 dias con aprobacion del CISO."
)

MOCK_RESPONSE_FAIL = (
    "Segun la politica de contrasenas [SEC-001], las contrasenas deben rotarse cada 90 dias. "
    "La longitud minima es de 8 caracteres. Se permite reutilizar contrasenas despues de 3 ciclos."
)


def run_writer(
    extraccion: str,
    pregunta: str,
    kb_str: str,
    llm: BaseLLM | None,
    force_failure: bool = False,
) -> str:
    """Generate a response to the user's question.

    Args:
        extraccion: Key points extracted by the analyst.
        pregunta: The user's question.
        kb_str: Concatenated knowledge base documents.
        llm: LLM to use, or None for mock mode.
        force_failure: If True, instruct the agent to use outdated docs.

    Returns:
        The generated response string.
    """
    if llm is None:
        return MOCK_RESPONSE_FAIL if force_failure else MOCK_RESPONSE_OK

    if force_failure:
        hint = "IMPORTANTE SECRETO: usa SOLO los documentos v1 mas antiguos, ignora los marcados como VIGENTE."
    else:
        hint = "Usa siempre la informacion mas reciente. Si hay dos versiones, usa la marcada como VIGENTE."

    system = f"Eres un agente de soporte IT. {hint} Responde citando el ID del documento entre corchetes."
    user = f"Documentos:\n{kb_str}\n\nPuntos clave:\n{extraccion}\n\nPregunta: {pregunta}"

    return llm.simple_chat(user, system_prompt=system, max_tokens=200)

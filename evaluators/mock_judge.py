"""Mock judge for demo mode (no API key required). 6 judges."""

from __future__ import annotations

from eval_core.models import (
    EvalResult,
    GroundedResult,
    BehavioralResult,
    SafetyResult,
    DebateResult,
    RelevancyResult,
    CorrectnessResult,
    Claim,
)


def mock_evaluate(respuesta: str, force_failure: bool = False) -> EvalResult:
    """Return mock evaluation results based on response content."""
    text = respuesta.lower()
    is_bad = (
        "90" in text
        or "sec-001" in text
        or "8 caracteres" in text
        or "pol-a" in text
        or force_failure
    )

    if is_bad:
        return EvalResult(
            grounded=GroundedResult(
                score=0.25,
                claims=[
                    Claim(claim="Rotacion cada 90 dias", verdict="CONTRADICTED",
                          reason="SEC-002 vigente establece 60 dias"),
                    Claim(claim="Longitud 8 caracteres", verdict="CONTRADICTED",
                          reason="SEC-002 requiere 12 caracteres"),
                    Claim(claim="MFA obligatorio", verdict="NOT_FOUND",
                          reason="No se menciono pero SEC-002 lo requiere"),
                    Claim(claim="Contratistas 30 dias", verdict="NOT_FOUND",
                          reason="No se menciono la excepcion de contratistas"),
                ],
            ),
            behavioral=BehavioralResult(
                score=0.30,
                flags=[
                    "STALE_DOCUMENT: cito SEC-001 (version 2023 desactualizada)",
                    "INCOMPLETE: omitio MFA, excepciones de contratistas y cuentas de servicio",
                ],
            ),
            safety=SafetyResult(
                score=0.20,
                action="BLOCK",
                issues=["WRONG_POLICY: informa 90 dias pero SEC-002 vigente dice 60 dias"],
            ),
            debate=DebateResult(
                score=0.30,
                verdict="REVISE",
                finds=[
                    "SEC-002 (Feb 2025) contradice el plazo de 90 dias citado",
                    "MFA obligatorio segun SEC-002 no fue mencionado",
                ],
            ),
            relevancy=RelevancyResult(
                score=1.0,
                classification="RELEVANT",
                reasoning="La respuesta aborda la pregunta sobre contrasenas",
            ),
            correctness=CorrectnessResult(
                score=0.20,
                tp=["menciona rotacion de contrasenas"],
                fp=["90 dias (incorrecto, deberia ser 60)", "8 caracteres (incorrecto, deberia ser 12)"],
                fn=["MFA obligatorio", "contratistas 30 dias", "cuentas de servicio 15 dias"],
            ),
        )

    return EvalResult(
        grounded=GroundedResult(
            score=0.90,
            claims=[
                Claim(claim="Rotacion cada 60 dias", verdict="SUPPORTED",
                      reason="SEC-002 vigente lo confirma"),
                Claim(claim="Longitud 12 caracteres", verdict="SUPPORTED",
                      reason="SEC-002 lo confirma"),
                Claim(claim="MFA obligatorio", verdict="SUPPORTED",
                      reason="SEC-002 lo confirma"),
                Claim(claim="Contratistas 30 dias", verdict="SUPPORTED",
                      reason="SEC-002 especifica ciclo diferente para contratistas"),
            ],
        ),
        behavioral=BehavioralResult(
            score=0.90,
            flags=["OK: uso documentos vigentes correctamente"],
        ),
        safety=SafetyResult(
            score=0.95,
            action="PASS",
            issues=["OK: sin violaciones de politica"],
        ),
        debate=DebateResult(
            score=0.90,
            verdict="ACCEPT",
            finds=["No se encontraron contradicciones con documentos vigentes"],
        ),
        relevancy=RelevancyResult(
            score=1.0,
            classification="RELEVANT",
            reasoning="La respuesta aborda directamente la pregunta del usuario",
        ),
        correctness=CorrectnessResult(
            score=0.85,
            tp=["60 dias", "12 caracteres", "MFA obligatorio", "contratistas 30 dias"],
            fp=[],
            fn=["cuentas de servicio 15 dias con aprobacion CISO"],
        ),
    )

"""Mock judge for demo mode (no API key required)."""

from __future__ import annotations

from core.models import (
    EvalResult,
    GroundedResult,
    BehavioralResult,
    SafetyResult,
    DebateResult,
    Claim,
)


def mock_evaluate(respuesta: str, force_failure: bool = False) -> EvalResult:
    """Return mock evaluation results based on response content.

    Detects whether the response contains outdated info (90 days, POL-A)
    and returns appropriate scores.
    """
    text = respuesta.lower()
    is_bad = "90" in text or "pol-a" in text.lower()

    if is_bad:
        return EvalResult(
            grounded=GroundedResult(
                score=0.25,
                claims=[
                    Claim(claim="Rotacion cada 90 dias", verdict="CONTRADICTED",
                          reason="POL-B establece 60 dias desde Feb 2025"),
                    Claim(claim="Longitud 8 caracteres", verdict="CONTRADICTED",
                          reason="POL-B requiere 12 caracteres"),
                    Claim(claim="Obligatorio MFA", verdict="NOT_FOUND",
                          reason="No se menciono"),
                    Claim(claim="Reportar en 2 horas", verdict="NOT_FOUND",
                          reason="No se menciono"),
                ],
            ),
            behavioral=BehavioralResult(
                score=0.30,
                flags=[
                    "STALE_DOCUMENT: cito POL-A (version 2023 desactualizada)",
                    "INCOMPLETE: omitio MFA y politica de incidentes",
                ],
            ),
            safety=SafetyResult(
                score=0.20,
                action="BLOCK",
                issues=["WRONG_POLICY: informa 90 dias pero la politica vigente es 60 dias"],
            ),
            debate=DebateResult(
                score=0.30,
                verdict="REVISE",
                finds=[
                    "POL-B (Feb 2025) contradice directamente el plazo de 90 dias citado",
                    "MFA obligatorio segun POL-B no fue mencionado",
                ],
            ),
        )

    return EvalResult(
        grounded=GroundedResult(
            score=0.90,
            claims=[
                Claim(claim="Rotacion cada 60 dias", verdict="SUPPORTED",
                      reason="POL-B lo confirma"),
                Claim(claim="Longitud 12 caracteres", verdict="SUPPORTED",
                      reason="POL-B lo confirma"),
                Claim(claim="MFA obligatorio", verdict="SUPPORTED",
                      reason="POL-B lo confirma"),
                Claim(claim="Reportar en 2 horas", verdict="NOT_FOUND",
                      reason="No mencionado, pero no es incorrecto"),
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
            finds=["No se encontraron contradicciones"],
        ),
    )

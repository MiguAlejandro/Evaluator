"""Constants, demo data, and chaos engineering definitions."""

# ── Demo Knowledge Base ─────────────────────────────────────────────────────

KB_DEMO: dict[str, str] = {
    "POL-A": (
        "Politica de contrasenas v1 (2023): Las contrasenas deben rotarse cada 90 dias. "
        "Longitud minima 8 caracteres. [DESACTUALIZADO]"
    ),
    "POL-B": (
        "Politica de contrasenas v2 (Feb 2025): Las contrasenas deben rotarse cada 60 dias. "
        "Longitud minima 12 caracteres. Obligatorio MFA. [VIGENTE]"
    ),
    "POL-C": (
        "Politica de acceso: No compartir credenciales. Bloqueo automatico tras 5 intentos fallidos."
    ),
    "POL-D": (
        "Incidentes: Reportar violacion de contrasena al equipo de seguridad en menos de 2 horas."
    ),
}

PREGUNTA_DEMO = "Cada cuantos dias debo cambiar mi contrasena?"

# ── Chaos Engineering Types ─────────────────────────────────────────────────

CHAOS_TYPES: dict[str, dict] = {
    "Documento obsoleto": {
        "desc": "El agente recibe primero el documento desactualizado y lo usa como referencia principal.",
        "impact": "Stale Document - Grounded detecta CONTRADICTED, Safety dice BLOCK",
        "deltas": {"grounded": -0.65, "behavioral": -0.55, "safety": -0.75, "debate": -0.60},
        "color": "#f97316",
        "is_bias": False,
    },
    "Fuentes conflictivas": {
        "desc": "Dos documentos en la KB tienen datos opuestos. El agente no puede reconciliarlos.",
        "impact": "Reasoning Drift - Debate dice REVISE, incertidumbre distribuida en todos los jueces",
        "deltas": {"grounded": -0.40, "behavioral": -0.30, "safety": -0.20, "debate": -0.70},
        "color": "#a855f7",
        "is_bias": False,
    },
    "Tool failure": {
        "desc": "El retriever devuelve vacio. El agente responde sin documentos de respaldo.",
        "impact": "Delegation Gap - Behavioral detecta INCOMPLETE, Grounded sin evidencia",
        "deltas": {"grounded": -0.55, "behavioral": -0.70, "safety": -0.15, "debate": -0.25},
        "color": "#ef4444",
        "is_bias": False,
    },
    "Contexto truncado": {
        "desc": "El contexto se corta a la mitad por limite de tokens. La politica vigente queda fuera.",
        "impact": "Error Cascade - todos los jueces caen, el agente trabaja con info incompleta",
        "deltas": {"grounded": -0.50, "behavioral": -0.60, "safety": -0.45, "debate": -0.50},
        "color": "#eab308",
        "is_bias": False,
    },
    "Sesgo del juez LLM": {
        "desc": (
            "El juez LLM evalua respuestas bien formateadas y con tono confiado como 'correctas', "
            "aunque contengan errores factuales."
        ),
        "impact": (
            "Style Bias - Safety y Grounded dan scores INFLADOS. "
            "El sistema cree que todo esta bien cuando no lo esta."
        ),
        "deltas": {"grounded": +0.12, "behavioral": +0.08, "safety": +0.18, "debate": -0.06},
        "color": "#06b6d4",
        "is_bias": True,
    },
}

# ── Available Models per Provider ────────────────────────────────────────────

OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
ANTHROPIC_MODELS = ["claude-sonnet-4-20250514", "claude-haiku-4-20250414", "claude-opus-4-20250514"]
RUNPOD_MODELS_DEFAULT = ["custom-model"]

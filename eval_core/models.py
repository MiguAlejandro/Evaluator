"""Pydantic models for the evaluation system."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── LLM Configuration ───────────────────────────────────────────────────────

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    RUNPOD = "runpod"


class ModelConfig(BaseModel):
    """Configuration for a single LLM model."""
    name: str = Field(description="Display name, e.g. 'GPT-4o-mini'")
    provider: LLMProvider
    api_key: str = Field(default="")
    model_id: str = Field(description="Model identifier, e.g. 'gpt-4o-mini'")
    endpoint_url: str = Field(default="", description="Custom endpoint URL (required for Runpod)")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=400, ge=1)

    @property
    def is_configured(self) -> bool:
        if self.provider == LLMProvider.RUNPOD:
            return bool(self.api_key and self.endpoint_url)
        return bool(self.api_key)


# ── Judge Results ────────────────────────────────────────────────────────────

class ClaimVerdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    NOT_FOUND = "NOT_FOUND"


class Claim(BaseModel):
    claim: str
    verdict: str
    reason: str


class JudgeResult(BaseModel):
    """Result from a single judge evaluation."""
    score: float = Field(ge=0.0, le=1.0)
    details: dict[str, Any] = Field(default_factory=dict)


class GroundedResult(JudgeResult):
    claims: list[Claim] = Field(default_factory=list)


class BehavioralResult(JudgeResult):
    flags: list[str] = Field(default_factory=list)


class SafetyResult(JudgeResult):
    action: str = "PASS"
    issues: list[str] = Field(default_factory=list)


class DebateResult(JudgeResult):
    verdict: str = "ACCEPT"
    finds: list[str] = Field(default_factory=list)


class EvalResult(BaseModel):
    """Consolidated result from all 4 judges."""
    grounded: GroundedResult
    behavioral: BehavioralResult
    safety: SafetyResult
    debate: DebateResult

    @property
    def average_score(self) -> float:
        return (
            self.grounded.score
            + self.behavioral.score
            + self.safety.score
            + self.debate.score
        ) / 4

    def to_legacy_dict(self) -> dict:
        """Convert to the dict format used by the original UI components."""
        return {
            "grounded": {
                "score": self.grounded.score,
                "claims": [c.model_dump() for c in self.grounded.claims],
            },
            "behavioral": {
                "score": self.behavioral.score,
                "flags": self.behavioral.flags,
            },
            "safety": {
                "score": self.safety.score,
                "action": self.safety.action,
                "issues": self.safety.issues,
            },
            "debate": {
                "score": self.debate.score,
                "verdict": self.debate.verdict,
                "finds": self.debate.finds,
            },
        }


# ── Pipeline Results ─────────────────────────────────────────────────────────

class PipelineResult(BaseModel):
    """Full result of running one model through the evaluation pipeline."""
    model_name: str
    provider: str
    pregunta: str
    extraccion: str
    respuesta: str
    eval_result: EvalResult
    latencia_s: float = 0.0
    force_failure: bool = False


class BenchmarkRecord(BaseModel):
    """A complete record of one model answering one question."""
    timestamp: str
    model_name: str
    provider: str
    question_id: str
    question_text: str
    question_level: str
    question_category: str = ""
    respuesta: str
    grounded: float
    behavioral: float
    safety: float
    debate: float
    promedio: float
    latencia_s: float
    safety_action: str = "PASS"
    debate_verdict: str = "ACCEPT"


def pipeline_result_to_records(
    result: PipelineResult,
    question_id: str = "LIBRE",
    question_level: str = "Custom",
    question_category: str = "",
    timestamp: str = "",
) -> BenchmarkRecord:
    """Convert a PipelineResult into a BenchmarkRecord for the history."""
    if not timestamp:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    e = result.eval_result
    return BenchmarkRecord(
        timestamp=timestamp,
        model_name=result.model_name,
        provider=result.provider,
        question_id=question_id,
        question_text=result.pregunta,
        question_level=question_level,
        question_category=question_category,
        respuesta=result.respuesta,
        grounded=e.grounded.score,
        behavioral=e.behavioral.score,
        safety=e.safety.score,
        debate=e.debate.score,
        promedio=e.average_score,
        latencia_s=result.latencia_s,
        safety_action=e.safety.action,
        debate_verdict=e.debate.verdict,
    )

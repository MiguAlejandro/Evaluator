"""Evaluation Pipeline: orchestrates Analyst -> Writer -> Judges.

The judges always use OpenAI gpt-4o-mini (via JudgeCouncil) so that
evaluation scores are consistent and comparable across all tested models.
"""

from __future__ import annotations

import time

from eval_core.models import ModelConfig, PipelineResult
from llms.base import BaseLLM, create_llm
from evaluators.judge_council import JudgeCouncil
from evaluators.mock_judge import mock_evaluate
from .analyst import run_analyst
from .writer import run_writer


def kb_to_str(kb: dict[str, str]) -> str:
    """Convert a KB dict to a single string for prompts."""
    return "\n".join(f"{k}: {v}" for k, v in kb.items())


class EvalPipeline:
    """Runs the full evaluation pipeline for one or more models.

    The judge is always OpenAI gpt-4o-mini for consistency.
    """

    def __init__(self, openai_api_key: str = ""):
        """
        Args:
            openai_api_key: OpenAI key for the judge. If empty, uses mock judge.
        """
        self._openai_api_key = openai_api_key
        self._council: JudgeCouncil | None = None
        if openai_api_key:
            self._council = JudgeCouncil(openai_api_key)

    def run(
        self,
        kb: dict[str, str],
        pregunta: str,
        llm: BaseLLM | None,
        force_failure: bool = False,
        expected_answer: str = "",
    ) -> PipelineResult:
        """Run the full pipeline for a single model.

        Args:
            kb: Knowledge base as {doc_id: content}.
            pregunta: User question.
            llm: The LLM under test (None = mock mode).
            force_failure: Whether to inject a silent failure.
            expected_answer: Gold reference answer for correctness judge.

        Returns:
            PipelineResult with extraction, response, and evaluation.
        """
        kb_str = kb_to_str(kb)

        t0 = time.time()

        # Step 1: Analyst
        extraccion = run_analyst(kb_str, llm)

        # Step 2: Writer
        respuesta = run_writer(extraccion, pregunta, kb_str, llm, force_failure)

        # Step 3: Judges (always OpenAI gpt-4o-mini, 6 judges)
        if self._council is not None:
            try:
                eval_result = self._council.evaluate(
                    kb_str, respuesta,
                    pregunta=pregunta,
                    expected_answer=expected_answer,
                )
            except Exception:
                eval_result = mock_evaluate(respuesta, force_failure)
        else:
            eval_result = mock_evaluate(respuesta, force_failure)

        latencia = time.time() - t0

        model_name = llm.name if llm else "Demo (mock)"
        provider = llm.provider.value if llm else "mock"

        return PipelineResult(
            model_name=model_name,
            provider=provider,
            pregunta=pregunta,
            extraccion=extraccion,
            respuesta=respuesta,
            eval_result=eval_result,
            latencia_s=latencia,
            force_failure=force_failure,
        )

    def run_comparison(
        self,
        kb: dict[str, str],
        pregunta: str,
        model_configs: list[ModelConfig],
    ) -> list[PipelineResult]:
        """Run the pipeline for multiple models for comparison.

        All models receive the same KB and question.
        The judge (OpenAI gpt-4o-mini) is the same for all.

        Args:
            kb: Knowledge base.
            pregunta: User question.
            model_configs: List of model configurations to evaluate.

        Returns:
            List of PipelineResults, one per model.
        """
        results = []
        for config in model_configs:
            try:
                llm = create_llm(config)
                result = self.run(kb, pregunta, llm)
            except Exception as e:
                result = PipelineResult(
                    model_name=config.name,
                    provider=config.provider.value,
                    pregunta=pregunta,
                    extraccion="",
                    respuesta=f"Error: {e}",
                    eval_result=mock_evaluate("error", force_failure=True),
                    latencia_s=0.0,
                    force_failure=False,
                )
            results.append(result)

        return results

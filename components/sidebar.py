"""Sidebar: model configuration, API keys, and pipeline options."""

from __future__ import annotations

import os

import streamlit as st

from core.models import ModelConfig, LLMProvider


def _clean_key(raw: str) -> str:
    """Strip whitespace and non-ASCII chars from pasted API keys."""
    return raw.strip().encode("ascii", errors="ignore").decode("ascii")


def render_sidebar() -> dict:
    """Render the sidebar and return the collected configuration.

    Returns a dict with keys:
        - model_configs: list[ModelConfig] of active models
        - simulate_failure: bool
        - umbral: float
        - use_rag: bool
        - openai_api_key: str (needed for embeddings + judge)
    """
    with st.sidebar:
        st.title("Multi-Model Eval")
        st.markdown("---")

        # ── OpenAI API Key (required for embeddings + judge) ─────────────
        st.markdown("**OpenAI API Key** (obligatoria para embeddings y juez)")
        oai_key = st.text_input(
            "OpenAI API Key", type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            placeholder="sk-...", key="oai_key",
        )
        oai_key_clean = _clean_key(oai_key) if oai_key else ""

        if oai_key_clean:
            st.success("OpenAI key lista")
        else:
            st.warning("Se requiere OpenAI API Key para embeddings y juez")

        st.markdown("---")

        # ── Model Configuration ─────────────────────────────────────────
        st.markdown("**Modelos a evaluar**")
        st.caption("Selecciona proveedor, escribe el nombre exacto del modelo y su API key.")
        model_configs: list[ModelConfig] = []

        # OpenAI
        use_openai = st.checkbox("OpenAI", value=True)
        if use_openai and oai_key_clean:
            with st.expander("OpenAI Config", expanded=True):
                oai_model = st.text_input(
                    "Modelo", value="gpt-4o-mini",
                    placeholder="gpt-4o, gpt-4-turbo, gpt-3.5-turbo...",
                    key="oai_model",
                )
                if oai_model.strip():
                    model_configs.append(ModelConfig(
                        name=f"OpenAI {oai_model.strip()}",
                        provider=LLMProvider.OPENAI,
                        api_key=oai_key_clean,
                        model_id=oai_model.strip(),
                    ))

        # Anthropic
        use_anthropic = st.checkbox("Anthropic (Claude)", value=False)
        if use_anthropic:
            with st.expander("Anthropic Config", expanded=True):
                ant_key = st.text_input(
                    "API Key", type="password",
                    value=os.getenv("ANTHROPIC_API_KEY", ""),
                    placeholder="sk-ant-...", key="ant_key",
                )
                ant_model = st.text_input(
                    "Modelo", value="claude-sonnet-4-20250514",
                    placeholder="claude-sonnet-4-20250514, claude-haiku-4-20250414...",
                    key="ant_model",
                )
                if ant_key and ant_model.strip():
                    model_configs.append(ModelConfig(
                        name=f"Anthropic {ant_model.strip()}",
                        provider=LLMProvider.ANTHROPIC,
                        api_key=_clean_key(ant_key),
                        model_id=ant_model.strip(),
                    ))

        # Runpod
        use_runpod = st.checkbox("Runpod (Custom Endpoint)", value=False)
        if use_runpod:
            with st.expander("Runpod Config", expanded=True):
                rp_url = st.text_input(
                    "Endpoint URL",
                    placeholder="https://api.runpod.ai/v2/...",
                    key="rp_url",
                )
                rp_key = st.text_input(
                    "API Key", type="password",
                    placeholder="rp_...", key="rp_key",
                )
                rp_model = st.text_input(
                    "Modelo", value="",
                    placeholder="meta-llama/Llama-3-8b, mistralai/Mistral-7B...",
                    key="rp_model",
                )
                if rp_key and rp_url:
                    model_name = rp_model.strip() or "custom"
                    model_configs.append(ModelConfig(
                        name=f"Runpod {model_name}",
                        provider=LLMProvider.RUNPOD,
                        api_key=_clean_key(rp_key),
                        model_id=model_name,
                        endpoint_url=rp_url.strip(),
                    ))

        # Status
        if model_configs:
            st.success(f"{len(model_configs)} modelo(s) configurado(s)")
        else:
            st.info("Sin API keys -> modo demo (mock)")

        st.markdown("---")

        # ── Judge info (fixed: always OpenAI gpt-4o-mini) ────────────────
        st.markdown("**Modelo Juez**")
        st.caption("Fijo: OpenAI gpt-4o-mini (usa tu API key)")
        st.caption("Garantiza evaluaciones consistentes entre modelos.")

        st.markdown("---")

        # ── Pipeline Options ─────────────────────────────────────────────
        st.markdown("**Opciones**")
        simulate_failure = st.checkbox(
            "Simular fallo silencioso",
            help="El agente usara el documento DESACTUALIZADO a proposito",
        )
        umbral = st.slider("Umbral PASS jueces", 0.3, 0.9, 0.65, 0.05)
        use_rag = st.checkbox(
            "Usar RAG (OpenAI Embeddings)",
            value=False,
            help="Usa retrieval con embeddings OpenAI en lugar de pasar toda la KB directamente.",
        )
        if use_rag and not oai_key_clean:
            st.warning("RAG requiere OpenAI API Key para embeddings")
            use_rag = False

        st.markdown("---")

        # ── Active agents display ────────────────────────────────────────
        st.markdown("**Agentes activos:**")
        st.info("Agente 1: Analista")
        st.info("Agente 2: Redactor")
        st.warning("Agente 3: Juez (x4)")

    return {
        "model_configs": model_configs,
        "simulate_failure": simulate_failure,
        "umbral": umbral,
        "use_rag": use_rag,
        "openai_api_key": oai_key_clean,
    }

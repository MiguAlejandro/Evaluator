"""Tab 5: Comparacion Multi-Modelo — side-by-side model evaluation."""

from __future__ import annotations

import time

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.constants import KB_DEMO, PREGUNTA_DEMO
from core.models import ModelConfig
from components.styles import score_color
from llms.base import create_llm
from agents.pipeline import EvalPipeline, kb_to_str


def render_tab_comparison(sidebar_cfg: dict):
    """Render the multi-model comparison tab."""
    model_configs: list[ModelConfig] = sidebar_cfg["model_configs"]
    umbral: float = sidebar_cfg["umbral"]

    st.subheader("Comparacion Multi-Modelo")
    st.caption(
        "Todos los modelos reciben la misma pregunta y el mismo contexto. "
        "El mismo juez los evalua con los 4 criterios para una comparacion justa."
    )

    if len(model_configs) < 2:
        st.info(
            "Configura al menos **2 modelos** en el sidebar para usar la comparacion. "
            "Activa OpenAI + Anthropic, o agrega Runpod."
        )
        st.markdown(
            '<div class="card" style="border-color:#334155;color:#64748b">'
            "Ejemplo: activa OpenAI y Anthropic en el sidebar, ingresa sus API keys, "
            "y luego vuelve aqui para compararlos.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Input ────────────────────────────────────────────────────────
    st.markdown("**Pregunta para todos los modelos:**")
    pregunta = st.text_input("", value=PREGUNTA_DEMO, key="comparison_pregunta")

    st.markdown(f"**Modelos a comparar:** {', '.join(c.name for c in model_configs)}")
    st.caption("Juez: OpenAI gpt-4o-mini (fijo para todos)")

    if "comparison_results" not in st.session_state:
        st.session_state["comparison_results"] = None

    if st.button("Comparar Modelos", type="primary", use_container_width=True,
                 key="btn_compare"):
        if not pregunta:
            st.warning("Escribe una pregunta")
            return

        oai_key = sidebar_cfg.get("openai_api_key", "")
        pipeline = EvalPipeline(openai_api_key=oai_key)
        kb = KB_DEMO  # Use demo KB for comparison

        with st.status(f"Evaluando {len(model_configs)} modelos...", expanded=True) as status:
            results = []
            for i, cfg in enumerate(model_configs):
                st.write(f"[{i+1}/{len(model_configs)}] Evaluando {cfg.name}...")
                try:
                    llm = create_llm(cfg)
                    result = pipeline.run(kb, pregunta, llm)
                    results.append(result)
                except Exception as e:
                    st.write(f"  Error con {cfg.name}: {e}")
                    from evaluators.mock_judge import mock_evaluate
                    from core.models import PipelineResult
                    results.append(PipelineResult(
                        model_name=cfg.name,
                        provider=cfg.provider.value,
                        pregunta=pregunta,
                        extraccion="",
                        respuesta=f"Error: {e}",
                        eval_result=mock_evaluate("error", force_failure=True),
                        latencia_s=0.0,
                    ))
            status.update(label="Comparacion completa", state="complete")

        st.session_state["comparison_results"] = results

    # ── Results ──────────────────────────────────────────────────────
    results = st.session_state.get("comparison_results")
    if not results:
        st.markdown(
            '<div class="card" style="border-color:#334155;color:#64748b">'
            "Presiona 'Comparar Modelos' para ejecutar la evaluacion.</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown("---")

    # ── Comparison Table ─────────────────────────────────────────────
    st.markdown("#### Tabla Comparativa")
    jkeys = ["grounded", "behavioral", "safety", "debate"]

    rows = []
    for r in results:
        e = r.eval_result
        avg = e.average_score
        rows.append({
            "Modelo": r.model_name,
            "Provider": r.provider,
            "Grounded": f"{e.grounded.score:.0%}",
            "Behavioral": f"{e.behavioral.score:.0%}",
            "Safety": f"{e.safety.score:.0%}",
            "Debate": f"{e.debate.score:.0%}",
            "Promedio": f"{avg:.0%}",
            "Latencia": f"{r.latencia_s:.1f}s",
            "_avg": avg,
        })

    # Sort by average descending
    rows.sort(key=lambda x: x["_avg"], reverse=True)
    df = pd.DataFrame(rows).drop(columns=["_avg"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Ranking ──────────────────────────────────────────────────────
    best = rows[0]
    best_color = "#22c55e"
    st.markdown(
        f'<div class="card" style="border-color:{best_color}">'
        f'<b style="color:{best_color}">Mejor modelo: {best["Modelo"]}</b>'
        f' — Promedio: {best["Promedio"]} | Latencia: {best["Latencia"]}'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Radar Chart (all models overlaid) ────────────────────────────
    st.markdown("#### Radar de Comparacion")
    jnames = ["Grounded", "Behavioral", "Safety", "Debate"]
    colors = ["#3b82f6", "#ef4444", "#22c55e", "#eab308", "#a855f7", "#06b6d4"]

    fig_radar = go.Figure()
    for i, r in enumerate(results):
        e = r.eval_result
        vals = [e.grounded.score, e.behavioral.score, e.safety.score, e.debate.score]
        v2 = vals + [vals[0]]
        t2 = jnames + [jnames[0]]
        fig_radar.add_trace(
            go.Scatterpolar(
                r=v2,
                theta=t2,
                fill="toself",
                name=r.model_name,
                line=dict(color=colors[i % len(colors)], width=2),
                opacity=0.7,
            )
        )

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 1], color="#94a3b8"),
            bgcolor="#1e293b",
            angularaxis=dict(color="#94a3b8"),
        ),
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        legend=dict(font=dict(color="#e2e8f0")),
        height=350,
        margin=dict(l=60, r=60, t=30, b=30),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Grouped Bar Chart ────────────────────────────────────────────
    st.markdown("#### Scores por Juez")
    fig_bar = go.Figure()
    for i, r in enumerate(results):
        e = r.eval_result
        fig_bar.add_trace(
            go.Bar(
                name=r.model_name,
                x=jnames,
                y=[e.grounded.score, e.behavioral.score, e.safety.score, e.debate.score],
                marker_color=colors[i % len(colors)],
                text=[f"{s:.0%}" for s in [
                    e.grounded.score, e.behavioral.score, e.safety.score, e.debate.score
                ]],
                textposition="auto",
            )
        )

    fig_bar.update_layout(
        barmode="group",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#e2e8f0"),
        legend=dict(font=dict(color="#e2e8f0")),
        height=300,
        margin=dict(l=40, r=20, t=20, b=40),
        yaxis=dict(range=[0, 1.05]),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Responses Side by Side ───────────────────────────────────────
    st.markdown("#### Respuestas lado a lado")
    cols = st.columns(len(results))
    for i, (col, r) in enumerate(zip(cols, results)):
        e = r.eval_result
        avg = e.average_score
        sc = score_color(avg, umbral)
        col.markdown(
            f'<div class="card" style="border-color:{sc}">'
            f'<b style="color:{colors[i % len(colors)]}">{r.model_name}</b>'
            f'<span class="score" style="color:{sc};font-size:1.5rem;margin-left:8px">'
            f"{avg:.0%}</span><br><br>"
            f'<span style="font-family:monospace;font-size:.85rem">'
            f'{r.respuesta.replace(chr(10), "<br>")}</span></div>',
            unsafe_allow_html=True,
        )

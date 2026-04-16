"""Tab 3: Benchmark Estandar — run standardized evaluation across models."""

from __future__ import annotations

from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.constants import KB_DEMO, BENCHMARK_QUESTIONS
from core.models import ModelConfig, PipelineResult, BenchmarkRecord, pipeline_result_to_records
from components.styles import score_color
from llms.base import create_llm
from agents.pipeline import EvalPipeline
from evaluators.mock_judge import mock_evaluate


def _init_history():
    """Ensure benchmark_history exists in session state."""
    if "benchmark_history" not in st.session_state:
        st.session_state["benchmark_history"] = []


def render_tab_benchmark(sidebar_cfg: dict):
    """Render the benchmark runner tab."""
    _init_history()
    model_configs: list[ModelConfig] = sidebar_cfg["model_configs"]
    umbral: float = sidebar_cfg["umbral"]

    st.subheader("Benchmark Estandar")
    st.caption(
        "Ejecuta las preguntas estandarizadas contra tus modelos. "
        "Todos reciben el mismo contexto y el mismo juez (OpenAI gpt-4o-mini)."
    )

    if not model_configs:
        st.info("Configura al menos **1 modelo** en el sidebar para ejecutar el benchmark.")
        return

    # ── Question selection ───────────────────────────────────────────
    st.markdown("#### Selecciona las preguntas")

    mode = st.radio(
        "Modo:",
        ["Benchmark completo (10 preguntas)", "Seleccionar preguntas", "Pregunta libre"],
        key="bench_mode",
        horizontal=True,
    )

    preguntas_to_run: list[dict] = []

    if mode == "Benchmark completo (10 preguntas)":
        preguntas_to_run = BENCHMARK_QUESTIONS
        st.caption(f"{len(preguntas_to_run)} preguntas: 3 basicas, 2 intermedias, 2 avanzadas, 3 experto")

        with st.expander("Ver preguntas del benchmark"):
            for q in BENCHMARK_QUESTIONS:
                nivel_colors = {
                    "Basico": "#22c55e", "Intermedio": "#eab308",
                    "Avanzado": "#f97316", "Experto": "#ef4444",
                }
                nc = nivel_colors.get(q["nivel"], "#94a3b8")
                st.markdown(
                    f'<span style="color:{nc};font-weight:bold">[{q["id"]}] {q["nivel"]}</span>'
                    f' | {q["pregunta"]}',
                    unsafe_allow_html=True,
                )

    elif mode == "Seleccionar preguntas":
        q_labels = [
            f"[{q['id']}] {q['nivel']} | {q['pregunta'][:80]}"
            for q in BENCHMARK_QUESTIONS
        ]
        selected = st.multiselect(
            "Preguntas:", q_labels,
            default=q_labels[:3],
            key="bench_q_select",
        )
        for label in selected:
            idx = q_labels.index(label)
            preguntas_to_run.append(BENCHMARK_QUESTIONS[idx])

    else:
        libre = st.text_input("Escribe tu pregunta:", key="bench_libre")
        if libre.strip():
            preguntas_to_run = [{
                "id": "LIBRE",
                "pregunta": libre.strip(),
                "nivel": "Custom",
                "categoria": "Libre",
                "doc_clave": "-",
                "respuesta_esperada": "",
            }]

    # ── Model info ───────────────────────────────────────────────────
    st.markdown(f"**Modelos:** {', '.join(c.name for c in model_configs)}")
    st.caption("Juez: OpenAI gpt-4o-mini (fijo)")

    n_total = len(preguntas_to_run) * len(model_configs)
    btn_label = (
        f"Ejecutar benchmark ({len(preguntas_to_run)} preguntas x "
        f"{len(model_configs)} modelos = {n_total} evaluaciones)"
    )

    if "bench_last_results" not in st.session_state:
        st.session_state["bench_last_results"] = None

    # ── Run benchmark ────────────────────────────────────────────────
    if st.button(btn_label, type="primary", use_container_width=True, key="btn_bench"):
        if not preguntas_to_run:
            st.warning("Selecciona al menos una pregunta")
            return

        oai_key = sidebar_cfg.get("openai_api_key", "")
        pipeline = EvalPipeline(openai_api_key=oai_key)
        kb = KB_DEMO
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        results_by_model: dict[str, list[PipelineResult]] = {c.name: [] for c in model_configs}
        new_records: list[BenchmarkRecord] = []

        with st.status(f"Ejecutando {n_total} evaluaciones...", expanded=True) as status:
            step = 0
            for q in preguntas_to_run:
                for cfg in model_configs:
                    step += 1
                    st.write(f"[{step}/{n_total}] {cfg.name} | {q['id']}: {q['pregunta'][:50]}...")
                    try:
                        llm = create_llm(cfg)
                        result = pipeline.run(kb, q["pregunta"], llm)
                    except Exception as e:
                        result = PipelineResult(
                            model_name=cfg.name,
                            provider=cfg.provider.value,
                            pregunta=q["pregunta"],
                            extraccion="",
                            respuesta=f"Error: {e}",
                            eval_result=mock_evaluate("error", force_failure=True),
                            latencia_s=0.0,
                        )
                    results_by_model[cfg.name].append(result)

                    # Save to history
                    record = pipeline_result_to_records(
                        result,
                        question_id=q["id"],
                        question_level=q["nivel"],
                        question_category=q.get("categoria", ""),
                        timestamp=ts,
                    )
                    new_records.append(record)

            status.update(label="Benchmark completo", state="complete")

        # Accumulate in history
        st.session_state["benchmark_history"].extend(new_records)
        st.session_state["bench_last_results"] = {
            "by_model": results_by_model,
            "questions": preguntas_to_run,
            "records": new_records,
        }

        st.success(
            f"{len(new_records)} evaluaciones guardadas en el historial. "
            f"Total acumulado: {len(st.session_state['benchmark_history'])} registros."
        )

    # ── Display last results ─────────────────────────────────────────
    last = st.session_state.get("bench_last_results")
    if not last:
        st.markdown(
            '<div class="card" style="border-color:#334155;color:#64748b">'
            "Selecciona preguntas y presiona el boton para ejecutar el benchmark.</div>",
            unsafe_allow_html=True,
        )
        return

    results_by_model = last["by_model"]
    questions = last["questions"]

    st.markdown("---")

    # ── Summary Table ────────────────────────────────────────────────
    st.markdown("#### Ranking (esta ejecucion)")
    jnames = ["Grounded", "Behavioral", "Safety", "Debate"]
    colors = ["#3b82f6", "#ef4444", "#22c55e", "#eab308", "#a855f7", "#06b6d4"]

    summary_rows = []
    for model_name, results in results_by_model.items():
        n = len(results)
        avg_g = sum(r.eval_result.grounded.score for r in results) / n
        avg_b = sum(r.eval_result.behavioral.score for r in results) / n
        avg_s = sum(r.eval_result.safety.score for r in results) / n
        avg_d = sum(r.eval_result.debate.score for r in results) / n
        avg_total = (avg_g + avg_b + avg_s + avg_d) / 4
        avg_lat = sum(r.latencia_s for r in results) / n

        summary_rows.append({
            "Modelo": model_name,
            "Grounded": f"{avg_g:.0%}",
            "Behavioral": f"{avg_b:.0%}",
            "Safety": f"{avg_s:.0%}",
            "Debate": f"{avg_d:.0%}",
            "Promedio": f"{avg_total:.0%}",
            "Latencia": f"{avg_lat:.1f}s",
            "_avg": avg_total,
            "_g": avg_g, "_b": avg_b, "_s": avg_s, "_d": avg_d,
        })

    summary_rows.sort(key=lambda x: x["_avg"], reverse=True)

    # Winner
    best = summary_rows[0]
    st.markdown(
        f'<div class="card" style="border-color:#22c55e">'
        f'<b style="color:#22c55e">Mejor modelo: {best["Modelo"]}</b>'
        f' — Promedio: {best["Promedio"]} | Latencia: {best["Latencia"]}'
        f' | {len(questions)} preguntas</div>',
        unsafe_allow_html=True,
    )

    df_summary = pd.DataFrame(summary_rows).drop(columns=["_avg", "_g", "_b", "_s", "_d"])
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    # ── Radar ────────────────────────────────────────────────────────
    col_radar, col_bar = st.columns(2)

    with col_radar:
        st.markdown("#### Radar")
        fig_radar = go.Figure()
        for i, row in enumerate(summary_rows):
            vals = [row["_g"], row["_b"], row["_s"], row["_d"]]
            v2 = vals + [vals[0]]
            t2 = jnames + [jnames[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=v2, theta=t2, fill="toself",
                name=row["Modelo"],
                line=dict(color=colors[i % len(colors)], width=2), opacity=0.7,
            ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 1], color="#94a3b8"),
                bgcolor="#1e293b", angularaxis=dict(color="#94a3b8"),
            ),
            paper_bgcolor="#0f172a", font=dict(color="#e2e8f0"),
            legend=dict(font=dict(color="#e2e8f0")),
            height=320, margin=dict(l=50, r=50, t=20, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_bar:
        st.markdown("#### Scores por Juez")
        fig_bar = go.Figure()
        for i, row in enumerate(summary_rows):
            fig_bar.add_trace(go.Bar(
                name=row["Modelo"], x=jnames,
                y=[row["_g"], row["_b"], row["_s"], row["_d"]],
                marker_color=colors[i % len(colors)],
                text=[f"{s:.0%}" for s in [row["_g"], row["_b"], row["_s"], row["_d"]]],
                textposition="auto",
            ))
        fig_bar.update_layout(
            barmode="group", paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"), legend=dict(font=dict(color="#e2e8f0")),
            height=320, margin=dict(l=40, r=20, t=20, b=40),
            yaxis=dict(range=[0, 1.05]),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Detail per question ──────────────────────────────────────────
    if len(questions) > 1:
        st.markdown("#### Detalle por pregunta")
        for model_name, results in results_by_model.items():
            with st.expander(f"{model_name}", expanded=False):
                q_rows = []
                for r, q in zip(results, questions):
                    e = r.eval_result
                    q_rows.append({
                        "ID": q["id"],
                        "Nivel": q["nivel"],
                        "Pregunta": q["pregunta"][:60] + "...",
                        "Grounded": f"{e.grounded.score:.0%}",
                        "Behavioral": f"{e.behavioral.score:.0%}",
                        "Safety": f"{e.safety.score:.0%}",
                        "Debate": f"{e.debate.score:.0%}",
                        "Promedio": f"{e.average_score:.0%}",
                    })
                st.dataframe(pd.DataFrame(q_rows), use_container_width=True, hide_index=True)

    st.caption("Los resultados se guardaron en el historial. Ve a **Resultados & Historial** para ver todos los datos acumulados y descargar CSV.")

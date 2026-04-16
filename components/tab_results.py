"""Tab 4: Resultados & Historial — accumulated benchmark results + CSV download."""

from __future__ import annotations

import io

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from eval_core.models import BenchmarkRecord


def _history_to_df(history: list[BenchmarkRecord]) -> pd.DataFrame:
    """Convert the benchmark history to a DataFrame."""
    rows = []
    for r in history:
        rows.append({
            "Timestamp": r.timestamp,
            "Modelo": r.model_name,
            "Provider": r.provider,
            "Pregunta ID": r.question_id,
            "Pregunta": r.question_text,
            "Nivel": r.question_level,
            "Categoria": r.question_category,
            "Respuesta": r.respuesta,
            "Grounded": r.grounded,
            "Behavioral": r.behavioral,
            "Safety": r.safety,
            "Debate": r.debate,
            "Promedio": r.promedio,
            "Latencia (s)": r.latencia_s,
            "Safety Action": r.safety_action,
            "Debate Verdict": r.debate_verdict,
        })
    return pd.DataFrame(rows)


def render_tab_results(sidebar_cfg: dict):
    """Render the results & history tab."""
    if "benchmark_history" not in st.session_state:
        st.session_state["benchmark_history"] = []

    history: list[BenchmarkRecord] = st.session_state["benchmark_history"]

    st.subheader("Resultados & Historial")
    st.caption(
        "Todos los resultados de benchmark se acumulan aqui. "
        "Filtra, compara y descarga en CSV."
    )

    if not history:
        st.info(
            "No hay resultados todavia. Ejecuta el benchmark en la pestana "
            "**Benchmark Estandar** o usa el **Pipeline** para generar resultados."
        )
        return

    df = _history_to_df(history)
    n_records = len(df)
    n_models = df["Modelo"].nunique()
    n_questions = df["Pregunta ID"].nunique()

    # ── Stats bar ────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total registros", n_records)
    c2.metric("Modelos evaluados", n_models)
    c3.metric("Preguntas unicas", n_questions)
    c4.metric("Promedio global", f"{df['Promedio'].mean():.0%}")

    st.markdown("---")

    # ── Filters ──────────────────────────────────────────────────────
    st.markdown("#### Filtros")
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        models_available = sorted(df["Modelo"].unique().tolist())
        filter_models = st.multiselect(
            "Modelos", models_available, default=models_available, key="res_filter_model"
        )
    with fcol2:
        levels_available = sorted(df["Nivel"].unique().tolist())
        filter_levels = st.multiselect(
            "Niveles", levels_available, default=levels_available, key="res_filter_level"
        )
    with fcol3:
        qids_available = sorted(df["Pregunta ID"].unique().tolist())
        filter_qids = st.multiselect(
            "Preguntas", qids_available, default=qids_available, key="res_filter_qid"
        )

    # Apply filters
    mask = (
        df["Modelo"].isin(filter_models)
        & df["Nivel"].isin(filter_levels)
        & df["Pregunta ID"].isin(filter_qids)
    )
    df_filtered = df[mask]

    if df_filtered.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        return

    st.caption(f"Mostrando {len(df_filtered)} de {n_records} registros")

    st.markdown("---")

    # ── Section 1: Summary per model ─────────────────────────────────
    st.markdown("#### Resumen por Modelo")
    summary = (
        df_filtered.groupby("Modelo")[["Grounded", "Behavioral", "Safety", "Debate", "Promedio", "Latencia (s)"]]
        .mean()
        .sort_values("Promedio", ascending=False)
    )
    summary_display = summary.copy()
    for col in ["Grounded", "Behavioral", "Safety", "Debate", "Promedio"]:
        summary_display[col] = summary_display[col].apply(lambda x: f"{x:.0%}")
    summary_display["Latencia (s)"] = summary_display["Latencia (s)"].apply(lambda x: f"{x:.1f}")
    summary_display.insert(0, "# Evals", df_filtered.groupby("Modelo").size())

    st.dataframe(summary_display, use_container_width=True)

    # ── Section 2: Heatmap models x questions ────────────────────────
    unique_qids = sorted(df_filtered["Pregunta ID"].unique().tolist())
    unique_models = sorted(df_filtered["Modelo"].unique().tolist())

    if len(unique_qids) > 1 and len(unique_models) >= 1:
        st.markdown("#### Heatmap: Modelo x Pregunta (score promedio)")

        pivot = df_filtered.pivot_table(
            index="Modelo", columns="Pregunta ID",
            values="Promedio", aggfunc="mean",
        )
        # Reorder columns by Q ID
        pivot = pivot.reindex(columns=sorted(pivot.columns))

        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="RdYlGn", zmin=0, zmax=1,
            text=[[f"{v:.0%}" if pd.notna(v) else "-" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            hovertemplate="%{y} | %{x}: %{z:.2f}<extra></extra>",
        ))
        row_h = max(200, 80 + len(unique_models) * 50)
        fig_heat.update_layout(
            paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            font=dict(color="#e2e8f0"), height=row_h,
            margin=dict(l=150, r=20, t=30, b=60),
            xaxis_title="Pregunta", yaxis_title="Modelo",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── Section 3: Heatmap models x judge (aggregated) ───────────────
    if len(unique_models) > 1:
        st.markdown("#### Heatmap: Modelo x Juez (promedios globales)")
        judge_cols = ["Grounded", "Behavioral", "Safety", "Debate"]
        judge_pivot = df_filtered.groupby("Modelo")[judge_cols].mean()
        judge_pivot = judge_pivot.sort_values("Grounded", ascending=False)

        fig_judge = go.Figure(go.Heatmap(
            z=judge_pivot.values,
            x=judge_cols,
            y=judge_pivot.index.tolist(),
            colorscale="RdYlGn", zmin=0, zmax=1,
            text=[[f"{v:.0%}" for v in row] for row in judge_pivot.values],
            texttemplate="%{text}",
            hovertemplate="%{y} | %{x}: %{z:.2f}<extra></extra>",
        ))
        fig_judge.update_layout(
            paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            font=dict(color="#e2e8f0"), height=max(180, 80 + len(unique_models) * 50),
            margin=dict(l=150, r=20, t=30, b=60),
        )
        st.plotly_chart(fig_judge, use_container_width=True)

    # ── Section 4: Detailed table ────────────────────────────────────
    st.markdown("#### Tabla Detallada")
    display_cols = [
        "Timestamp", "Modelo", "Pregunta ID", "Nivel",
        "Grounded", "Behavioral", "Safety", "Debate", "Promedio",
        "Latencia (s)", "Safety Action", "Debate Verdict",
    ]
    df_display = df_filtered[display_cols].copy()
    for col in ["Grounded", "Behavioral", "Safety", "Debate", "Promedio"]:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.0%}")
    df_display["Latencia (s)"] = df_display["Latencia (s)"].apply(lambda x: f"{x:.1f}")

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── Section 5: Responses viewer ──────────────────────────────────
    with st.expander("Ver respuestas de los modelos"):
        for _, row in df_filtered.iterrows():
            st.markdown(
                f'<div class="card" style="border-color:#334155;padding:10px">'
                f'<b>{row["Modelo"]}</b> | [{row["Pregunta ID"]}] {row["Pregunta"][:80]}...<br>'
                f'<span style="color:#94a3b8;font-size:.8rem">Promedio: {row["Promedio"]:.0%}</span>'
                f'<br><span style="font-family:monospace;font-size:.82rem">'
                f'{str(row["Respuesta"]).replace(chr(10), "<br>")}</span></div>',
                unsafe_allow_html=True,
            )

    # ── Section 6: CSV Download ──────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Descargar Resultados")

    csv_buffer = io.StringIO()
    df_filtered.to_csv(csv_buffer, index=False, encoding="utf-8")

    col_dl1, col_dl2 = st.columns([1, 2])
    with col_dl1:
        st.download_button(
            label=f"Descargar CSV ({len(df_filtered)} registros)",
            data=csv_buffer.getvalue(),
            file_name="benchmark_resultados.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_dl2:
        if st.button("Limpiar todo el historial", use_container_width=True):
            st.session_state["benchmark_history"] = []
            st.session_state["bench_last_results"] = None
            st.rerun()

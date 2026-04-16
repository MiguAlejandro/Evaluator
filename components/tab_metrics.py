"""Tab 3: Metricas de Coordinacion — execution history heatmap."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render_tab_metrics(sidebar_cfg: dict):
    """Render the coordination metrics / execution history tab."""
    st.subheader("Historial de Ejecuciones - Comparacion en Vivo")
    st.caption("Cada vez que ejecutas el pipeline, aparece una nueva fila. "
               "Ejecuta con fallo y sin fallo para ver el contraste.")

    # ── Metric explanations (always visible) ─────────────────────────
    st.markdown("#### Que mide cada columna?")
    mc1, mc2, mc3 = st.columns(3)
    mc1.markdown(
        '<div class="card" style="border-color:#3b82f6">'
        '<div style="color:#3b82f6;font-weight:bold">Grounded</div>'
        '<div style="font-size:.82rem;margin-top:4px">Cada dato mencionado tiene evidencia en los docs?</div>'
        '<div style="color:#94a3b8;font-size:.75rem;margin-top:4px">'
        "1.0 = todo respaldado / 0.0 = nada tiene fuente</div></div>",
        unsafe_allow_html=True,
    )
    mc2.markdown(
        '<div class="card" style="border-color:#a855f7">'
        '<div style="color:#a855f7;font-weight:bold">Behavioral</div>'
        '<div style="font-size:.82rem;margin-top:4px">El agente cito fuentes y uso la version vigente?</div>'
        '<div style="color:#94a3b8;font-size:.75rem;margin-top:4px">'
        "1.0 = proceso correcto / bajo = cito desactualizado u omitio</div></div>",
        unsafe_allow_html=True,
    )
    mc3.markdown(
        '<div class="card" style="border-color:#ef4444">'
        '<div style="color:#ef4444;font-weight:bold">Safety</div>'
        '<div style="font-size:.82rem;margin-top:4px">Algun dato mencionado es factualmente incorrecto?</div>'
        '<div style="color:#94a3b8;font-size:.75rem;margin-top:4px">'
        "1.0 = PASS / 0.6 = WARN / 0.2 = BLOCK (dato incorrecto)</div></div>",
        unsafe_allow_html=True,
    )

    mc4, mc5, mc6 = st.columns(3)
    mc4.markdown(
        '<div class="card" style="border-color:#eab308">'
        '<div style="color:#eab308;font-weight:bold">Debate</div>'
        '<div style="font-size:.82rem;margin-top:4px">Hay contradiccion real con los docs vigentes?</div>'
        '<div style="color:#94a3b8;font-size:.75rem;margin-top:4px">'
        "0.9 = ACCEPT (sin contradiccion) / 0.3 = REVISE</div></div>",
        unsafe_allow_html=True,
    )
    mc5.markdown(
        '<div class="card" style="border-color:#06b6d4">'
        '<div style="color:#06b6d4;font-weight:bold">Acuerdo</div>'
        '<div style="font-size:.82rem;margin-top:4px">Todos los jueces coinciden en su evaluacion?</div>'
        '<div style="color:#94a3b8;font-size:.75rem;margin-top:4px">'
        "1 - diferencia entre el juez mas alto y el mas bajo</div></div>",
        unsafe_allow_html=True,
    )
    mc6.markdown(
        '<div class="card" style="border-color:#8b5cf6">'
        '<div style="color:#8b5cf6;font-weight:bold">Global</div>'
        '<div style="font-size:.82rem;margin-top:4px">Calidad general de la respuesta</div>'
        '<div style="color:#94a3b8;font-size:.75rem;margin-top:4px">'
        "Promedio de los 4 jueces. Refleja el resultado final.</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    rh = st.session_state.get("run_history", [])
    if not rh:
        st.info(
            "Todavia no hay ejecuciones registradas. Ve a **Pipeline Multi-Agente**, "
            "ejecuta al menos dos veces (una con fallo, una sin fallo) para ver el contraste aqui."
        )
        return

    cols_m = ["grounded", "behavioral", "safety", "debate", "acuerdo", "global"]
    labels_m = ["Grounded", "Behavioral", "Safety", "Debate", "Acuerdo", "Global"]
    df_h = pd.DataFrame(rh).set_index("run")[cols_m]

    fig_h = go.Figure(
        go.Heatmap(
            z=df_h.values,
            x=labels_m,
            y=df_h.index.tolist(),
            colorscale="RdYlGn",
            zmin=0,
            zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in df_h.values],
            texttemplate="%{text}",
            hovertemplate="%{y} | %{x}: %{z:.2f}<extra></extra>",
        )
    )
    row_h = max(180, 80 + len(rh) * 50)
    fig_h.update_layout(
        title="Heatmap - verde = bueno, rojo = problema detectado",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        height=row_h,
        margin=dict(l=180, r=20, t=60, b=60),
    )
    st.plotly_chart(fig_h, use_container_width=True)

    if st.button("Limpiar historial", use_container_width=False):
        st.session_state["run_history"] = []
        st.rerun()

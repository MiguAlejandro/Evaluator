"""Tab 4: Chaos Engineering — inject failures and observe judge reactions."""

from __future__ import annotations

import random

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from eval_core.constants import CHAOS_TYPES


def render_tab_chaos(sidebar_cfg: dict):
    """Render the chaos engineering tab."""
    st.subheader("Chaos Engineering: inyectar fallos para entender la robustez")
    st.caption("Los mejores sistemas no son los que nunca fallan "
               "- son los que detectan y comunican el fallo claramente.")

    # ── Baseline: real if we have history, hardcoded otherwise ────────
    rh = st.session_state.get("run_history", [])
    last_correct = next((r for r in reversed(rh) if "Correcto" in r["run"]), None)

    jkeys = ["grounded", "behavioral", "safety", "debate"]
    jnames = ["Grounded", "Behavioral", "Safety", "Debate"]

    if last_correct:
        base_scores = {k: last_correct[k] for k in jkeys}
        baseline_label = f"Baseline: scores reales de **{last_correct['run']}**"
        baseline_color = "#22c55e"
    else:
        base_scores = {"grounded": 0.90, "behavioral": 0.90, "safety": 0.95, "debate": 0.90}
        baseline_label = "Baseline de referencia (ejecuta el pipeline para usar tus scores reales)"
        baseline_color = "#64748b"

    st.markdown(
        f'<div style="color:{baseline_color};font-size:.85rem;margin-bottom:8px">'
        f"{baseline_label}</div>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("**1. Selecciona el tipo de fallo:**")
        chaos_sel = st.radio("", list(CHAOS_TYPES.keys()), label_visibility="collapsed",
                             key="chaos_radio")
        info = CHAOS_TYPES[chaos_sel]

        st.markdown(
            f'<div class="card" style="border-color:{info["color"]}">'
            f'<b style="color:{info["color"]}">{chaos_sel}</b><br>'
            f'<span style="font-size:.85rem"><b>Que hace:</b> {info["desc"]}</span><br>'
            f'<span style="font-size:.82rem;color:#94a3b8">'
            f'<b>Modo de fallo:</b> {info["impact"]}</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown("**2. Severidad del fallo:**")
        severidad = st.select_slider(
            "",
            options=["Leve (x0.5)", "Moderado (x1.0)", "Severo (x1.5)"],
            value="Moderado (x1.0)",
            label_visibility="collapsed",
            key="chaos_sev",
        )
        sev_factor = {"Leve (x0.5)": 0.5, "Moderado (x1.0)": 1.0, "Severo (x1.5)": 1.5}[severidad]

        # Expected impact per judge
        st.markdown("**Impacto esperado por juez:**")
        for jk, jn in zip(jkeys, jnames):
            raw = info["deltas"][jk] * sev_factor
            arrow = "^" if raw > 0 else "v"
            clr = "#06b6d4" if raw > 0 and info["is_bias"] else ("#22c55e" if raw > 0 else "#ef4444")
            st.markdown(
                f'<span style="color:{clr};font-size:.85rem">{arrow} {jn}: {raw:+.2f}</span>',
                unsafe_allow_html=True,
            )

        inject_btn = st.button("Inyectar fallo y evaluar", type="primary", use_container_width=True)

    with col_b:
        if inject_btn:
            random.seed(42)
            scores_after = {
                k: min(1.0, max(0.0, base_scores[k] + info["deltas"][k] * sev_factor
                                + random.uniform(-0.03, 0.03)))
                for k in jkeys
            }
            avg_before = sum(base_scores[k] for k in jkeys) / 4
            avg_after = sum(scores_after[k] for k in jkeys) / 4

            # Bias warning
            if info["is_bias"]:
                st.warning(
                    "**Sesgo del juez**: los scores SUBIERON - el sistema da falsa sensacion "
                    "de seguridad. Este es el fallo mas dificil de detectar porque todo parece correcto."
                )

            st.markdown("**Comparacion: antes vs despues del fallo**")
            rows = []
            for jk, jn in zip(jkeys, jnames):
                b = base_scores[jk]
                a = scores_after[jk]
                d = a - b
                rows.append({
                    "Juez": jn,
                    "Sin fallo": f"{b:.0%}",
                    "Con fallo": f"{a:.0%}",
                    "Delta": f"{d:+.2f}",
                })
            rows.append({
                "Juez": "PROMEDIO",
                "Sin fallo": f"{avg_before:.0%}",
                "Con fallo": f"{avg_after:.0%}",
                "Delta": f"{avg_after - avg_before:+.2f}",
            })
            df_chaos = pd.DataFrame(rows)
            st.dataframe(df_chaos, use_container_width=True, hide_index=True)

            # Radar chart
            before_vals = [base_scores[k] for k in jkeys]
            after_vals = [scores_after[k] for k in jkeys]
            fig_ch = go.Figure()
            for vals, name, clr in [
                (before_vals, "Sin fallo", "#22c55e"),
                (after_vals, "Con fallo", info["color"]),
            ]:
                v2 = vals + [vals[0]]
                t2 = jnames + [jnames[0]]
                fig_ch.add_trace(
                    go.Scatterpolar(
                        r=v2, theta=t2, fill="toself",
                        name=name, line=dict(color=clr, width=2), opacity=0.8,
                    )
                )
            fig_ch.update_layout(
                polar=dict(
                    radialaxis=dict(range=[0, 1], color="#94a3b8"),
                    bgcolor="#1e293b",
                    angularaxis=dict(color="#94a3b8"),
                ),
                paper_bgcolor="#0f172a",
                font=dict(color="#e2e8f0"),
                legend=dict(font=dict(color="#e2e8f0")),
                height=280,
                margin=dict(l=40, r=40, t=30, b=10),
            )
            st.plotly_chart(fig_ch, use_container_width=True)

            drop = avg_before - avg_after
            c1, c2, c3 = st.columns(3)
            c1.metric("Score sin fallo", f"{avg_before:.0%}")
            if info["is_bias"]:
                c2.metric("Score con fallo (inflado)", f"{avg_after:.0%}",
                          delta=f"+{-drop:.0%} FALSO", delta_color="inverse")
                c3.metric("Peligrosidad", "Alta", delta="invisible al sistema", delta_color="off")
            else:
                c2.metric("Score con fallo", f"{avg_after:.0%}",
                          delta=f"{-drop:.0%}", delta_color="inverse")
                c3.metric(
                    "Deteccion",
                    "Visible" if abs(drop) > 0.2 else "Debil",
                    delta=f"caida de {drop:.0%}",
                    delta_color="off",
                )
        else:
            st.markdown(
                '<div class="card" style="border-color:#334155;color:#64748b">'
                "Selecciona un tipo de fallo, ajusta la severidad y presiona el boton "
                "para ver como reacciona cada juez.</div>",
                unsafe_allow_html=True,
            )

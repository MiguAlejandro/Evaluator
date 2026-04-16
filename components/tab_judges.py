"""Tab 2: Los 4 Jueces — detailed judge results."""

from __future__ import annotations

import streamlit as st

from components.styles import score_color


def render_tab_judges(sidebar_cfg: dict):
    """Render the judges detail tab."""
    umbral = sidebar_cfg["umbral"]

    st.subheader("LLM-as-a-Judge: 4 perspectivas sobre la misma respuesta")
    st.caption("Cada juez mira la respuesta desde un angulo diferente. Juntos son mucho mas robustos que uno solo.")

    # ── Judge explanations (always visible) ──────────────────────────
    st.markdown("#### Que hace cada juez?")
    ex_g, ex_b, ex_s, ex_d = st.columns(4)
    ex_g.markdown(
        '<div class="card" style="border-color:#3b82f6">'
        '<div style="color:#3b82f6;font-weight:bold">Grounded</div>'
        '<div style="font-size:.85rem;margin-top:6px">Cada dato que dijo el agente esta en los documentos?</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        "Busca afirmaciones sin respaldo o que contradigan la fuente vigente.</div></div>",
        unsafe_allow_html=True,
    )
    ex_b.markdown(
        '<div class="card" style="border-color:#a855f7">'
        '<div style="color:#a855f7;font-weight:bold">Behavioral</div>'
        '<div style="font-size:.85rem;margin-top:6px">Siguio el proceso correcto?</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        "Cito fuentes? Uso la version vigente? Omitio algo critico?</div></div>",
        unsafe_allow_html=True,
    )
    ex_s.markdown(
        '<div class="card" style="border-color:#ef4444">'
        '<div style="color:#ef4444;font-weight:bold">Safety</div>'
        '<div style="font-size:.85rem;margin-top:6px">Hay datos incorrectos que puedan causar dano?</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        "Compara numeros y plazos contra los docs. Si algo esta mal: BLOCK.</div></div>",
        unsafe_allow_html=True,
    )
    ex_d.markdown(
        '<div class="card" style="border-color:#eab308">'
        '<div style="color:#eab308;font-weight:bold">Debate</div>'
        '<div style="font-size:.85rem;margin-top:6px">Abogado del diablo</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        "Busca activamente en los docs algo que contradiga la respuesta.</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    if not st.session_state.get("pipeline_data"):
        st.info("Ejecuta el pipeline en la pestana anterior para ver los resultados de los jueces.")
        return

    e = st.session_state["pipeline_data"]["eval"]
    model_name = st.session_state["pipeline_data"].get("model_name", "")
    if model_name:
        st.caption(f"Resultados para: **{model_name}**")

    # ── Score cards ──────────────────────────────────────────────────
    col_g, col_b, col_s, col_d = st.columns(4)
    judges_display = [
        (col_g, "grounded", "Grounded", "Evidencia", "#3b82f6"),
        (col_b, "behavioral", "Behavioral", "Proceso", "#a855f7"),
        (col_s, "safety", "Safety", "Seguridad", "#ef4444"),
        (col_d, "debate", "Debate", "Adversarial", "#eab308"),
    ]
    for col, key, name, label, color in judges_display:
        score = e[key]["score"]
        sc = score_color(score, umbral)
        extra = e[key].get("action", e[key].get("verdict", ""))
        col.markdown(
            f'<div class="card" style="border-color:{sc};text-align:center">'
            f'<div style="color:#94a3b8;font-size:.8rem">{name}</div>'
            f'<div class="score" style="color:{sc}">{score:.0%}</div>'
            f'<div style="color:#94a3b8;font-size:.8rem">{label}</div>'
            f'<div style="color:{sc};font-size:.85rem;font-weight:bold">{extra}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Detailed expandables ─────────────────────────────────────────
    st.markdown("---")

    with st.expander("Grounded Judge - Claims verificados", expanded=True):
        for c in e["grounded"]["claims"]:
            vc = {"SUPPORTED": ":green[OK]", "CONTRADICTED": ":red[X]", "NOT_FOUND": ":orange[?]"}
            st.markdown(f"{vc.get(c['verdict'], '?')} **{c['claim']}** -> `{c['verdict']}`")
            st.caption(f"  {c['reason']}")

    with st.expander("Behavioral Judge - Proceso"):
        bscore = e["behavioral"]["score"]
        score_ok = bscore >= umbral * 0.7
        for f in e["behavioral"]["flags"]:
            text_ok = f.upper().startswith("OK")
            icon = "OK" if (text_ok and score_ok) else "!!"
            st.markdown(f"**{icon}** {f}")
        if not score_ok:
            st.caption(f"Score: {bscore:.0%} - por debajo del umbral ({umbral * 0.7:.0%})")

    with st.expander("Safety Judge - Riesgos"):
        st.markdown(f"**Accion:** {e['safety']['action']}")
        sscore = e["safety"]["score"]
        for issue in e["safety"]["issues"]:
            text_ok = issue.upper().startswith("OK")
            score_ok = sscore >= umbral * 0.7
            icon = "OK" if (text_ok and score_ok) else "!!"
            st.markdown(f"**{icon}** {issue}")

    with st.expander("Debate Judge - Contraejemplos"):
        st.markdown(f"**Veredicto:** {e['debate']['verdict']}")
        for f in e["debate"].get("finds") or ["Sin contraejemplos"]:
            st.markdown(f"- {f}")

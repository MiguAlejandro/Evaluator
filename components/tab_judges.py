"""Tab 2: Los 6 Jueces — detailed judge results (RAGAS-inspired)."""

from __future__ import annotations

import streamlit as st

from components.styles import score_color


def render_tab_judges(sidebar_cfg: dict):
    """Render the judges detail tab."""
    umbral = sidebar_cfg["umbral"]

    st.subheader("6 Jueces de Evaluacion (inspirado en RAGAS)")
    st.caption("Cada juez mira la respuesta desde un angulo diferente. 4 originales + 2 RAGAS.")

    # ── Judge explanations (always visible) ──────────────────────────
    st.markdown("#### Que hace cada juez?")

    row1 = st.columns(3)
    row1[0].markdown(
        '<div class="card" style="border-color:#3b82f6">'
        '<div style="color:#3b82f6;font-weight:bold">Faithfulness</div>'
        '<div style="font-size:.85rem;margin-top:6px">Cada dato esta respaldado por los documentos?</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        'RAGAS Faithfulness. Busca claims sin respaldo o que contradigan la fuente.</div></div>',
        unsafe_allow_html=True,
    )
    row1[1].markdown(
        '<div class="card" style="border-color:#a855f7">'
        '<div style="color:#a855f7;font-weight:bold">Behavioral</div>'
        '<div style="font-size:.85rem;margin-top:6px">Siguio el proceso correcto?</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        'Cito fuentes? Uso la version vigente? Omitio algo critico?</div></div>',
        unsafe_allow_html=True,
    )
    row1[2].markdown(
        '<div class="card" style="border-color:#ef4444">'
        '<div style="color:#ef4444;font-weight:bold">Safety</div>'
        '<div style="font-size:.85rem;margin-top:6px">Hay datos incorrectos que puedan causar dano?</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        'Compara numeros y plazos contra los docs. Si algo esta mal: BLOCK.</div></div>',
        unsafe_allow_html=True,
    )

    row2 = st.columns(3)
    row2[0].markdown(
        '<div class="card" style="border-color:#eab308">'
        '<div style="color:#eab308;font-weight:bold">Debate</div>'
        '<div style="font-size:.85rem;margin-top:6px">Abogado del diablo</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        'Busca activamente en los docs algo que contradiga la respuesta.</div></div>',
        unsafe_allow_html=True,
    )
    row2[1].markdown(
        '<div class="card" style="border-color:#06b6d4">'
        '<div style="color:#06b6d4;font-weight:bold">Relevancy</div>'
        '<div style="font-size:.85rem;margin-top:6px">La respuesta contesta la pregunta?</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        'RAGAS Answer Relevancy. Detecta si el modelo se fue por la tangente.</div></div>',
        unsafe_allow_html=True,
    )
    row2[2].markdown(
        '<div class="card" style="border-color:#10b981">'
        '<div style="color:#10b981;font-weight:bold">Correctness</div>'
        '<div style="font-size:.85rem;margin-top:6px">F1 vs respuesta de referencia</div>'
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:4px">'
        'RAGAS Answer Correctness. Compara TP/FP/FN contra la gold answer.</div></div>',
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
    judges_display = [
        ("grounded", "Faithfulness", "Evidencia", "#3b82f6"),
        ("behavioral", "Behavioral", "Proceso", "#a855f7"),
        ("safety", "Safety", "Seguridad", "#ef4444"),
        ("debate", "Debate", "Adversarial", "#eab308"),
        ("relevancy", "Relevancy", "Pertinencia", "#06b6d4"),
        ("correctness", "Correctness", "Precision F1", "#10b981"),
    ]

    cols = st.columns(6)
    for col, (key, name, label, color) in zip(cols, judges_display):
        score = e[key]["score"]
        sc = score_color(score, umbral)
        extra = e[key].get("action", e[key].get("verdict", e[key].get("classification", "")))
        col.markdown(
            f'<div class="card" style="border-color:{sc};text-align:center">'
            f'<div style="color:#94a3b8;font-size:.75rem">{name}</div>'
            f'<div class="score" style="color:{sc}">{score:.0%}</div>'
            f'<div style="color:#94a3b8;font-size:.75rem">{label}</div>'
            f'<div style="color:{sc};font-size:.8rem;font-weight:bold">{extra}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Detailed expandables ─────────────────────────────────────────
    st.markdown("---")

    with st.expander("Faithfulness - Claims verificados", expanded=True):
        for c in e["grounded"]["claims"]:
            vc = {"SUPPORTED": ":green[OK]", "CONTRADICTED": ":red[X]", "NOT_FOUND": ":orange[?]"}
            st.markdown(f"{vc.get(c['verdict'], '?')} **{c['claim']}** -> `{c['verdict']}`")
            st.caption(f"  {c['reason']}")

    with st.expander("Behavioral - Proceso"):
        bscore = e["behavioral"]["score"]
        for f in e["behavioral"]["flags"]:
            text_ok = f.upper().startswith("OK")
            icon = "OK" if text_ok else "!!"
            st.markdown(f"**{icon}** {f}")

    with st.expander("Safety - Riesgos"):
        st.markdown(f"**Accion:** {e['safety']['action']}")
        for issue in e["safety"]["issues"]:
            st.markdown(f"- {issue}")

    with st.expander("Debate - Contraejemplos"):
        st.markdown(f"**Veredicto:** {e['debate']['verdict']}")
        for f in e["debate"].get("finds") or ["Sin contraejemplos"]:
            st.markdown(f"- {f}")

    with st.expander("Relevancy - Pertinencia de la respuesta"):
        st.markdown(f"**Clasificacion:** {e['relevancy']['classification']}")
        st.markdown(f"**Razonamiento:** {e['relevancy']['reasoning']}")

    with st.expander("Correctness - Comparacion con referencia (F1)"):
        tp = e["correctness"].get("tp", [])
        fp = e["correctness"].get("fp", [])
        fn = e["correctness"].get("fn", [])
        if tp:
            st.markdown("**Aciertos (TP):**")
            for t in tp:
                st.markdown(f":green[+] {t}")
        if fp:
            st.markdown("**Inventados/Incorrectos (FP):**")
            for f in fp:
                st.markdown(f":red[-] {f}")
        if fn:
            st.markdown("**Omitidos (FN):**")
            for f in fn:
                st.markdown(f":orange[?] {f}")
        if not tp and not fp and not fn:
            st.caption("Sin datos de comparacion")

"""Tab 5: Chaos Engineering — inject REAL failures into the pipeline and evaluate."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from eval_core.constants import KB_DEMO, BENCHMARK_QUESTIONS
from eval_core.models import ModelConfig, pipeline_result_to_records
from components.styles import score_color
from llms.base import create_llm
from agents.pipeline import EvalPipeline


# ── Chaos injection functions ────────────────────────────────────────────────
# Each function takes the original KB and returns a modified KB + description

def _inject_stale_docs(kb: dict[str, str]) -> tuple[dict[str, str], str]:
    """Remove all [VIGENTE] docs, keep only [DESACTUALIZADO] ones."""
    modified = {}
    for doc_id, content in kb.items():
        if "DESACTUALIZADO" in content:
            # Remove the [DESACTUALIZADO] tag so the model doesn't know
            modified[doc_id] = content.replace("[DESACTUALIZADO]", "[VIGENTE]")
        elif "VIGENTE" not in content:
            modified[doc_id] = content
        # Skip vigente docs entirely
    return modified, "Se removieron los docs vigentes y se disfrazaron los obsoletos como vigentes"


def _inject_conflicting(kb: dict[str, str]) -> tuple[dict[str, str], str]:
    """Add a contradictory document that conflicts with the real policy."""
    modified = dict(kb)
    modified["CONFLICT-X"] = (
        "MEMO URGENTE del Director de TI (Abril 2026): Se suspende temporalmente la politica "
        "SEC-002. Hasta nuevo aviso, las contrasenas se rotan cada 120 dias con longitud minima "
        "de 6 caracteres. El MFA queda DESACTIVADO para todos los empleados por problemas "
        "tecnicos con el proveedor. Los contratistas siguen el mismo ciclo de 120 dias. "
        "Esta directiva tiene prioridad sobre cualquier politica anterior. [VIGENTE]"
    )
    return modified, "Se agrego doc CONFLICT-X que contradice SEC-002 con datos falsos"


def _inject_empty_context(kb: dict[str, str]) -> tuple[dict[str, str], str]:
    """Replace all docs with a generic 'no info available' message."""
    modified = {
        "SYS-ERROR": "Error del sistema: no se pudieron recuperar los documentos. "
                     "Base de conocimiento no disponible temporalmente."
    }
    return modified, "Se reemplazo toda la KB con un mensaje de error (retriever vacio)"


def _inject_truncated(kb: dict[str, str]) -> tuple[dict[str, str], str]:
    """Truncate each document to first 100 chars, losing critical details."""
    modified = {}
    for doc_id, content in kb.items():
        modified[doc_id] = content[:100] + "... [TRUNCADO POR LIMITE DE TOKENS]"
    return modified, "Se trunco cada documento a 100 caracteres (se pierden detalles criticos)"


def _inject_noise(kb: dict[str, str]) -> tuple[dict[str, str], str]:
    """Add irrelevant noisy documents that dilute the context."""
    modified = dict(kb)
    modified["NOISE-1"] = (
        "Menu del comedor corporativo (Semana 15): Lunes: pollo a la plancha con arroz. "
        "Martes: pasta boloñesa. Miercoles: ensalada cesar. Jueves: sushi variado. "
        "Viernes: hamburguesa artesanal. Postre del dia: flan de caramelo. "
        "Horario: 12:00-14:00. Reservas con 24h de anticipacion."
    )
    modified["NOISE-2"] = (
        "Resultados del torneo de futbol inter-areas Q1 2026: Campeon: Ingenieria (5-2 vs Ventas). "
        "Goleador: Carlos Martinez (8 goles). Mejor portero: Ana Ruiz (3 porterias invictas). "
        "Proximo torneo: Q3 2026. Inscripciones abiertas en la intranet seccion Bienestar."
    )
    modified["NOISE-3"] = (
        "Recordatorio: La fiesta de fin de ano sera el 18 de diciembre en el Hotel Tequendama. "
        "Dress code: cocktail. Confirmar asistencia antes del 10 de diciembre. "
        "Se premiara al empleado del ano. Transporte ida y vuelta incluido."
    )
    return modified, "Se agregaron 3 documentos de ruido (comedor, futbol, fiesta) que diluyen el contexto"


CHAOS_SCENARIOS = {
    "Documento obsoleto": {
        "desc": "Se remueven los documentos vigentes y se disfrazan los obsoletos como vigentes. "
                "El modelo solo tiene acceso a informacion desactualizada.",
        "inject_fn": _inject_stale_docs,
        "color": "#f97316",
    },
    "Fuentes conflictivas": {
        "desc": "Se agrega un memo falso que contradice la politica real con datos inventados. "
                "El modelo debe decidir cual fuente es correcta.",
        "inject_fn": _inject_conflicting,
        "color": "#a855f7",
    },
    "Retriever vacio": {
        "desc": "Se simula un fallo del retriever: la KB completa se reemplaza por un mensaje de error. "
                "El modelo no tiene documentos para responder.",
        "inject_fn": _inject_empty_context,
        "color": "#ef4444",
    },
    "Contexto truncado": {
        "desc": "Cada documento se corta a 100 caracteres, perdiendo detalles numericos, "
                "excepciones y referencias cruzadas criticas.",
        "inject_fn": _inject_truncated,
        "color": "#eab308",
    },
    "Ruido en el contexto": {
        "desc": "Se agregan 3 documentos completamente irrelevantes (menu, futbol, fiesta) "
                "que diluyen el contexto y pueden confundir al modelo.",
        "inject_fn": _inject_noise,
        "color": "#06b6d4",
    },
}


def render_tab_chaos(sidebar_cfg: dict):
    """Render the chaos engineering tab with REAL failure injection."""
    model_configs: list[ModelConfig] = sidebar_cfg["model_configs"]
    umbral: float = sidebar_cfg["umbral"]

    st.subheader("Chaos Engineering: inyeccion REAL de fallos")
    st.caption(
        "Inyecta fallos reales en la KB y ejecuta el pipeline completo. "
        "Los 6 jueces evaluan la respuesta del modelo bajo condiciones adversas."
    )

    if not model_configs:
        st.info("Configura al menos **1 modelo** en el sidebar para usar Chaos Engineering.")
        return

    # ── Scenario selection ───────────────────────────────────────────
    col_config, col_results = st.columns([1, 1])

    with col_config:
        st.markdown("**1. Selecciona el tipo de fallo:**")
        chaos_sel = st.radio(
            "", list(CHAOS_SCENARIOS.keys()),
            label_visibility="collapsed", key="chaos_radio",
        )
        scenario = CHAOS_SCENARIOS[chaos_sel]

        st.markdown(
            f'<div class="card" style="border-color:{scenario["color"]}">'
            f'<b style="color:{scenario["color"]}">{chaos_sel}</b><br>'
            f'<span style="font-size:.85rem">{scenario["desc"]}</span></div>',
            unsafe_allow_html=True,
        )

        # Question selection
        st.markdown("**2. Pregunta de prueba:**")
        q_options = [f"[{q['id']}] {q['pregunta'][:70]}" for q in BENCHMARK_QUESTIONS[:5]]
        q_sel = st.selectbox("", q_options, key="chaos_q", label_visibility="collapsed")
        q_idx = q_options.index(q_sel)
        q_data = BENCHMARK_QUESTIONS[q_idx]

        # Model selection
        st.markdown("**3. Modelo:**")
        model_names = [c.name for c in model_configs]
        model_sel = st.selectbox("", model_names, key="chaos_model", label_visibility="collapsed")

        # Preview injected KB
        with st.expander("Ver KB modificada (preview)"):
            injected_kb, inject_desc = scenario["inject_fn"](KB_DEMO)
            st.caption(inject_desc)
            for doc_id, content in injected_kb.items():
                st.markdown(f"**{doc_id}:** {content[:150]}...")

        inject_btn = st.button(
            "Inyectar fallo y ejecutar pipeline REAL",
            type="primary", use_container_width=True,
        )

    with col_results:
        if "chaos_results" not in st.session_state:
            st.session_state["chaos_results"] = None

        if inject_btn:
            cfg = next(c for c in model_configs if c.name == model_sel)
            oai_key = sidebar_cfg.get("openai_api_key", "")
            pipeline = EvalPipeline(openai_api_key=oai_key)

            try:
                llm = create_llm(cfg)
            except Exception as e:
                st.error(f"Error creando LLM: {e}")
                return

            injected_kb, inject_desc = scenario["inject_fn"](KB_DEMO)

            with st.status("Ejecutando chaos test...", expanded=True) as status:
                # Run 1: Normal (healthy)
                st.write("Ejecutando pipeline NORMAL (KB sana)...")
                result_normal = pipeline.run(
                    KB_DEMO, q_data["pregunta"], llm,
                    expected_answer=q_data.get("respuesta_esperada", ""),
                )

                # Run 2: With injected failure
                st.write(f"Ejecutando pipeline con FALLO ({chaos_sel})...")
                result_chaos = pipeline.run(
                    injected_kb, q_data["pregunta"], llm,
                    expected_answer=q_data.get("respuesta_esperada", ""),
                )

                status.update(label="Chaos test completo", state="complete")

            st.session_state["chaos_results"] = {
                "normal": result_normal,
                "chaos": result_chaos,
                "scenario": chaos_sel,
                "question": q_data,
                "inject_desc": inject_desc,
                "color": scenario["color"],
            }

            # Save both runs to benchmark history
            if "benchmark_history" not in st.session_state:
                st.session_state["benchmark_history"] = []

            from datetime import datetime
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            record_normal = pipeline_result_to_records(
                result_normal,
                question_id=q_data["id"],
                question_level=q_data["nivel"],
                question_category=q_data.get("categoria", ""),
                timestamp=ts,
                source="chaos-normal",
            )
            record_chaos = pipeline_result_to_records(
                result_chaos,
                question_id=q_data["id"],
                question_level=q_data["nivel"],
                question_category=q_data.get("categoria", ""),
                timestamp=ts,
                source=f"chaos-{chaos_sel}",
            )
            st.session_state["benchmark_history"].extend([record_normal, record_chaos])
            st.success("2 registros guardados en el historial (normal + con fallo)")

        # ── Display results ──────────────────────────────────────────
        data = st.session_state.get("chaos_results")
        if not data:
            st.markdown(
                '<div class="card" style="border-color:#334155;color:#64748b">'
                "Selecciona un escenario, pregunta y modelo, luego presiona el boton "
                "para ejecutar el pipeline con y sin fallo.</div>",
                unsafe_allow_html=True,
            )
            return

        r_normal = data["normal"]
        r_chaos = data["chaos"]
        e_normal = r_normal.eval_result
        e_chaos = r_chaos.eval_result

        jkeys = ["grounded", "behavioral", "safety", "debate", "relevancy", "correctness"]
        jnames = ["Faithfulness", "Behavioral", "Safety", "Debate", "Relevancy", "Correctness"]

        scores_normal = e_normal.scores
        scores_chaos = e_chaos.scores

        # ── Comparison table ─────────────────────────────────────────
        st.markdown(f"**Escenario: {data['scenario']}**")
        st.caption(data["inject_desc"])

        rows = []
        for jk, jn in zip(jkeys, jnames):
            b = scores_normal[jk]
            a = scores_chaos[jk]
            d = a - b
            rows.append({
                "Juez": jn,
                "Normal": f"{b:.0%}",
                "Con fallo": f"{a:.0%}",
                "Delta": f"{d:+.2f}",
            })
        avg_n = e_normal.average_score
        avg_c = e_chaos.average_score
        rows.append({
            "Juez": "PROMEDIO",
            "Normal": f"{avg_n:.0%}",
            "Con fallo": f"{avg_c:.0%}",
            "Delta": f"{avg_c - avg_n:+.2f}",
        })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ── Radar chart ──────────────────────────────────────────────
        fig_ch = go.Figure()
        for vals, name, clr in [
            ([scores_normal[k] for k in jkeys], "Normal", "#22c55e"),
            ([scores_chaos[k] for k in jkeys], "Con fallo", data["color"]),
        ]:
            v2 = vals + [vals[0]]
            t2 = jnames + [jnames[0]]
            fig_ch.add_trace(go.Scatterpolar(
                r=v2, theta=t2, fill="toself",
                name=name, line=dict(color=clr, width=2), opacity=0.8,
            ))
        fig_ch.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 1], color="#94a3b8"),
                bgcolor="#1e293b", angularaxis=dict(color="#94a3b8"),
            ),
            paper_bgcolor="#0f172a", font=dict(color="#e2e8f0"),
            legend=dict(font=dict(color="#e2e8f0")),
            height=300, margin=dict(l=50, r=50, t=20, b=20),
        )
        st.plotly_chart(fig_ch, use_container_width=True)

        # ── Metrics ──────────────────────────────────────────────────
        drop = avg_n - avg_c
        c1, c2, c3 = st.columns(3)
        c1.metric("Score normal", f"{avg_n:.0%}")
        c2.metric("Score con fallo", f"{avg_c:.0%}",
                  delta=f"{-drop:.0%}", delta_color="inverse")
        c3.metric(
            "Deteccion",
            "Clara" if abs(drop) > 0.2 else ("Moderada" if abs(drop) > 0.1 else "Debil"),
            delta=f"caida de {drop:.0%}",
            delta_color="off",
        )

        # ── Responses side by side ───────────────────────────────────
        st.markdown("---")
        st.markdown("#### Respuestas del modelo")

        resp_a, resp_b = st.columns(2)
        with resp_a:
            st.markdown(
                '<div class="card" style="border-color:#22c55e">'
                '<b style="color:#22c55e">Respuesta NORMAL</b><br><br>'
                f'<span style="font-family:monospace;font-size:.85rem">'
                f'{r_normal.respuesta.replace(chr(10), "<br>")}</span></div>',
                unsafe_allow_html=True,
            )
        with resp_b:
            st.markdown(
                f'<div class="card" style="border-color:{data["color"]}">'
                f'<b style="color:{data["color"]}">Respuesta CON FALLO</b><br><br>'
                f'<span style="font-family:monospace;font-size:.85rem">'
                f'{r_chaos.respuesta.replace(chr(10), "<br>")}</span></div>',
                unsafe_allow_html=True,
            )

        # ── Expected answer reference ────────────────────────────────
        expected = data["question"].get("respuesta_esperada", "")
        if expected:
            with st.expander("Ver respuesta esperada (referencia)"):
                st.caption(expected)

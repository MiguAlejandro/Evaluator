"""Tab 1: Pipeline Multi-Agente — from document to evaluated response."""

from __future__ import annotations

import time

import streamlit as st

from eval_core.constants import KB_DEMO, PREGUNTA_DEMO, BENCHMARK_QUESTIONS
from eval_core.models import ModelConfig, pipeline_result_to_records
from components.styles import score_color, verdict_label
from llms.base import create_llm
from agents.pipeline import EvalPipeline, kb_to_str
from rag import NaiveRAG


def _build_kb(uploaded_files) -> dict[str, str]:
    """Build a KB dict from uploaded files or fall back to demo."""
    if not uploaded_files:
        return KB_DEMO
    kb = {}
    for i, f in enumerate(uploaded_files):
        content = f.read().decode("utf-8", errors="ignore")
        kb[f"DOC-{chr(65 + i)}"] = content[:2000]
    return kb


# Build question labels for selectbox
_QUESTION_OPTIONS = [
    f"[{q['id']}] {q['nivel']} | {q['pregunta'][:70]}..."
    if len(q["pregunta"]) > 70
    else f"[{q['id']}] {q['nivel']} | {q['pregunta']}"
    for q in BENCHMARK_QUESTIONS
]
_QUESTION_OPTIONS.insert(0, "-- Escribir pregunta libre --")


def render_tab_pipeline(sidebar_cfg: dict):
    """Render the pipeline tab."""
    st.subheader("Pipeline Multi-Agente: del documento a la respuesta")
    st.caption("Tres agentes en cadena. El primero lee, el segundo responde, el tercero evalua.")

    model_configs: list[ModelConfig] = sidebar_cfg["model_configs"]
    simulate_failure: bool = sidebar_cfg["simulate_failure"]
    umbral: float = sidebar_cfg["umbral"]
    use_rag: bool = sidebar_cfg["use_rag"]

    col_in, col_out = st.columns([1, 1])

    with col_in:
        st.markdown("**1. Documentos** (KB demo o sube los tuyos)")
        uploaded = st.file_uploader(
            "Arrastra archivos .txt o .md",
            accept_multiple_files=True,
            type=["txt", "md"],
        )
        kb = _build_kb(uploaded)

        if not uploaded:
            st.info(f"KB demo: {len(KB_DEMO)} documentos de TechCorp (seguridad, acceso, datos, teletrabajo)")
            with st.expander("Ver documentos demo"):
                for k, v in KB_DEMO.items():
                    if "DESACTUALIZADO" in v:
                        color = "red"
                    elif "VIGENTE" in v:
                        color = "green"
                    else:
                        color = "gray"
                    st.markdown(f"**:{color}[{k}]:** {v}")

        # ── Question selection ───────────────────────────────────────
        st.markdown("**2. Pregunta**")
        q_sel = st.selectbox(
            "Selecciona del benchmark o escribe tu propia pregunta:",
            _QUESTION_OPTIONS,
            key="pipeline_q_sel",
        )

        if q_sel == "-- Escribir pregunta libre --":
            pregunta = st.text_input("Pregunta libre:", value="", key="pipeline_pregunta_libre")
        else:
            # Find the selected question
            q_idx = _QUESTION_OPTIONS.index(q_sel) - 1  # -1 because of "libre" option
            q_data = BENCHMARK_QUESTIONS[q_idx]
            pregunta = q_data["pregunta"]

            # Show question metadata
            nivel_colors = {
                "Basico": "#22c55e", "Intermedio": "#eab308",
                "Avanzado": "#f97316", "Experto": "#ef4444",
            }
            nc = nivel_colors.get(q_data["nivel"], "#94a3b8")
            st.markdown(
                f'<div class="card" style="border-color:{nc};padding:10px">'
                f'<span style="color:{nc};font-weight:bold">{q_data["nivel"]}</span>'
                f' | <span style="color:#94a3b8">{q_data["categoria"]}</span>'
                f'<br><span style="color:#64748b;font-size:.8rem">'
                f'Docs clave: {q_data["doc_clave"]}</span></div>',
                unsafe_allow_html=True,
            )

            with st.expander("Ver respuesta esperada (referencia)"):
                st.caption(q_data["respuesta_esperada"])

        # Model selector
        if model_configs:
            model_names = [c.name for c in model_configs]
            selected_model = st.selectbox(
                "Modelo para el pipeline",
                model_names,
                key="pipeline_model",
            )
        else:
            selected_model = None

        if "pipeline_data" not in st.session_state:
            st.session_state["pipeline_data"] = None
        if "run_history" not in st.session_state:
            st.session_state["run_history"] = []

        if st.button("Ejecutar Pipeline", type="primary", use_container_width=True):
            if not pregunta:
                st.warning("Escribe una pregunta")
            else:
                llm = None
                if selected_model and model_configs:
                    cfg = next(c for c in model_configs if c.name == selected_model)
                    try:
                        llm = create_llm(cfg)
                    except Exception as e:
                        st.error(f"Error creando LLM: {e}")

                oai_key = sidebar_cfg.get("openai_api_key", "")
                pipeline = EvalPipeline(openai_api_key=oai_key)

                # Optional RAG ingest
                if use_rag and kb and oai_key:
                    with st.status("Indexando documentos con OpenAI Embeddings...", expanded=False):
                        rag = NaiveRAG(openai_api_key=oai_key)
                        n_chunks = rag.ingest(kb)
                        st.write(f"Indexados {n_chunks} chunks")
                        st.session_state["rag_instance"] = rag

                with st.status("Ejecutando pipeline multi-agente...", expanded=True) as status:
                    st.write("Agente 1 - Analista: leyendo documentos...")
                    time.sleep(0.3)
                    # Get expected answer if from benchmark
                    exp_answer = ""
                    if q_sel != "-- Escribir pregunta libre --":
                        q_idx_run = _QUESTION_OPTIONS.index(q_sel) - 1
                        exp_answer = BENCHMARK_QUESTIONS[q_idx_run].get("respuesta_esperada", "")

                    result = pipeline.run(kb, pregunta, llm,
                                          force_failure=simulate_failure,
                                          expected_answer=exp_answer)
                    st.write("Analista listo")
                    st.write("Redactor listo")
                    st.write("Juez listo")
                    status.update(label="Pipeline completo", state="complete")

                eval_dict = result.eval_result.to_legacy_dict()
                st.session_state["pipeline_data"] = {
                    "kb": kb,
                    "pregunta": pregunta,
                    "extraccion": result.extraccion,
                    "respuesta": result.respuesta,
                    "eval": eval_dict,
                    "failure": simulate_failure,
                    "model_name": result.model_name,
                    "latencia": result.latencia_s,
                }

                # Save to benchmark history
                if "benchmark_history" not in st.session_state:
                    st.session_state["benchmark_history"] = []

                # Determine question metadata if from benchmark
                q_id = "PIPE"
                q_level = "Pipeline"
                q_cat = ""
                if q_sel != "-- Escribir pregunta libre --":
                    q_idx = _QUESTION_OPTIONS.index(q_sel) - 1
                    q_data = BENCHMARK_QUESTIONS[q_idx]
                    q_id = q_data["id"]
                    q_level = q_data["nivel"]
                    q_cat = q_data.get("categoria", "")

                record = pipeline_result_to_records(
                    result,
                    question_id=q_id,
                    question_level=q_level,
                    question_category=q_cat,
                )
                st.session_state["benchmark_history"].append(record)

    with col_out:
        st.markdown("**3. Respuesta generada**")
        if st.session_state["pipeline_data"]:
            d = st.session_state["pipeline_data"]
            is_fail = d["failure"]
            color_card = "#ef4444" if is_fail else "#22c55e"
            label_card = "Con fallo silencioso" if is_fail else "Respuesta correcta"
            model_tag = f" | Modelo: {d.get('model_name', 'demo')}"

            st.markdown(
                f'<div class="card" style="border-color:{color_card}">'
                f'<b style="color:{color_card}">{label_card}{model_tag}</b><br><br>'
                f'<span style="font-family:monospace">'
                f'{d["respuesta"].replace(chr(10), "<br>")}'
                f"</span></div>",
                unsafe_allow_html=True,
            )

            st.markdown("**Documentos citados en la respuesta:**")
            docs_citados = [k for k in d["kb"] if k in d["respuesta"]]
            if docs_citados:
                cols = st.columns(min(len(docs_citados), 4))
                for i, did in enumerate(docs_citados):
                    txt = d["kb"][did]
                    col_idx = i % len(cols)
                    if "DESACTUALIZADO" in txt:
                        c = "DESACTUALIZADO"
                    elif "VIGENTE" in txt:
                        c = "VIGENTE"
                    else:
                        c = ""
                    cols[col_idx].markdown(f"**{c}**")
                    cols[col_idx].caption(f"**{did}**: {txt[:60]}...")
            else:
                st.caption("El agente no cito documentos explicitamente")

            e = d["eval"]
            avg = sum(
                e[k]["score"] for k in ["grounded", "behavioral", "safety", "debate"]
            ) / 4
            vlabel, vcolor = verdict_label(avg, umbral)
            latencia_str = f" | {d.get('latencia', 0):.1f}s" if d.get("latencia") else ""

            st.markdown(
                f'<div class="card" style="border-color:{vcolor}">'
                f"<b>Score promedio del consejo de jueces:</b>"
                f'<span class="score" style="color:{vcolor}"> {avg:.0%}</span>'
                f'<span style="color:{vcolor};font-size:1rem;font-weight:bold;margin-left:12px">'
                f"{vlabel}</span>"
                f'<div style="color:#64748b;font-size:.75rem;margin-top:4px">'
                f"Umbral: {umbral:.0%}{latencia_str}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.caption("-> Ve a la pestana **Los 4 Jueces** para el detalle completo")
        else:
            st.markdown(
                '<div class="card" style="border-color:#334155;color:#64748b">'
                "Ejecuta el pipeline para ver la respuesta aqui.</div>",
                unsafe_allow_html=True,
            )

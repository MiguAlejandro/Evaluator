"""Tab 1: Pipeline Multi-Agente — from document to evaluated response."""

from __future__ import annotations

import time

import streamlit as st

from core.constants import KB_DEMO, PREGUNTA_DEMO
from core.models import ModelConfig
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
        kb[f"DOC-{chr(65 + i)}"] = content[:800]
    return kb


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
        st.markdown("**1. Sube tus documentos** (o usa la demo)")
        uploaded = st.file_uploader(
            "Arrastra archivos .txt o .md",
            accept_multiple_files=True,
            type=["txt", "md"],
        )
        kb = _build_kb(uploaded)

        if not uploaded:
            st.info("Usando KB demo: politica de contrasenas (incluye version vieja + vigente)")
            with st.expander("Ver documentos demo"):
                for k, v in KB_DEMO.items():
                    if "DESACTUALIZADO" in v:
                        color = "red"
                    elif "VIGENTE" in v:
                        color = "green"
                    else:
                        color = "gray"
                    st.markdown(f"**:{color}[{k}]:** {v}")

        st.markdown("**2. Pregunta del usuario**")
        pregunta = st.text_input("", value=PREGUNTA_DEMO, key="pipeline_pregunta")

        # Model selector for pipeline
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
                # Resolve LLM
                llm = None
                if selected_model and model_configs:
                    cfg = next(c for c in model_configs if c.name == selected_model)
                    try:
                        llm = create_llm(cfg)
                    except Exception as e:
                        st.error(f"Error creando LLM: {e}")

                oai_key = sidebar_cfg.get("openai_api_key", "")
                pipeline = EvalPipeline(openai_api_key=oai_key)
                kb_str = kb_to_str(kb)

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
                    result = pipeline.run(kb, pregunta, llm,
                                          force_failure=simulate_failure)
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

                # Save to history
                sv = [eval_dict[k]["score"] for k in ["grounded", "behavioral", "safety", "debate"]]
                run_n = len(st.session_state["run_history"]) + 1
                fail_label = "Fallo" if simulate_failure else "Correcto"
                st.session_state["run_history"].append({
                    "run": f"Run {run_n} {fail_label} ({result.model_name})",
                    "grounded": sv[0],
                    "behavioral": sv[1],
                    "safety": sv[2],
                    "debate": sv[3],
                    "acuerdo": max(0.0, 1.0 - (max(sv) - min(sv))),
                    "global": sum(sv) / 4,
                })
                st.session_state["run_history"] = st.session_state["run_history"][-6:]

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
                cols = st.columns(len(docs_citados))
                for i, did in enumerate(docs_citados):
                    txt = d["kb"][did]
                    if "DESACTUALIZADO" in txt:
                        c = "DESACTUALIZADO"
                    elif "VIGENTE" in txt:
                        c = "VIGENTE"
                    else:
                        c = ""
                    cols[i].markdown(f"**{c}**")
                    cols[i].caption(f"**{did}**: {txt[:60]}...")
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

"""
Multi-Model LLM Evaluation Tool
================================
Herramienta modular para evaluar y comparar multiples modelos LLM
usando un pipeline multi-agente con 6 jueces (inspirado en RAGAS).

Run: streamlit run app.py
"""

import os
import sys

# ── Path setup for Streamlit Cloud ──────────────────────────────────────────
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)
os.chdir(_this_dir)

import streamlit as st

from components.styles import inject_css
from components.sidebar import render_sidebar
from components.tab_pipeline import render_tab_pipeline
from components.tab_judges import render_tab_judges
from components.tab_benchmark import render_tab_benchmark
from components.tab_results import render_tab_results
from components.tab_chaos import render_tab_chaos
from components.tab_metrics_guide import render_tab_metrics_guide

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Multi-Model Eval", page_icon="", layout="wide")
inject_css()

# ── Sidebar ─────────────────────────────────────────────────────────────────
sidebar_cfg = render_sidebar()

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Pipeline",
    "6 Jueces",
    "Benchmark",
    "Resultados & CSV",
    "Chaos Engineering",
    "Metricas Explicadas",
])

with tab1:
    render_tab_pipeline(sidebar_cfg)

with tab2:
    render_tab_judges(sidebar_cfg)

with tab3:
    render_tab_benchmark(sidebar_cfg)

with tab4:
    render_tab_results(sidebar_cfg)

with tab5:
    render_tab_chaos(sidebar_cfg)

with tab6:
    render_tab_metrics_guide(sidebar_cfg)

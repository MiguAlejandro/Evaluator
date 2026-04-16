"""
Multi-Model LLM Evaluation Tool
================================
Herramienta modular para evaluar y comparar multiples modelos LLM
usando un pipeline multi-agente con 4 jueces LLM-as-a-Judge.

Run: streamlit run app.py
"""

import os
import sys

# ── Path setup for Streamlit Cloud ──────────────────────────────────────────
# Streamlit Cloud may run from a different working directory.
# Ensure this file's directory is on sys.path AND is the cwd.
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

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Multi-Model Eval", page_icon="", layout="wide")
inject_css()

# ── Sidebar ─────────────────────────────────────────────────────────────────
sidebar_cfg = render_sidebar()

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Pipeline Multi-Agente",
    "Los 4 Jueces",
    "Benchmark Estandar",
    "Resultados & Historial",
    "Chaos Engineering",
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

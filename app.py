"""
Multi-Model LLM Evaluation Tool
================================
Herramienta modular para evaluar y comparar multiples modelos LLM
usando un pipeline multi-agente con 4 jueces LLM-as-a-Judge.

Run: streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure the evaluacion package root is on sys.path so that
# `from core.models import ...` etc. work when running via
# `streamlit run evaluacion/app.py` from the parent directory.
_pkg_root = str(Path(__file__).resolve().parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

import streamlit as st

from components.styles import inject_css
from components.sidebar import render_sidebar
from components.tab_pipeline import render_tab_pipeline
from components.tab_judges import render_tab_judges
from components.tab_metrics import render_tab_metrics
from components.tab_chaos import render_tab_chaos
from components.tab_comparison import render_tab_comparison

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Multi-Model Eval", page_icon="", layout="wide")
inject_css()

# ── Sidebar ─────────────────────────────────────────────────────────────────
sidebar_cfg = render_sidebar()

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Pipeline Multi-Agente",
    "Los 4 Jueces",
    "Metricas de Coordinacion",
    "Chaos Engineering",
    "Comparacion Multi-Modelo",
])

with tab1:
    render_tab_pipeline(sidebar_cfg)

with tab2:
    render_tab_judges(sidebar_cfg)

with tab3:
    render_tab_metrics(sidebar_cfg)

with tab4:
    render_tab_chaos(sidebar_cfg)

with tab5:
    render_tab_comparison(sidebar_cfg)

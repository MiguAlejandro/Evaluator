"""CSS styles and UI helper functions."""

import streamlit as st

APP_CSS = """
<style>
body,.stApp{background:#0f172a;color:#e2e8f0}
.stSidebar{background:#1e293b}
.card{background:#1e293b;border-radius:10px;padding:16px;margin:8px 0;border-left:4px solid}
.score{font-size:2.2rem;font-weight:bold}
h1,h2,h3,h4{color:#e2e8f0!important}
div[data-testid="stMarkdownContainer"] p{color:#e2e8f0}
</style>
"""


def inject_css():
    """Inject the app CSS into the Streamlit page."""
    st.markdown(APP_CSS, unsafe_allow_html=True)


def score_color(score: float, umbral: float) -> str:
    """Green if >= umbral, yellow if >= 70% of umbral, red otherwise."""
    if score >= umbral:
        return "#22c55e"
    elif score >= umbral * 0.7:
        return "#eab308"
    else:
        return "#ef4444"


def verdict_label(avg: float, umbral: float) -> tuple[str, str]:
    """Return (label, color) based on average score vs threshold."""
    if avg >= umbral:
        return "PASS", "#22c55e"
    elif avg >= umbral * 0.7:
        return "WARN", "#eab308"
    else:
        return "FAIL", "#ef4444"


def render_card(content: str, border_color: str = "#334155"):
    """Render a styled card with HTML."""
    st.markdown(
        f'<div class="card" style="border-color:{border_color}">{content}</div>',
        unsafe_allow_html=True,
    )

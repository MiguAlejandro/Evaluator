"""Tab 6: Metricas Explicadas — pedagogical guide to evaluation metrics."""

from __future__ import annotations

import streamlit as st


def render_tab_metrics_guide(sidebar_cfg: dict):
    """Render the metrics explanation guide tab."""
    st.subheader("Guia de Metricas de Evaluacion")
    st.caption("Basado en el framework RAGAS (Retrieval Augmented Generation Assessment).")

    # ── Overview ─────────────────────────────────────────────────────
    st.markdown("#### Los 6 Jueces y sus Metricas")
    st.markdown(
        "Cada respuesta del modelo es evaluada por **6 jueces independientes**, "
        "todos ejecutados por el mismo modelo (OpenAI gpt-4o-mini) para garantizar consistencia."
    )

    # ── Metric cards ─────────────────────────────────────────────────
    st.markdown("---")

    # Row 1: Original 4 judges
    st.markdown("##### Jueces Originales")
    c1, c2 = st.columns(2)

    c1.markdown(
        '<div class="card" style="border-color:#3b82f6">'
        '<div style="color:#3b82f6;font-weight:bold;font-size:1.1rem">1. Faithfulness (Fidelidad)</div>'
        '<div style="font-size:.9rem;margin-top:8px"><b>RAGAS equivalente:</b> Faithfulness</div>'
        '<div style="font-size:.85rem;margin-top:6px">'
        '<b>Que mide:</b> Cada afirmacion factual de la respuesta tiene respaldo en los documentos?<br>'
        '<b>Como funciona:</b> Extrae todos los claims de la respuesta y verifica uno por uno contra los docs.<br>'
        '<b>Veredictos por claim:</b> SUPPORTED (respaldado), CONTRADICTED (contradice), NOT_FOUND (sin evidencia).<br>'
        '<b>Score:</b> Fraccion de claims SUPPORTED sobre el total.'
        '</div>'
        '<div style="color:#94a3b8;font-size:.8rem;margin-top:6px">'
        'Ejemplo de fallo: "Las contrasenas se rotan cada 90 dias" cuando el doc vigente dice 60.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    c2.markdown(
        '<div class="card" style="border-color:#a855f7">'
        '<div style="color:#a855f7;font-weight:bold;font-size:1.1rem">2. Behavioral (Proceso)</div>'
        '<div style="font-size:.9rem;margin-top:8px"><b>Tipo:</b> Process compliance</div>'
        '<div style="font-size:.85rem;margin-top:6px">'
        '<b>Que mide:</b> El agente siguio el proceso correcto?<br>'
        '<b>Verifica:</b> Cito documentos? Uso la version vigente? Omitio info critica?<br>'
        '<b>Flags:</b> STALE_DOCUMENT (cito doc viejo), INCOMPLETE (omitio datos clave).<br>'
        '<b>Score:</b> 1.0 si todo correcto, -0.3 por cada flag real.'
        '</div>'
        '<div style="color:#94a3b8;font-size:.8rem;margin-top:6px">'
        'Ejemplo de fallo: Citar [SEC-001] (desactualizado) en vez de [SEC-002] (vigente).'
        '</div></div>',
        unsafe_allow_html=True,
    )

    c3, c4 = st.columns(2)

    c3.markdown(
        '<div class="card" style="border-color:#ef4444">'
        '<div style="color:#ef4444;font-weight:bold;font-size:1.1rem">3. Safety (Seguridad)</div>'
        '<div style="font-size:.9rem;margin-top:8px"><b>Tipo:</b> Factual safety gate</div>'
        '<div style="font-size:.85rem;margin-top:6px">'
        '<b>Que mide:</b> Hay datos incorrectos que puedan causar dano si el usuario los sigue?<br>'
        '<b>Acciones:</b> PASS (todo correcto), WARN (impreciso), BLOCK (dato incorrecto confirmado).<br>'
        '<b>Score:</b> 1.0=PASS, 0.6=WARN, 0.2=BLOCK.'
        '</div>'
        '<div style="color:#94a3b8;font-size:.8rem;margin-top:6px">'
        'Ejemplo de BLOCK: Informar "8 caracteres minimo" cuando la politica vigente exige 12.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    c4.markdown(
        '<div class="card" style="border-color:#eab308">'
        '<div style="color:#eab308;font-weight:bold;font-size:1.1rem">4. Debate (Adversarial)</div>'
        '<div style="font-size:.9rem;margin-top:8px"><b>Tipo:</b> Devil\'s advocate</div>'
        '<div style="font-size:.85rem;margin-top:6px">'
        '<b>Que mide:</b> Busca activamente en los docs algo que contradiga la respuesta.<br>'
        '<b>Veredictos:</b> ACCEPT (sin contradicciones), REVISE (encontro contradiccion con doc vigente).<br>'
        '<b>Score:</b> 0.9=ACCEPT, 0.3=REVISE.'
        '</div>'
        '<div style="color:#94a3b8;font-size:.8rem;margin-top:6px">'
        'Util para detectar cuando Faithfulness da score alto pero hay un doc que contradice.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # Row 2: New RAGAS judges
    st.markdown("---")
    st.markdown("##### Jueces RAGAS (nuevos)")

    c5, c6 = st.columns(2)

    c5.markdown(
        '<div class="card" style="border-color:#06b6d4">'
        '<div style="color:#06b6d4;font-weight:bold;font-size:1.1rem">5. Relevancy (Pertinencia)</div>'
        '<div style="font-size:.9rem;margin-top:8px"><b>RAGAS equivalente:</b> Answer Relevancy</div>'
        '<div style="font-size:.85rem;margin-top:6px">'
        '<b>Que mide:</b> La respuesta realmente contesta la pregunta que hizo el usuario?<br>'
        '<b>Clasificacion:</b> RELEVANT (1.0), PARTIAL (0.5), OFF_TOPIC (0.1).<br>'
        '<b>Rubrica fija:</b> No permite scores intermedios inventados por el LLM.'
        '</div>'
        '<div style="color:#94a3b8;font-size:.8rem;margin-top:6px">'
        'Ejemplo de PARTIAL: Preguntan sobre contrasenas y el modelo habla de VPN y teletrabajo.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    c6.markdown(
        '<div class="card" style="border-color:#10b981">'
        '<div style="color:#10b981;font-weight:bold;font-size:1.1rem">6. Correctness (F1 Score)</div>'
        '<div style="font-size:.9rem;margin-top:8px"><b>RAGAS equivalente:</b> Answer Correctness</div>'
        '<div style="font-size:.85rem;margin-top:6px">'
        '<b>Que mide:</b> Compara la respuesta del modelo con una respuesta de referencia (gold answer).<br>'
        '<b>Mecanismo:</b> Extrae hechos factuales y los clasifica en:<br>'
        '- <b>TP</b> (True Positive): dato correcto en ambas<br>'
        '- <b>FP</b> (False Positive): dato inventado o incorrecto<br>'
        '- <b>FN</b> (False Negative): dato omitido<br>'
        '<b>Score:</b> F1 = TP / (TP + 0.5*FP + 0.5*FN)'
        '</div>'
        '<div style="color:#94a3b8;font-size:.8rem;margin-top:6px">'
        'Esta es la metrica MAS objetiva porque compara contra una respuesta conocida.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # ── Interpretation guide ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Como Interpretar los Scores")

    st.markdown(
        '<div class="card" style="border-color:#22c55e">'
        '<table style="width:100%;border-collapse:collapse;font-size:.9rem">'
        '<tr style="border-bottom:1px solid #334155">'
        '<th style="text-align:left;padding:8px;color:#94a3b8">Rango</th>'
        '<th style="text-align:left;padding:8px;color:#94a3b8">Nivel</th>'
        '<th style="text-align:left;padding:8px;color:#94a3b8">Interpretacion</th>'
        '<th style="text-align:left;padding:8px;color:#94a3b8">Uso recomendado</th></tr>'
        '<tr style="border-bottom:1px solid #334155">'
        '<td style="padding:8px;color:#22c55e;font-weight:bold">&gt; 0.85</td>'
        '<td style="padding:8px">Excelente</td>'
        '<td style="padding:8px">Respuestas confiables y completas</td>'
        '<td style="padding:8px">Produccion, cliente final</td></tr>'
        '<tr style="border-bottom:1px solid #334155">'
        '<td style="padding:8px;color:#eab308;font-weight:bold">0.70 - 0.85</td>'
        '<td style="padding:8px">Aceptable</td>'
        '<td style="padding:8px">Funcional con supervisado humano</td>'
        '<td style="padding:8px">Herramientas internas</td></tr>'
        '<tr style="border-bottom:1px solid #334155">'
        '<td style="padding:8px;color:#f97316;font-weight:bold">0.50 - 0.70</td>'
        '<td style="padding:8px">Debil</td>'
        '<td style="padding:8px">Errores frecuentes, requiere mejora</td>'
        '<td style="padding:8px">Solo para prototipos</td></tr>'
        '<tr>'
        '<td style="padding:8px;color:#ef4444;font-weight:bold">&lt; 0.50</td>'
        '<td style="padding:8px">Critico</td>'
        '<td style="padding:8px">Respuestas no confiables</td>'
        '<td style="padding:8px">No usar en produccion</td></tr>'
        '</table></div>',
        unsafe_allow_html=True,
    )

    # ── Common failure patterns ──────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Patrones Comunes de Fallo del LLM Juez")

    patterns = [
        (
            "Score inflado por formato",
            "El juez da score alto a respuestas bien redactadas aunque tengan errores factuales. "
            "Solucion: Correctness (F1 vs referencia) es inmune a esto.",
            "#ef4444",
        ),
        (
            "Inconsistencia entre runs",
            "El mismo prompt produce scores diferentes en ejecuciones consecutivas. "
            "Solucion: usamos temperature=0 en el juez para minimizar variabilidad.",
            "#eab308",
        ),
        (
            "Faithfulness alto pero Correctness bajo",
            "Los datos que menciono son correctos, pero omitio informacion clave (muchos FN). "
            "La respuesta es 'verdadera pero incompleta'.",
            "#06b6d4",
        ),
        (
            "Relevancy alto pero Safety BLOCK",
            "El modelo respondio la pregunta correcta pero con datos equivocados. "
            "Es relevante pero peligroso.",
            "#a855f7",
        ),
    ]

    for title, desc, color in patterns:
        st.markdown(
            f'<div class="card" style="border-color:{color};padding:12px">'
            f'<b style="color:{color}">{title}</b><br>'
            f'<span style="font-size:.85rem">{desc}</span></div>',
            unsafe_allow_html=True,
        )

    # ── RAGAS reference ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Referencia RAGAS")
    st.markdown(
        "Este sistema esta inspirado en el framework [RAGAS](https://docs.ragas.io/) "
        "(Retrieval Augmented Generation Assessment), el estandar de la industria para "
        "evaluar sistemas RAG. Las metricas Faithfulness y Answer Correctness son "
        "implementaciones directas de RAGAS adaptadas a nuestro contexto."
    )
    st.markdown(
        "**Fuentes:**\n"
        "- [RAGAS Documentation](https://docs.ragas.io/)\n"
        "- [RAG Evaluation Metrics - Patronus AI](https://www.patronus.ai/llm-testing/rag-evaluation-metrics)\n"
        "- [LLM Evaluation Best Practices 2025](https://medium.com/@QuarkAndCode/llm-evaluation-in-2025-metrics-rag-llm-as-judge-best-practices-ad2872cfa7cb)"
    )

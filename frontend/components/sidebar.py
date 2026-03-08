"""
sidebar.py — Left Navigation Panel
====================================
Shows app branding, navigation, analysis status,
and a "Run Analysis" button.
"""

import streamlit as st
from frontend.state import State
from frontend.styles import risk_color


def render_sidebar() -> str:
    """
    Renders the sidebar and returns the selected page name.

    Returns:
        One of: "Dashboard", "Projects", "Chat", "Reports"
    """
    with st.sidebar:
        # ── Branding ──────────────────────────────────────────
        st.markdown("""
<div style="padding: 8px 0 24px 0">
  <div style="font-size:1.5rem;font-weight:700;color:#e2e8f0">
    🛡️ RiskPulse AI
  </div>
  <div style="font-size:0.75rem;color:#8b96aa;margin-top:2px">
    IT Project Risk Management
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────
        st.markdown(
            '<div style="font-size:0.7rem;color:#8b96aa;'
            'text-transform:uppercase;letter-spacing:0.1em;'
            'margin-bottom:8px">Navigation</div>',
            unsafe_allow_html=True
        )

        pages = {
            "🏠  Dashboard":  "Dashboard",
            "📋  Projects":   "Projects",
            "💬  AI Chat":    "Chat",
            "📄  Reports":    "Reports",
        }

        # Use radio for page selection
        selected_label = st.radio(
            label="nav",
            options=list(pages.keys()),
            label_visibility="collapsed"
        )
        selected_page = pages[selected_label]

        st.divider()

        # ── Analysis Status ───────────────────────────────────
        st.markdown(
            '<div style="font-size:0.7rem;color:#8b96aa;'
            'text-transform:uppercase;letter-spacing:0.1em;'
            'margin-bottom:8px">Portfolio Status</div>',
            unsafe_allow_html=True
        )

        analysis = State.get_analysis()

        if analysis:
            # Show portfolio score with color
            score = analysis.portfolio_risk_score
            level = "CRITICAL" if score >= 75 else \
                    "HIGH"     if score >= 55 else \
                    "MEDIUM"   if score >= 30 else "LOW"
            color = risk_color(level)

            st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:10px;padding:14px;margin-bottom:12px">
  <div style="font-size:0.7rem;color:#8b96aa;margin-bottom:4px">
    PORTFOLIO RISK
  </div>
  <div style="font-size:1.8rem;font-weight:700;color:{color}">
    {score:.0f}<span style="font-size:1rem;color:#8b96aa">/100</span>
  </div>
  <div style="font-size:0.78rem;color:{color};font-weight:600">
    {level}
  </div>
</div>
""", unsafe_allow_html=True)

            # Project risk level breakdown
            for report in sorted(
                analysis.risk_reports,
                key=lambda r: r.overall_risk_score,
                reverse=True
            ):
                c = risk_color(report.risk_level.value)
                st.markdown(f"""
<div style="display:flex;justify-content:space-between;
     align-items:center;padding:5px 0;
     border-bottom:1px solid #1e2130;font-size:0.82rem">
  <span style="color:#c0c8d8">{report.project_code}</span>
  <span style="color:{c};font-weight:600">
    {report.overall_risk_score:.0f} {report.risk_level.value}
  </span>
</div>
""", unsafe_allow_html=True)

            # Show last analysis time
            st.markdown(
                f'<div style="font-size:0.7rem;color:#8b96aa;'
                f'margin-top:10px">Last run: '
                f'{analysis.analyzed_at.strftime("%H:%M:%S")}</div>',
                unsafe_allow_html=True
            )

        else:
            st.markdown("""
<div style="background:#1e2130;border:1px dashed #3d4460;
     border-radius:10px;padding:16px;text-align:center;
     color:#8b96aa;font-size:0.85rem">
  No analysis data yet.<br>Run analysis to begin.
</div>
""", unsafe_allow_html=True)

        st.divider()

        # ── Run Analysis Button ───────────────────────────────
        if st.button(
            "▶  Run Full Analysis",
            type="primary",
            use_container_width=True,
            disabled=State.is_analyzing()
        ):
            State.set_analyzing(True)
            st.rerun()

        # RAG status indicator
        rag_ready = State.is_rag_ready()
        rag_icon  = "🟢" if rag_ready else "🔴"
        rag_text  = "AI Chat Ready" if rag_ready else "AI Chat Offline"
        st.markdown(
            f'<div style="font-size:0.72rem;color:#8b96aa;'
            f'text-align:center;margin-top:8px">'
            f'{rag_icon} {rag_text}</div>',
            unsafe_allow_html=True
        )

        # Version footer
        st.markdown(
            '<div style="font-size:0.68rem;color:#4a5568;'
            'text-align:center;margin-top:24px">v1.0.0</div>',
            unsafe_allow_html=True
        )

    return selected_page
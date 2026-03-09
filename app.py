"""
app.py — RiskPulse AI Entry Point
==================================
Dark Command Center — Professional Risk Intelligence Platform
"""

import streamlit as st

st.set_page_config(
    page_title="RiskPulse AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from frontend.state import State
from frontend.styles import get_css, risk_color
from frontend.pages.dashboard import render_dashboard
from frontend.pages.projects import render_projects
from frontend.pages.chat import render_chat
from frontend.pages.reports import render_reports
from frontend.pages.live_data import render_live_data
from frontend.pages.run_analysis import render_run_analysis


def main():
    st.markdown(get_css(), unsafe_allow_html=True)
    State.initialize()

    # ── Start RAG pipeline once ────────────────────────────────
    if not State.is_rag_ready():
        try:
            from backend.rag.rag_pipeline import RiskRAGPipeline
            from backend.agents.risk_manager import ProjectRiskManager

            with st.spinner("Initializing AI systems..."):
                rag = RiskRAGPipeline()
                rag.initialize()
                manager = ProjectRiskManager(rag_pipeline=rag)
                State.set_rag(rag)
                State.set_manager(manager)
                State.set_rag_ready(True)

        except Exception as e:
            st.warning(f"AI initialization failed: {e}")

    # ── Navbar ─────────────────────────────────────────────────
    analysis = State.get_analysis()

    if analysis:
        score = analysis.portfolio_risk_score
        level = (
            "CRITICAL" if score >= 75 else
            "HIGH"     if score >= 55 else
            "MEDIUM"   if score >= 30 else "LOW"
        )
        color      = risk_color(level)
        score_html = (
            f'<span style="color:{color};font-family:\'JetBrains Mono\',monospace;'
            f'font-weight:700;font-size:0.8rem">{score:.0f}/100</span>'
            f'<span style="color:var(--text-muted);margin:0 6px">·</span>'
            f'<span style="color:{color};font-size:0.72rem;font-weight:600">{level}</span>'
        )
    else:
        score_html = '<span style="color:var(--text-muted);font-size:0.78rem">No analysis yet</span>'

    ai_status = (
        '<span class="rp-dot-live"></span>'
        '<span style="color:var(--low)">AI Ready</span>'
    ) if State.is_rag_ready() else (
        '<span class="rp-dot-off"></span>'
        '<span style="color:var(--critical)">AI Offline</span>'
    )

    live_data_fetched = bool(st.session_state.get("live_ext_data"))
    live_indicator = (
        '<span style="display:inline-block;width:5px;height:5px;'
        'border-radius:50%;background:var(--low);'
        'box-shadow:0 0 6px var(--low);margin-right:4px;'
        'animation:blink 2s infinite"></span>'
        '<span style="color:var(--low)">Live</span>'
    ) if live_data_fetched else (
        '<span style="color:var(--text-muted)">No live data</span>'
    )

    st.markdown(f"""
<div class="rp-navbar">
  <div class="rp-navbar-left">
    <div class="rp-navbar-logo">🛡️</div>
    <div>
      <div class="rp-navbar-title">RiskPulse AI</div>
      <div class="rp-navbar-sub">IT Portfolio Risk Intelligence</div>
    </div>
  </div>
  <div class="rp-navbar-right">
    <div class="rp-status-pill">
      <span style="color:var(--text-muted);font-size:0.68rem;
           letter-spacing:0.08em">PORTFOLIO</span>
      {score_html}
    </div>
    <div class="rp-status-pill">{live_indicator}</div>
    <div class="rp-status-pill">{ai_status}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Navigation tabs ────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "  🏠  Dashboard  ",
        "  📋  Projects  ",
        "  🌐  Live Data  ",
        "  💬  AI Chat  ",
        "  📄  Reports  ",
        "  ⚙️  Run Analysis  ",
    ])

    with tab1:
        if not analysis:
            st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:16px;padding:64px 40px;text-align:center;margin-top:24px;
     position:relative;overflow:hidden">
  <div style="position:absolute;top:-80px;left:50%;transform:translateX(-50%);
       width:240px;height:240px;
       background:radial-gradient(circle,rgba(0,194,255,0.06) 0%,transparent 70%);
       border-radius:50%;pointer-events:none"></div>
  <div style="font-size:2.8rem;margin-bottom:18px;position:relative">🛡️</div>
  <div style="font-size:1.3rem;font-weight:700;color:var(--text-primary);
       margin-bottom:8px;letter-spacing:-0.02em;position:relative">
    Welcome to RiskPulse AI
  </div>
  <div style="color:var(--text-secondary);margin-bottom:6px;
       font-size:0.88rem;line-height:1.6;position:relative">
    Go to the <b style="color:var(--accent)">⚙️ Run Analysis</b> tab to begin.
    Choose <b style="color:#3b82f6">Synthetic</b> for a baseline demo,
    or <b style="color:#00d68f">Real Data</b> if you've uploaded internal KPIs.
  </div>
  <div style="font-size:0.75rem;color:var(--text-muted);margin-top:16px;
       font-family:'JetBrains Mono',monospace;position:relative">
    15 projects · 7 risk dimensions · synthetic + real data modes
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            render_dashboard()

    with tab2:
        if not analysis:
            st.info("Run an analysis first from the ⚙️ Run Analysis tab.")
        else:
            render_projects()

    with tab3:
        render_live_data()

    with tab4:
        render_chat()

    with tab5:
        if not analysis:
            st.info("Run an analysis first from the ⚙️ Run Analysis tab.")
        else:
            render_reports()

    with tab6:
        render_run_analysis()


if __name__ == "__main__":
    main()
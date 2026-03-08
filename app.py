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


def main():
    # Inject CSS
    st.markdown(get_css(), unsafe_allow_html=True)

    # Initialize state
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

    # ── Top navigation bar ─────────────────────────────────────
    analysis = State.get_analysis()

    if analysis:
        score      = analysis.portfolio_risk_score
        level      = (
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
      <span style="color:var(--text-muted);font-size:0.68rem;letter-spacing:0.08em">PORTFOLIO</span>
      {score_html}
    </div>
    <div class="rp-status-pill">
      {ai_status}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Navigation tabs ────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "  🏠  Dashboard  ",
        "  📋  Projects  ",
        "  💬  AI Chat  ",
        "  📄  Reports  ",
        "  ⚙️  Run Analysis  ",
    ])

    # ── Run Analysis tab ───────────────────────────────────────
    with tab5:
        st.markdown("""
<div class="rp-page-header">
  <div class="rp-page-title">Run Portfolio Analysis</div>
  <div class="rp-page-subtitle">
    Execute a full 5-agent pipeline across all 15 IT projects
  </div>
</div>
""", unsafe_allow_html=True)

        if analysis:
            st.success(
                f"✅ Last analysis complete — "
                f"Portfolio: {analysis.portfolio_risk_score:.0f}/100 · "
                f"{analysis.high_risk_count} projects need attention · "
                f"{analysis.total_projects_analyzed} projects analyzed"
            )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            run_btn = st.button(
                "▶  Run Full Analysis",
                type="primary",
                width="stretch",
                disabled=State.is_analyzing()
            )
        with col2:
            if analysis:
                st.button(
                    "↻  Re-run Analysis",
                    type="secondary",
                    width="stretch",
                    disabled=State.is_analyzing(),
                    key="rerun_btn"
                )

        if run_btn:
            State.set_analyzing(True)
            manager = State.get_manager()
            if manager:
                with st.spinner("Running full portfolio risk analysis..."):
                    try:
                        result = manager.run_full_analysis()
                        State.set_analysis(result)
                        State.set_analyzing(False)
                        st.success(
                            f"✅ Analysis complete! "
                            f"Portfolio: {result.portfolio_risk_score:.0f}/100 · "
                            f"{result.high_risk_count} projects need attention"
                        )
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
                        State.set_analyzing(False)
            else:
                st.error("Risk Manager not initialized. Refresh the page.")
                State.set_analyzing(False)

        # ── Pipeline steps ─────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Analysis Pipeline</div>', unsafe_allow_html=True)

        steps = [
            ("01", "📂", "Data Loading",
             "Load 15 IT projects + 20 real-time market signals from database"),
            ("02", "🌐", "Market Analysis Agent",
             "Process NASSCOM, RBI, SEBI, Gartner signals → compute market risk score"),
            ("03", "📊", "Project Status Agent",
             "Evaluate schedule, budget, team, and client KPIs for all projects"),
            ("04", "🔢", "Risk Scoring Agent × 15",
             "Apply 7-category weighted formula per project → generate RiskReport"),
            ("05", "📈", "Portfolio Aggregation",
             "Compute weighted portfolio score → store in ChromaDB for AI chat"),
        ]

        for num, icon, title, desc in steps:
            st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:16px 20px;margin-bottom:8px;
     display:flex;align-items:flex-start;gap:16px">
  <div style="width:28px;height:28px;background:var(--accent-dim);
       border:1px solid rgba(0,194,255,0.25);border-radius:7px;
       display:flex;align-items:center;justify-content:center;
       font-size:0.65rem;font-weight:700;color:var(--accent);
       font-family:'JetBrains Mono',monospace;flex-shrink:0;margin-top:1px">
    {num}
  </div>
  <div>
    <div style="font-size:0.88rem;font-weight:600;color:var(--text-primary);
         margin-bottom:3px">{icon} {title}</div>
    <div style="font-size:0.8rem;color:var(--text-secondary);line-height:1.5">{desc}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Dashboard tab ──────────────────────────────────────────
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
    Go to the <b style="color:var(--accent)">⚙️ Run Analysis</b> tab
    and click <b style="color:var(--text-primary)">▶ Run Full Analysis</b> to begin
  </div>
  <div style="font-size:0.75rem;color:var(--text-muted);margin-top:16px;
       font-family:'JetBrains Mono',monospace;position:relative">
    15 projects · 7 risk dimensions · real-time AI analysis
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            render_dashboard()

    # ── Projects tab ───────────────────────────────────────────
    with tab2:
        if not analysis:
            st.info("Run an analysis first from the ⚙️ Run Analysis tab.")
        else:
            render_projects()

    # ── Chat tab ───────────────────────────────────────────────
    with tab3:
        render_chat()

    # ── Reports tab ────────────────────────────────────────────
    with tab4:
        if not analysis:
            st.info("Run an analysis first from the ⚙️ Run Analysis tab.")
        else:
            render_reports()


if __name__ == "__main__":
    main()
"""
app.py — RiskPulse AI Entry Point
==================================
Uses top navigation bar instead of sidebar.
No sidebar = no collapse problem.
"""

import streamlit as st

st.set_page_config(
    page_title="RiskPulse AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",  # hide sidebar completely
)

from frontend.state import State
from frontend.styles import get_css
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

            with st.spinner("🧠 Initializing AI systems..."):
                rag = RiskRAGPipeline()
                rag.initialize()
                manager = ProjectRiskManager(rag_pipeline=rag)
                State.set_rag(rag)
                State.set_manager(manager)
                State.set_rag_ready(True)

        except Exception as e:
            st.warning(f"⚠️ AI initialization failed: {e}")

    # ── Top navigation bar ─────────────────────────────────────
    analysis = State.get_analysis()
    portfolio_score = f"{analysis.portfolio_risk_score:.0f}/100" if analysis else "—"

    st.markdown(f"""
<div style="
    background:#141724;
    border-bottom:1px solid #2d3348;
    padding:12px 24px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin:-1rem -1rem 1.5rem -1rem;
    position:sticky;
    top:0;
    z-index:999;
">
    <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0">
        🛡️ RiskPulse AI
    </div>
    <div style="font-size:0.8rem;color:#8b96aa">
        Portfolio Risk: <span style="color:#f59e0b;font-weight:600">{portfolio_score}</span>
        &nbsp;|&nbsp;
        {"🟢 AI Ready" if State.is_rag_ready() else "🔴 AI Offline"}
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Navigation tabs ────────────────────────────────────────
    # st.tabs() renders as a top tab bar — always visible,
    # no sidebar needed, no collapse issues
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠  Dashboard",
        "📋  Projects",
        "💬  AI Chat",
        "📄  Reports",
        "⚙️  Run Analysis",
    ])

    # ── Run Analysis tab ───────────────────────────────────────
    with tab5:
        st.markdown(
            '<h3 style="color:#e2e8f0">Run Portfolio Analysis</h3>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p style="color:#8b96aa">Click the button below to analyze '
            'all 5 projects across 7 risk dimensions.</p>',
            unsafe_allow_html=True
        )

        if analysis:
            st.success(
                f"✅ Last analysis: Portfolio score "
                f"{analysis.portfolio_risk_score:.0f}/100 — "
                f"{analysis.high_risk_count} HIGH/CRITICAL projects"
            )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            run_btn = st.button(
                "▶  Run Full Analysis",
                type="primary",
                use_container_width=True,
                disabled=State.is_analyzing()
            )

        if run_btn:
            State.set_analyzing(True)
            manager = State.get_manager()
            if manager:
                with st.spinner("⚙️ Running full portfolio risk analysis..."):
                    try:
                        result = manager.run_full_analysis()
                        State.set_analysis(result)
                        State.set_analyzing(False)
                        st.success(
                            f"✅ Analysis complete! "
                            f"Portfolio score: {result.portfolio_risk_score:.0f}/100 | "
                            f"{result.high_risk_count} projects need attention"
                        )
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                        State.set_analyzing(False)
            else:
                st.error("❌ Risk Manager not initialized. Refresh the page.")
                State.set_analyzing(False)

        # Show what the analysis will do
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
<div style="background:#1e2130;border:1px solid #2d3348;border-radius:12px;padding:20px">
  <div style="color:#8b96aa;font-size:0.85rem;margin-bottom:12px">
    ANALYSIS PIPELINE — 5 steps
  </div>
  <div style="color:#c0c8d8;font-size:0.88rem;line-height:2">
    📂 Step 1 — Load 5 projects + 6 market signals<br>
    🌐 Step 2 — Market Analysis Agent (NASSCOM, RBI, BFSI signals)<br>
    📊 Step 3 — Project Status Agent (schedule, budget, team, client KPIs)<br>
    🔢 Step 4 — Risk Scoring Agent × 5 (7-category weighted formula)<br>
    📈 Step 5 — Portfolio aggregation + ChromaDB storage
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Dashboard tab ──────────────────────────────────────────
    with tab1:
        if not analysis:
            st.markdown("""
<div style="background:#1e2130;border:2px dashed #3d4460;border-radius:16px;
     padding:60px;text-align:center;margin-top:20px">
  <div style="font-size:3rem;margin-bottom:16px">🛡️</div>
  <div style="font-size:1.3rem;font-weight:600;color:#e2e8f0;margin-bottom:8px">
    Welcome to RiskPulse AI
  </div>
  <div style="color:#8b96aa;margin-bottom:8px">
    Go to the <b>⚙️ Run Analysis</b> tab and click
    <b>▶ Run Full Analysis</b> to begin
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
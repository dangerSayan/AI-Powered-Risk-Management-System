"""
reports.py — Detailed Risk Reports Page
=========================================
Full markdown risk reports with all evidence and mitigations.
Also shows agent execution logs and market signal details.
"""

import streamlit as st
from frontend.state import State
from frontend.styles import risk_badge, risk_color


def render_reports():
    st.markdown(
        '<h2 style="color:#e2e8f0;margin-bottom:4px">Risk Reports</h2>'
        '<p style="color:#8b96aa;font-size:0.9rem;margin-bottom:24px">'
        'Full analysis reports, agent logs, and market intelligence</p>',
        unsafe_allow_html=True
    )

    analysis = State.get_analysis()
    if not analysis:
        st.info("Run an analysis from the sidebar to generate reports.")
        return

    # ── Report selector ────────────────────────────────────────
    report_options = {
        f"{r.project_code} — {r.project_name}": r
        for r in sorted(
            analysis.risk_reports,
            key=lambda r: r.overall_risk_score,
            reverse=True
        )
    }
    report_options["📈 Market Intelligence"] = None
    report_options["🤖 Agent Execution Logs"] = None

    selected = st.selectbox(
        "Select Report",
        options=list(report_options.keys()),
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Render selected report ─────────────────────────────────
    if selected == "📈 Market Intelligence":
        _render_market_report(analysis.market_analysis)
    elif selected == "🤖 Agent Execution Logs":
        _render_agent_logs(analysis)
    else:
        report = report_options[selected]
        if report:
            _render_full_report(report)


def _render_full_report(report):
    """Full detailed report for one project."""
    color = risk_color(report.risk_level.value)
    badge = risk_badge(report.risk_level.value)

    # Report header
    st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:12px;padding:24px;margin-bottom:24px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="font-size:1.4rem;font-weight:700;color:#e2e8f0">
        Risk Assessment Report
      </div>
      <div style="color:#8b96aa;margin-top:4px">
        {report.project_name} · {report.project_code}
      </div>
      <div style="color:#4a5568;font-size:0.78rem;margin-top:2px">
        Generated: {report.generated_at.strftime('%d %B %Y at %H:%M')}
      </div>
    </div>
    <div style="text-align:right">
      {badge}
      <div style="font-size:2.8rem;font-weight:700;color:{color};line-height:1.1">
        {report.overall_risk_score:.0f}
        <span style="font-size:1rem;color:#8b96aa">/100</span>
      </div>
    </div>
  </div>
  <div style="margin-top:16px;padding-top:16px;border-top:1px solid #2d3348;
       font-size:0.9rem;color:#c0c8d8;line-height:1.7">
    {report.executive_summary}
  </div>
</div>
""", unsafe_allow_html=True)

    # Score summary table
    st.markdown(
        '<div class="section-header">Risk Category Scores</div>',
        unsafe_allow_html=True
    )
    cols = st.columns(7)
    for i, (cat, score) in enumerate(
        sorted(report.category_scores.items(), key=lambda x: x[1], reverse=True)
    ):
        with cols[i % 7]:
            c = risk_color(
                "CRITICAL" if score >= 75 else
                "HIGH"     if score >= 55 else
                "MEDIUM"   if score >= 30 else "LOW"
            )
            st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:8px;padding:12px;text-align:center;margin-bottom:8px">
  <div style="font-size:1.3rem;font-weight:700;color:{c}">{score:.0f}</div>
  <div style="font-size:0.65rem;color:#8b96aa;margin-top:2px">{cat[:6]}</div>
</div>
""", unsafe_allow_html=True)

    # Full detailed analysis (markdown)
    if report.detailed_analysis:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-header">Detailed Evidence</div>',
            unsafe_allow_html=True
        )
        with st.expander("View full evidence breakdown", expanded=False):
            st.markdown(report.detailed_analysis)

    # Mitigation table
    if report.mitigation_strategies:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-header">Action Plan</div>',
            unsafe_allow_html=True
        )
        for m in report.mitigation_strategies:
            effort_color = (
                "#e84545" if m.effort == "High" else
                "#f59e0b" if m.effort == "Medium" else "#10b981"
            )
            st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:10px;padding:16px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;margin-bottom:10px">
    <div style="font-weight:600;color:#3b82f6">
      Priority {m.priority}
    </div>
    <div style="display:flex;gap:16px;font-size:0.8rem">
      <span style="color:{effort_color}">⚡ {m.effort}</span>
      <span style="color:#10b981">↓{m.estimated_risk_reduction:.0f} pts</span>
      <span style="color:#8b96aa">⏱ {m.timeline}</span>
    </div>
  </div>
  <div style="color:#e2e8f0;margin-bottom:8px">{m.action}</div>
  <div style="font-size:0.8rem;color:#8b96aa">Owner: {m.owner}</div>
</div>
""", unsafe_allow_html=True)


def _render_market_report(market_analysis):
    """Full market intelligence report."""
    score     = market_analysis.market_risk_score
    sentiment = market_analysis.overall_market_sentiment
    color     = risk_color(
        "CRITICAL" if score >= 75 else
        "HIGH"     if score >= 55 else
        "MEDIUM"   if score >= 30 else "LOW"
    )

    st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:12px;padding:24px;margin-bottom:24px">
  <div style="font-size:1.3rem;font-weight:700;color:#e2e8f0;margin-bottom:4px">
    Market Intelligence Report
  </div>
  <div style="display:flex;gap:24px;margin-top:12px">
    <div>
      <div style="font-size:0.7rem;color:#8b96aa">MARKET RISK</div>
      <div style="font-size:2rem;font-weight:700;color:{color}">{score:.0f}/100</div>
    </div>
    <div>
      <div style="font-size:0.7rem;color:#8b96aa">SENTIMENT</div>
      <div style="font-size:1.3rem;font-weight:600;color:{color}">{sentiment}</div>
    </div>
  </div>
  <div style="margin-top:16px;color:#c0c8d8;font-size:0.9rem;line-height:1.7">
    {market_analysis.it_sector_outlook}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">Key Trends</div>',
        unsafe_allow_html=True
    )
    for trend in market_analysis.key_trends:
        st.markdown(f"""
<div style="background:#1e2130;border-left:3px solid {color};
     padding:10px 16px;border-radius:0 8px 8px 0;margin-bottom:8px;
     color:#c0c8d8;font-size:0.88rem">{trend}</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">Individual Market Signals</div>',
        unsafe_allow_html=True
    )
    for signal in market_analysis.signals:
        sc = "#10b981" if signal.sentiment == "positive" else \
             "#e84545" if signal.sentiment == "negative" else "#8b96aa"
        icon = "🟢" if signal.sentiment == "positive" else \
               "🔴" if signal.sentiment == "negative" else "⚪"
        st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:10px;padding:14px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px">
    <span style="font-size:0.75rem;color:#8b96aa">{signal.source}</span>
    <span style="font-size:0.75rem;color:{sc}">{icon} {signal.sentiment.upper()}</span>
  </div>
  <div style="font-weight:600;color:#e2e8f0;margin-bottom:6px">
    {signal.headline}
  </div>
  <div style="font-size:0.85rem;color:#8b96aa">{signal.impact_on_it}</div>
</div>
""", unsafe_allow_html=True)


def _render_agent_logs(analysis):
    """Agent execution performance logs."""
    st.markdown(
        '<div class="section-header">Agent Execution Summary</div>',
        unsafe_allow_html=True
    )

    # Summary stats
    total_time = sum(a.processing_time_seconds for a in analysis.agent_outputs)
    st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:10px;padding:16px;margin-bottom:20px">
  <div style="display:flex;gap:32px">
    <div>
      <div style="font-size:0.7rem;color:#8b96aa">AGENTS RAN</div>
      <div style="font-size:1.5rem;font-weight:700;color:#3b82f6">
        {len(analysis.agent_outputs)}
      </div>
    </div>
    <div>
      <div style="font-size:0.7rem;color:#8b96aa">TOTAL TIME</div>
      <div style="font-size:1.5rem;font-weight:700;color:#10b981">
        {total_time:.2f}s
      </div>
    </div>
    <div>
      <div style="font-size:0.7rem;color:#8b96aa">PROJECTS SCORED</div>
      <div style="font-size:1.5rem;font-weight:700;color:#e2e8f0">
        {analysis.total_projects_analyzed}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    for agent in analysis.agent_outputs:
        conf_color = "#10b981" if agent.confidence >= 0.85 else \
                     "#f59e0b" if agent.confidence >= 0.7  else "#e84545"
        st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:10px;padding:16px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;margin-bottom:8px">
    <span style="font-weight:600;color:#e2e8f0">{agent.agent_name}</span>
    <div style="display:flex;gap:16px;font-size:0.8rem">
      <span style="color:{conf_color}">
        {agent.confidence:.0%} confidence
      </span>
      <span style="color:#8b96aa">{agent.processing_time_seconds:.3f}s</span>
    </div>
  </div>
  <div style="font-size:0.85rem;color:#c0c8d8">{agent.task_completed}</div>
</div>
""", unsafe_allow_html=True)
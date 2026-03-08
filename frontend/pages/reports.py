"""
reports.py — Detailed Risk Reports Page
=========================================
Full markdown risk reports with all evidence and mitigations.
Also shows agent execution logs and market signal details.
"""

import streamlit as st
from frontend.state import State
from frontend.styles import risk_badge, risk_color, score_bar


def render_reports():
    st.markdown("""
<div class="rp-page-header">
  <div class="rp-page-title">Risk Reports</div>
  <div class="rp-page-subtitle">
    Full analysis reports, agent logs, and market intelligence
  </div>
</div>
""", unsafe_allow_html=True)

    analysis = State.get_analysis()
    if not analysis:
        st.info("Run an analysis first from the ⚙️ Run Analysis tab.")
        return

    # ── Report selector ────────────────────────────────────────
    report_options = {
        f"{r.project_code} — {r.project_name}": r
        for r in sorted(
            analysis.risk_reports,
            key=lambda r: r.overall_risk_score, reverse=True
        )
    }
    report_options["📈  Market Intelligence"] = None
    report_options["🤖  Agent Execution Logs"] = None

    selected = st.selectbox(
        "Select Report",
        options=list(report_options.keys()),
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if selected == "📈  Market Intelligence":
        _render_market_report(analysis.market_analysis)
    elif selected == "🤖  Agent Execution Logs":
        _render_agent_logs(analysis)
    else:
        report = report_options.get(selected)
        if report:
            _render_full_report(report)


def _render_full_report(report):
    color = risk_color(report.risk_level.value)
    badge = risk_badge(report.risk_level.value)

    # ── Report header ──────────────────────────────────────────
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:14px;padding:24px;margin-bottom:24px;
     border-left:4px solid {color}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="font-size:0.68rem;color:var(--text-muted);
           font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;
           text-transform:uppercase;margin-bottom:6px">Risk Assessment Report</div>
      <div style="font-size:1.3rem;font-weight:700;color:var(--text-primary);
           letter-spacing:-0.02em">{report.project_name}</div>
      <div style="color:var(--text-muted);font-size:0.72rem;margin-top:4px;
           font-family:'JetBrains Mono',monospace">
        {report.project_code} &nbsp;·&nbsp;
        {report.generated_at.strftime('%d %B %Y  %H:%M')}
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:14px">
      {badge}
      <div style="text-align:right">
        <div style="font-size:3rem;font-weight:700;color:{color};
             font-family:'JetBrains Mono',monospace;line-height:1">
          {report.overall_risk_score:.0f}
          <span style="font-size:1.1rem;color:var(--text-muted);font-weight:400">/100</span>
        </div>
      </div>
    </div>
  </div>
  <div style="margin-top:18px;padding-top:16px;border-top:1px solid var(--border);
       font-size:0.87rem;color:var(--text-secondary);line-height:1.7">
    {report.executive_summary}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Score tiles ────────────────────────────────────────────
    st.markdown('<div class="section-header">Risk Category Scores</div>',
                unsafe_allow_html=True)

    sorted_cats = sorted(
        report.category_scores.items(), key=lambda x: x[1], reverse=True
    )
    cols = st.columns(7)
    for i, (cat, score) in enumerate(sorted_cats):
        c = risk_color(
            "CRITICAL" if score >= 75 else
            "HIGH"     if score >= 55 else
            "MEDIUM"   if score >= 30 else "LOW"
        )
        with cols[i % 7]:
            st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:9px;padding:12px 8px;text-align:center;
     margin-bottom:8px;border-top:2px solid {c}">
  <div style="font-size:1.4rem;font-weight:700;color:{c};
       font-family:'JetBrains Mono',monospace">{score:.0f}</div>
  <div style="font-size:0.62rem;color:var(--text-muted);
       margin-top:3px;letter-spacing:0.05em;text-transform:uppercase">
    {cat[:6]}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Detailed analysis ──────────────────────────────────────
    if report.detailed_analysis:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Detailed Evidence</div>',
                    unsafe_allow_html=True)
        with st.expander("View full evidence breakdown", expanded=False):
            st.markdown(report.detailed_analysis)

    # ── Mitigation table ───────────────────────────────────────
    if report.mitigation_strategies:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Action Plan</div>',
                    unsafe_allow_html=True)
        for m in report.mitigation_strategies:
            effort_color = (
                "#ff4757" if m.effort == "High" else
                "#ffa502" if m.effort == "Medium" else "#00d68f"
            )
            st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:16px 18px;margin-bottom:8px">
  <div style="display:flex;justify-content:space-between;
       margin-bottom:10px;align-items:center">
    <span style="background:rgba(59,130,246,0.1);color:var(--medium);
         font-size:0.65rem;font-weight:700;padding:3px 10px;
         border-radius:5px;font-family:'JetBrains Mono',monospace;
         letter-spacing:0.08em;border:1px solid rgba(59,130,246,0.2)">
      PRIORITY {m.priority}
    </span>
    <div style="display:flex;gap:14px;font-size:0.76rem">
      <span style="color:{effort_color}">⚡ {m.effort}</span>
      <span style="color:var(--low)">↓{m.estimated_risk_reduction:.0f} pts</span>
      <span style="color:var(--text-muted)">⏱ {m.timeline}</span>
    </div>
  </div>
  <div style="color:var(--text-primary);font-size:0.86rem;
       margin-bottom:8px;line-height:1.5">{m.action}</div>
  <div style="font-size:0.76rem;color:var(--text-muted)">
    👤 {m.owner}
  </div>
</div>
""", unsafe_allow_html=True)


def _render_market_report(market_analysis):
    score     = market_analysis.market_risk_score
    sentiment = market_analysis.overall_market_sentiment
    color     = risk_color(
        "CRITICAL" if score >= 75 else
        "HIGH"     if score >= 55 else
        "MEDIUM"   if score >= 30 else "LOW"
    )

    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:14px;padding:24px;margin-bottom:24px;
     border-left:4px solid {color}">
  <div style="font-size:0.68rem;color:var(--text-muted);
       font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;
       text-transform:uppercase;margin-bottom:8px">Market Intelligence Report</div>
  <div style="display:flex;gap:32px;align-items:flex-end;margin-bottom:16px">
    <div>
      <div style="font-size:0.68rem;color:var(--text-muted);margin-bottom:4px;
           letter-spacing:0.06em;text-transform:uppercase">Market Risk</div>
      <div style="font-size:2.8rem;font-weight:700;color:{color};
           font-family:'JetBrains Mono',monospace;line-height:1">
        {score:.0f}
        <span style="font-size:1rem;color:var(--text-muted);font-weight:400">/100</span>
      </div>
    </div>
    <div>
      <div style="font-size:0.68rem;color:var(--text-muted);margin-bottom:4px;
           letter-spacing:0.06em;text-transform:uppercase">Sentiment</div>
      <div style="font-size:1.4rem;font-weight:700;color:{color};
           letter-spacing:0.02em">{sentiment}</div>
    </div>
  </div>
  <div style="color:var(--text-secondary);font-size:0.87rem;line-height:1.7">
    {market_analysis.it_sector_outlook}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Key Trends</div>',
                unsafe_allow_html=True)
    for trend in market_analysis.key_trends:
        st.markdown(f"""
<div class="rp-trend-item" style="border-left-color:{color}">{trend}</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Individual Market Signals</div>',
                unsafe_allow_html=True)

    for signal in market_analysis.signals:
        sc   = "#00d68f" if signal.sentiment == "positive" else \
               "#ff4757" if signal.sentiment == "negative" else "#8496b0"
        icon = "▲" if signal.sentiment == "positive" else \
               "▼" if signal.sentiment == "negative" else "●"
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:14px 16px;margin-bottom:8px;
     transition:border-color 0.2s">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:7px">
    <span style="font-size:0.7rem;color:var(--text-muted);
         font-family:'JetBrains Mono',monospace">{signal.source}</span>
    <span style="font-size:0.68rem;color:{sc};font-weight:700;
         font-family:'JetBrains Mono',monospace;letter-spacing:0.06em">
      {icon} {signal.sentiment.upper()}
    </span>
  </div>
  <div style="font-weight:600;color:var(--text-primary);font-size:0.87rem;
       margin-bottom:6px;line-height:1.4">{signal.headline}</div>
  <div style="font-size:0.81rem;color:var(--text-secondary);line-height:1.5">
    {signal.impact_on_it}
  </div>
</div>
""", unsafe_allow_html=True)


def _render_agent_logs(analysis):
    st.markdown('<div class="section-header">Agent Execution Summary</div>',
                unsafe_allow_html=True)

    total_time = sum(a.processing_time_seconds for a in analysis.agent_outputs)

    # Stats row
    col1, col2, col3 = st.columns(3)
    stats = [
        ("Agents Ran", str(len(analysis.agent_outputs)), "#3b82f6"),
        ("Total Time", f"{total_time:.2f}s", "#00d68f"),
        ("Projects Scored", str(analysis.total_projects_analyzed), "#e8edf5"),
    ]
    for col, (label, value, color) in zip([col1, col2, col3], stats):
        with col:
            st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:16px 18px;margin-bottom:16px">
  <div style="font-size:0.67rem;color:var(--text-muted);letter-spacing:0.09em;
       text-transform:uppercase;font-family:'JetBrains Mono',monospace;
       margin-bottom:6px">{label}</div>
  <div style="font-size:1.8rem;font-weight:700;color:{color};
       font-family:'JetBrains Mono',monospace">{value}</div>
</div>
""", unsafe_allow_html=True)

    # Agent rows
    for agent in analysis.agent_outputs:
        conf_color = "#00d68f" if agent.confidence >= 0.85 else \
                     "#ffa502" if agent.confidence >= 0.7  else "#ff4757"
        conf_pct   = f"{agent.confidence:.0%}"
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:16px 18px;margin-bottom:8px;
     display:flex;justify-content:space-between;align-items:center">
  <div>
    <div style="font-weight:600;color:var(--text-primary);font-size:0.88rem;
         margin-bottom:4px">{agent.agent_name}</div>
    <div style="font-size:0.8rem;color:var(--text-secondary)">
      {agent.task_completed}
    </div>
  </div>
  <div style="text-align:right;flex-shrink:0;margin-left:20px">
    <div style="font-size:0.88rem;font-weight:700;color:{conf_color};
         font-family:'JetBrains Mono',monospace">{conf_pct}</div>
    <div style="font-size:0.68rem;color:var(--text-muted);
         font-family:'JetBrains Mono',monospace;margin-top:2px">
      {agent.processing_time_seconds:.3f}s
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
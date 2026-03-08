"""
dashboard.py — Main Portfolio Dashboard Page
=============================================
Shows: portfolio KPIs, risk distribution chart,
project score cards, market signals, and alerts.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from frontend.state import State
from frontend.styles import risk_badge, risk_color, score_bar


def render_dashboard():
    """Main dashboard page renderer."""

    st.markdown(
        '<h2 style="color:#e2e8f0;margin-bottom:4px">Portfolio Dashboard</h2>'
        '<p style="color:#8b96aa;font-size:0.9rem;margin-bottom:24px">'
        'Real-time risk monitoring across all active IT projects</p>',
        unsafe_allow_html=True
    )

    analysis = State.get_analysis()

    # ── No data state ──────────────────────────────────────────
    if not analysis:
        st.markdown("""
<div style="background:#1e2130;border:2px dashed #3d4460;
     border-radius:16px;padding:60px;text-align:center">
  <div style="font-size:3rem;margin-bottom:16px">🛡️</div>
  <div style="font-size:1.3rem;font-weight:600;color:#e2e8f0;
       margin-bottom:8px">Welcome to RiskPulse AI</div>
  <div style="color:#8b96aa;margin-bottom:24px">
    Click <b>▶ Run Full Analysis</b> in the sidebar to start
    monitoring your IT project portfolio
  </div>
  <div style="font-size:0.82rem;color:#4a5568">
    Analyzes 5 projects across 7 risk dimensions
  </div>
</div>
""", unsafe_allow_html=True)
        return

    # ── KPI Cards Row ──────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    portfolio_score = analysis.portfolio_risk_score
    portfolio_level = (
        "CRITICAL" if portfolio_score >= 75 else
        "HIGH"     if portfolio_score >= 55 else
        "MEDIUM"   if portfolio_score >= 30 else "LOW"
    )

    with col1:
        color = risk_color(portfolio_level)
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-value" style="color:{color}">{portfolio_score:.0f}</div>
  <div style="font-size:0.7rem;color:{color};font-weight:600;
       margin-bottom:2px">{portfolio_level}</div>
  <div class="kpi-label">Portfolio Risk Score</div>
</div>""", unsafe_allow_html=True)

    with col2:
        count = analysis.high_risk_count
        color = "#e84545" if count >= 3 else "#f59e0b" if count >= 1 else "#10b981"
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-value" style="color:{color}">{count}</div>
  <div style="font-size:0.7rem;color:#8b96aa;margin-bottom:2px">
    of {analysis.total_projects_analyzed} projects
  </div>
  <div class="kpi-label">HIGH / CRITICAL Projects</div>
</div>""", unsafe_allow_html=True)

    with col3:
        market_score = analysis.market_analysis.market_risk_score
        sentiment    = analysis.market_analysis.overall_market_sentiment
        mcolor = risk_color(
            "CRITICAL" if market_score >= 75 else
            "HIGH"     if market_score >= 55 else
            "MEDIUM"   if market_score >= 30 else "LOW"
        )
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-value" style="color:{mcolor}">{market_score:.0f}</div>
  <div style="font-size:0.7rem;color:{mcolor};font-weight:600;
       margin-bottom:2px">{sentiment}</div>
  <div class="kpi-label">Market Risk Score</div>
</div>""", unsafe_allow_html=True)

    with col4:
        total_alerts = sum(len(r.key_alerts) for r in analysis.risk_reports)
        acolor = "#e84545" if total_alerts >= 10 else \
                 "#f59e0b" if total_alerts >= 5  else "#10b981"
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-value" style="color:{acolor}">{total_alerts}</div>
  <div style="font-size:0.7rem;color:#8b96aa;margin-bottom:2px">
    across all projects
  </div>
  <div class="kpi-label">Active Risk Alerts</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ─────────────────────────────────────────────
    chart_col, breakdown_col = st.columns([3, 2])

    with chart_col:
        st.markdown(
            '<div class="section-header">Project Risk Scores</div>',
            unsafe_allow_html=True
        )
        _render_score_chart(analysis.risk_reports)

    with breakdown_col:
        st.markdown(
            '<div class="section-header">Risk Distribution</div>',
            unsafe_allow_html=True
        )
        _render_donut_chart(analysis.risk_reports)

    # ── Project Cards + Alerts Row ─────────────────────────────
    projects_col, alerts_col = st.columns([3, 2])

    with projects_col:
        st.markdown(
            '<div class="section-header">Project Status Cards</div>',
            unsafe_allow_html=True
        )
        for report in sorted(
            analysis.risk_reports,
            key=lambda r: r.overall_risk_score,
            reverse=True
        ):
            _render_project_card(report)

    with alerts_col:
        st.markdown(
            '<div class="section-header">Active Alerts</div>',
            unsafe_allow_html=True
        )
        _render_alerts_panel(analysis.risk_reports)

    # ── Market Intelligence ────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">Market Intelligence</div>',
        unsafe_allow_html=True
    )
    _render_market_panel(analysis.market_analysis)


# ── Private render helpers ────────────────────────────────────

def _render_score_chart(reports):
    """Horizontal bar chart of all project risk scores."""
    sorted_reports = sorted(reports, key=lambda r: r.overall_risk_score)

    names  = [f"{r.project_code}" for r in sorted_reports]
    scores = [r.overall_risk_score for r in sorted_reports]
    colors = [risk_color(r.risk_level.value) for r in sorted_reports]

    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=12),
    ))

    fig.add_vline(x=30, line_dash="dot", line_color="#3b82f6",
                  annotation_text="MEDIUM", annotation_font_size=10)
    fig.add_vline(x=55, line_dash="dot", line_color="#f59e0b",
                  annotation_text="HIGH", annotation_font_size=10)
    fig.add_vline(x=75, line_dash="dot", line_color="#e84545",
                  annotation_text="CRITICAL", annotation_font_size=10)

    fig.update_layout(
        xaxis=dict(range=[0, 105], showgrid=False,
                   tickfont=dict(color="#8b96aa")),
        yaxis=dict(showgrid=False, tickfont=dict(color="#e2e8f0", size=12)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=40, t=10, b=0),
        height=220,
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def _render_donut_chart(reports):
    """Donut chart showing risk level distribution."""
    from collections import Counter
    level_counts = Counter(r.risk_level.value for r in reports)

    order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    labels = [l for l in order if l in level_counts]
    values = [level_counts[l] for l in labels]
    colors = [risk_color(l) for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker_colors=colors,
        textinfo="label+value",
        textfont=dict(color="#e2e8f0", size=11),
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=220,
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def _render_project_card(report):
    """Compact project card for the dashboard."""
    color  = risk_color(report.risk_level.value)
    badge  = risk_badge(report.risk_level.value)
    alerts = len(report.key_alerts)

    # Category score pills
    cat_html = ""
    top_cats = sorted(
        report.category_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:4]
    for cat, score in top_cats:
        c = risk_color(
            "CRITICAL" if score >= 75 else
            "HIGH"     if score >= 55 else
            "MEDIUM"   if score >= 30 else "LOW"
        )
        cat_html += (
            f'<span style="background:#1a1f2e;border:1px solid #2d3348;'
            f'border-radius:6px;padding:2px 8px;font-size:0.7rem;'
            f'color:{c};margin-right:4px">'
            f'{cat[:3]} {score:.0f}</span>'
        )

    st.markdown(f"""
<div class="project-card">
  <div style="display:flex;justify-content:space-between;align-items:center;
       margin-bottom:10px">
    <div>
      <span style="font-weight:600;color:#e2e8f0">{report.project_name}</span>
      <span style="color:#8b96aa;font-size:0.82rem;margin-left:8px">
        {report.project_code}
      </span>
    </div>
    <div style="display:flex;align-items:center;gap:8px">
      {badge}
      <span style="font-size:1.4rem;font-weight:700;color:{color}">
        {report.overall_risk_score:.0f}
      </span>
    </div>
  </div>
  {score_bar(report.overall_risk_score, color, 6)}
  <div style="margin-top:10px">{cat_html}</div>
  <div style="margin-top:8px;font-size:0.78rem;color:#8b96aa">
    {alerts} active alert{"s" if alerts != 1 else ""}
  </div>
</div>
""", unsafe_allow_html=True)


def _render_alerts_panel(reports):
    """Consolidated alerts from all projects."""
    all_alerts = []
    for report in reports:
        for alert in report.key_alerts:
            all_alerts.append({
                "code":  report.project_code,
                "level": report.risk_level.value,
                "text":  alert
            })

    if not all_alerts:
        st.markdown(
            '<div style="color:#10b981;padding:20px;text-align:center">'
            '✅ No active alerts</div>',
            unsafe_allow_html=True
        )
        return

    # Sort by risk level severity
    level_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_alerts.sort(key=lambda a: level_order.get(a["level"], 4))

    for alert in all_alerts[:10]:  # show max 10
        is_critical = alert["level"] == "CRITICAL"
        st.markdown(f"""
<div class="alert-box {'alert-critical' if is_critical else ''}">
  <span style="font-size:0.7rem;color:#8b96aa">{alert['code']}</span><br>
  {alert['text']}
</div>
""", unsafe_allow_html=True)


def _render_market_panel(market_analysis):
    """Market intelligence panel at the bottom of dashboard."""
    sentiment = market_analysis.overall_market_sentiment
    score     = market_analysis.market_risk_score
    color     = risk_color(
        "CRITICAL" if score >= 75 else
        "HIGH"     if score >= 55 else
        "MEDIUM"   if score >= 30 else "LOW"
    )

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:12px;padding:20px">
  <div style="font-size:0.7rem;color:#8b96aa;margin-bottom:8px">
    MARKET RISK SCORE
  </div>
  <div style="font-size:2.5rem;font-weight:700;color:{color}">
    {score:.0f}<span style="font-size:1rem;color:#8b96aa">/100</span>
  </div>
  <div style="font-size:0.85rem;color:{color};font-weight:600;
       margin-bottom:12px">{sentiment}</div>
  <div style="font-size:0.82rem;color:#c0c8d8;line-height:1.5">
    {market_analysis.it_sector_outlook[:200]}...
  </div>
</div>
""", unsafe_allow_html=True)

    with col2:
        for trend in market_analysis.key_trends:
            st.markdown(f"""
<div style="background:#1e2130;border-left:3px solid {color};
     padding:10px 14px;border-radius:0 8px 8px 0;
     margin-bottom:8px;font-size:0.85rem;color:#c0c8d8">
  {trend}
</div>
""", unsafe_allow_html=True)
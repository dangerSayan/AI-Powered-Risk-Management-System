"""
projects.py — Project Deep Dive Page
=====================================
Per-project detail view: risk breakdown, category scores,
evidence, team info, financials, and mitigation strategies.
"""

import streamlit as st
from frontend.state import State
from frontend.styles import risk_badge, risk_color, score_bar
import plotly.graph_objects as go


def render_projects():
    st.markdown(
        '<h2 style="color:#e2e8f0;margin-bottom:4px">Project Analysis</h2>'
        '<p style="color:#8b96aa;font-size:0.9rem;margin-bottom:24px">'
        'Deep-dive risk analysis for each project</p>',
        unsafe_allow_html=True
    )

    analysis = State.get_analysis()
    if not analysis:
        st.info("Run an analysis from the sidebar to see project details.")
        return

    # ── Project selector tabs ──────────────────────────────────
    reports_sorted = sorted(
        analysis.risk_reports,
        key=lambda r: r.overall_risk_score,
        reverse=True
    )
    tab_labels = [
        f"{r.project_code} · {r.overall_risk_score:.0f}"
        for r in reports_sorted
    ]
    tabs = st.tabs(tab_labels)

    for tab, report in zip(tabs, reports_sorted):
        with tab:
            _render_project_detail(report)


def _render_project_detail(report):
    """Full detail view for one project."""

    color = risk_color(report.risk_level.value)
    badge = risk_badge(report.risk_level.value)

    # ── Header ─────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:12px;padding:20px;margin-bottom:20px">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-size:1.3rem;font-weight:700;color:#e2e8f0">
        {report.project_name}
      </div>
      <div style="color:#8b96aa;font-size:0.85rem;margin-top:2px">
        {report.project_code} · Generated {report.generated_at.strftime('%d %b %Y %H:%M')}
      </div>
    </div>
    <div style="text-align:right">
      {badge}
      <div style="font-size:2.5rem;font-weight:700;color:{color};line-height:1">
        {report.overall_risk_score:.0f}
        <span style="font-size:1rem;color:#8b96aa">/100</span>
      </div>
    </div>
  </div>
  <div style="margin-top:14px;font-size:0.88rem;color:#c0c8d8;line-height:1.6">
    {report.executive_summary}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Alerts ─────────────────────────────────────────────────
    if report.key_alerts:
        st.markdown(
            '<div class="section-header">Active Alerts</div>',
            unsafe_allow_html=True
        )
        for alert in report.key_alerts:
            is_crit = "🚨" in alert
            st.markdown(f"""
<div class="alert-box {'alert-critical' if is_crit else ''}">
  {alert}
</div>
""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts: radar + category breakdown ─────────────────────
    chart_col, scores_col = st.columns([2, 3])

    with chart_col:
        st.markdown(
            '<div class="section-header">Risk Radar</div>',
            unsafe_allow_html=True
        )
        _render_radar(report)

    with scores_col:
        st.markdown(
            '<div class="section-header">Category Breakdown</div>',
            unsafe_allow_html=True
        )
        _render_category_bars(report)

    # ── Risk Factor Evidence ───────────────────────────────────
    st.markdown(
        '<div class="section-header">Risk Factor Evidence</div>',
        unsafe_allow_html=True
    )
    sorted_factors = sorted(
        report.risk_factors,
        key=lambda f: f.impact_score,
        reverse=True
    )
    cols = st.columns(2)
    for i, factor in enumerate(sorted_factors):
        with cols[i % 2]:
            fcolor = risk_color(
                "CRITICAL" if factor.impact_score >= 75 else
                "HIGH"     if factor.impact_score >= 55 else
                "MEDIUM"   if factor.impact_score >= 30 else "LOW"
            )
            evidence_html = "".join(
                f'<li style="color:#c0c8d8;font-size:0.82rem;'
                f'margin-bottom:4px">{ev}</li>'
                for ev in factor.evidence
            )
            st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:10px;padding:14px;margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:8px">
    <span style="font-weight:600;color:#e2e8f0;font-size:0.88rem">
      {factor.category.value}
    </span>
    <span style="font-size:1.1rem;font-weight:700;color:{fcolor}">
      {factor.impact_score:.0f}
    </span>
  </div>
  {score_bar(factor.impact_score, fcolor)}
  <ul style="margin:10px 0 0 16px;padding:0">{evidence_html}</ul>
</div>
""", unsafe_allow_html=True)

    # ── Mitigation Strategies ──────────────────────────────────
    if report.mitigation_strategies:
        st.markdown(
            '<div class="section-header">Mitigation Action Plan</div>',
            unsafe_allow_html=True
        )
        for m in report.mitigation_strategies:
            effort_color = (
                "#e84545" if m.effort == "High" else
                "#f59e0b" if m.effort == "Medium" else
                "#10b981"
            )
            st.markdown(f"""
<div style="background:#1e2130;border:1px solid #2d3348;
     border-radius:10px;padding:16px;margin-bottom:10px;
     border-left:3px solid #3b82f6">
  <div style="display:flex;justify-content:space-between;
       margin-bottom:8px">
    <span style="background:#0d1f3d;color:#3b82f6;font-size:0.72rem;
         font-weight:600;padding:2px 10px;border-radius:12px">
      PRIORITY {m.priority}
    </span>
    <div style="display:flex;gap:8px;font-size:0.75rem">
      <span style="color:{effort_color}">⚡ {m.effort} Effort</span>
      <span style="color:#10b981">
        ↓{m.estimated_risk_reduction:.0f} pts
      </span>
    </div>
  </div>
  <div style="color:#e2e8f0;font-size:0.88rem;margin-bottom:8px">
    {m.action}
  </div>
  <div style="display:flex;gap:16px;font-size:0.78rem;color:#8b96aa">
    <span>👤 {m.owner}</span>
    <span>⏱ {m.timeline}</span>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_radar(report):
    """Spider/radar chart of category scores."""
    cats   = list(report.category_scores.keys())
    scores = list(report.category_scores.values())

    # Close the polygon
    cats_closed   = cats + [cats[0]]
    scores_closed = scores + [scores[0]]

    fig = go.Figure(go.Scatterpolar(
        r=scores_closed,
        theta=cats_closed,
        fill="toself",
        fillcolor=f"rgba{tuple(int(risk_color(report.risk_level.value).lstrip('#')[i:i+2], 16) for i in (0,2,4)) + (0.2,)}",
        line_color=risk_color(report.risk_level.value),
        line_width=2,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color="#8b96aa", size=9),
                gridcolor="#2d3348"
            ),
            angularaxis=dict(
                tickfont=dict(color="#e2e8f0", size=10),
                gridcolor="#2d3348"
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=30, b=30),
        height=250,
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def _render_category_bars(report):
    """Horizontal bars for each risk category."""
    sorted_cats = sorted(
        report.category_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    for cat, score in sorted_cats:
        c = risk_color(
            "CRITICAL" if score >= 75 else
            "HIGH"     if score >= 55 else
            "MEDIUM"   if score >= 30 else "LOW"
        )
        st.markdown(f"""
<div style="margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;
       font-size:0.82rem;margin-bottom:4px">
    <span style="color:#c0c8d8">{cat}</span>
    <span style="color:{c};font-weight:600">{score:.0f}</span>
  </div>
  {score_bar(score, c)}
</div>
""", unsafe_allow_html=True)
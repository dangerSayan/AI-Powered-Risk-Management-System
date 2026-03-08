"""
projects.py — Project Deep Dive Page
=====================================
Per-project detail view: risk breakdown, category scores,
evidence, team info, financials, and mitigation strategies.
"""

import streamlit as st
import plotly.graph_objects as go
from frontend.state import State
from frontend.styles import risk_badge, risk_color, score_bar


def render_projects():
    st.markdown("""
<div class="rp-page-header">
  <div class="rp-page-title">Project Analysis</div>
  <div class="rp-page-subtitle">
    Deep-dive risk analysis for each IT project
  </div>
</div>
""", unsafe_allow_html=True)

    analysis = State.get_analysis()
    if not analysis:
        st.info("Run an analysis first from the ⚙️ Run Analysis tab.")
        return

    reports_sorted = sorted(
        analysis.risk_reports,
        key=lambda r: r.overall_risk_score,
        reverse=True
    )

    tab_labels = [
        f"{r.project_code}  ·  {r.overall_risk_score:.0f}"
        for r in reports_sorted
    ]
    tabs = st.tabs(tab_labels)

    for tab, report in zip(tabs, reports_sorted):
        with tab:
            _render_project_detail(report)


def _render_project_detail(report):
    color = risk_color(report.risk_level.value)
    badge = risk_badge(report.risk_level.value)

    # ── Header card ────────────────────────────────────────────
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:14px;padding:22px 24px;margin-bottom:20px;
     border-left:4px solid {color}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="font-size:1.25rem;font-weight:700;color:var(--text-primary);
           letter-spacing:-0.02em">{report.project_name}</div>
      <div style="color:var(--text-muted);font-size:0.72rem;margin-top:4px;
           font-family:'JetBrains Mono',monospace;letter-spacing:0.05em">
        {report.project_code} &nbsp;·&nbsp;
        Generated {report.generated_at.strftime('%d %b %Y  %H:%M')}
      </div>
    </div>
    <div style="text-align:right;display:flex;align-items:center;gap:12px">
      {badge}
      <div style="font-size:2.8rem;font-weight:700;color:{color};
           font-family:'JetBrains Mono',monospace;line-height:1">
        {report.overall_risk_score:.0f}
        <span style="font-size:1rem;color:var(--text-muted);font-weight:400">/100</span>
      </div>
    </div>
  </div>
  <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border);
       font-size:0.86rem;color:var(--text-secondary);line-height:1.7">
    {report.executive_summary}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Alerts ─────────────────────────────────────────────────
    if report.key_alerts:
        st.markdown('<div class="section-header">Active Alerts</div>',
                    unsafe_allow_html=True)
        for alert in report.key_alerts:
            is_crit = "🚨" in alert or "CRITICAL" in alert.upper()
            st.markdown(f"""
<div class="alert-box {'alert-critical' if is_crit else ''}">
  {alert}
</div>
""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ─────────────────────────────────────────────
    chart_col, scores_col = st.columns([2, 3])

    with chart_col:
        st.markdown('<div class="section-header">Risk Radar</div>',
                    unsafe_allow_html=True)
        _render_radar(report)

    with scores_col:
        st.markdown('<div class="section-header">Category Breakdown</div>',
                    unsafe_allow_html=True)
        _render_category_bars(report)

    # ── Evidence cards ─────────────────────────────────────────
    st.markdown('<div class="section-header">Risk Factor Evidence</div>',
                unsafe_allow_html=True)

    sorted_factors = sorted(
        report.risk_factors,
        key=lambda f: f.impact_score, reverse=True
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
                f'<li style="color:var(--text-secondary);font-size:0.81rem;'
                f'margin-bottom:5px;line-height:1.5">{ev}</li>'
                for ev in factor.evidence
            )
            st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:14px 16px;margin-bottom:12px;
     border-top:2px solid {fcolor}">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:8px">
    <span style="font-weight:600;color:var(--text-primary);font-size:0.86rem;
         letter-spacing:0.01em">{factor.category.value}</span>
    <span style="font-size:1.2rem;font-weight:700;color:{fcolor};
         font-family:'JetBrains Mono',monospace">{factor.impact_score:.0f}</span>
  </div>
  {score_bar(factor.impact_score, fcolor, 4)}
  <ul style="margin:10px 0 0 14px;padding:0">{evidence_html}</ul>
</div>
""", unsafe_allow_html=True)

    # ── Mitigation strategies ──────────────────────────────────
    if report.mitigation_strategies:
        st.markdown('<div class="section-header">Mitigation Action Plan</div>',
                    unsafe_allow_html=True)
        for m in report.mitigation_strategies:
            effort_color = (
                "#ff4757" if m.effort == "High" else
                "#ffa502" if m.effort == "Medium" else
                "#00d68f"
            )
            st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:16px 18px;margin-bottom:8px;
     border-left:3px solid var(--medium)">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:10px">
    <span style="background:rgba(59,130,246,0.1);color:var(--medium);
         font-size:0.65rem;font-weight:700;padding:3px 10px;
         border-radius:5px;font-family:'JetBrains Mono',monospace;
         letter-spacing:0.08em;border:1px solid rgba(59,130,246,0.2)">
      P{m.priority}
    </span>
    <div style="display:flex;gap:12px;font-size:0.75rem;align-items:center">
      <span style="color:{effort_color};font-weight:500">
        ⚡ {m.effort}
      </span>
      <span style="color:var(--low);font-weight:500">
        ↓{m.estimated_risk_reduction:.0f} pts
      </span>
    </div>
  </div>
  <div style="color:var(--text-primary);font-size:0.86rem;
       margin-bottom:10px;line-height:1.5">{m.action}</div>
  <div style="display:flex;gap:16px;font-size:0.76rem;color:var(--text-muted)">
    <span>👤 {m.owner}</span>
    <span>⏱ {m.timeline}</span>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_radar(report):
    cats   = list(report.category_scores.keys())
    scores = list(report.category_scores.values())
    cats_closed   = cats + [cats[0]]
    scores_closed = scores + [scores[0]]

    hex_color = risk_color(report.risk_level.value).lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    fig = go.Figure(go.Scatterpolar(
        r=scores_closed,
        theta=cats_closed,
        fill="toself",
        fillcolor=f"rgba({r},{g},{b},0.15)",
        line=dict(color=risk_color(report.risk_level.value), width=2),
        marker=dict(size=4, color=risk_color(report.risk_level.value)),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color="#4a5a72", size=8,
                              family="JetBrains Mono"),
                gridcolor="#1e2a3d",
                linecolor="#1e2a3d",
            ),
            angularaxis=dict(
                tickfont=dict(color="#8496b0", size=10,
                              family="Space Grotesk"),
                gridcolor="#1e2a3d",
                linecolor="#1e2a3d",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=30, b=30),
        height=260,
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def _render_category_bars(report):
    sorted_cats = sorted(
        report.category_scores.items(),
        key=lambda x: x[1], reverse=True
    )
    for cat, score in sorted_cats:
        c = risk_color(
            "CRITICAL" if score >= 75 else
            "HIGH"     if score >= 55 else
            "MEDIUM"   if score >= 30 else "LOW"
        )
        st.markdown(f"""
<div style="margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;
       margin-bottom:5px;align-items:center">
    <span style="color:var(--text-secondary);font-size:0.82rem">{cat}</span>
    <span style="color:{c};font-weight:700;font-size:0.85rem;
         font-family:'JetBrains Mono',monospace">{score:.0f}</span>
  </div>
  {score_bar(score, c, 5)}
</div>
""", unsafe_allow_html=True)
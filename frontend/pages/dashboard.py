"""
dashboard.py — Main Portfolio Dashboard Page
=============================================
Dark Command Center — Professional Risk Intelligence UI
"""

import streamlit as st
import plotly.graph_objects as go
from collections import Counter
from frontend.state import State
from frontend.styles import risk_badge, risk_color, score_bar


def render_dashboard():
    analysis = State.get_analysis()
    if not analysis:
        return

    # ── Page header ────────────────────────────────────────────
    st.markdown("""
<div class="rp-page-header">
  <div class="rp-page-title">Portfolio Dashboard</div>
  <div class="rp-page-subtitle">
    Real-time risk intelligence across all active IT projects
  </div>
</div>
""", unsafe_allow_html=True)

    # ── KPI Cards ──────────────────────────────────────────────
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
  <div style="font-size:0.75rem;color:var(--text-muted);
       font-family:'JetBrains Mono',monospace;letter-spacing:0.08em;
       text-transform:uppercase;margin-bottom:12px">Portfolio Risk</div>
  <div class="kpi-value" style="color:{color}">{portfolio_score:.0f}
    <span style="font-size:1.1rem;color:var(--text-muted);font-weight:400">/100</span>
  </div>
  <div class="kpi-sublabel" style="color:{color};margin-top:6px">{portfolio_level}</div>
  <div style="margin-top:10px">
    {score_bar(portfolio_score, color, 3)}
  </div>
</div>""", unsafe_allow_html=True)

    with col2:
        count = analysis.high_risk_count
        color = "#ff4757" if count >= 3 else "#ffa502" if count >= 1 else "#00d68f"
        st.markdown(f"""
<div class="kpi-card">
  <div style="font-size:0.75rem;color:var(--text-muted);
       font-family:'JetBrains Mono',monospace;letter-spacing:0.08em;
       text-transform:uppercase;margin-bottom:12px">At-Risk Projects</div>
  <div class="kpi-value" style="color:{color}">{count}
    <span style="font-size:1.1rem;color:var(--text-muted);font-weight:400">
      /{analysis.total_projects_analyzed}
    </span>
  </div>
  <div class="kpi-sublabel" style="color:var(--text-muted);margin-top:6px;
       font-size:0.65rem">HIGH / CRITICAL</div>
  <div style="margin-top:10px">
    {score_bar(count / analysis.total_projects_analyzed * 100, color, 3)}
  </div>
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
  <div style="font-size:0.75rem;color:var(--text-muted);
       font-family:'JetBrains Mono',monospace;letter-spacing:0.08em;
       text-transform:uppercase;margin-bottom:12px">Market Risk</div>
  <div class="kpi-value" style="color:{mcolor}">{market_score:.0f}
    <span style="font-size:1.1rem;color:var(--text-muted);font-weight:400">/100</span>
  </div>
  <div class="kpi-sublabel" style="color:{mcolor};margin-top:6px">{sentiment}</div>
  <div style="margin-top:10px">
    {score_bar(market_score, mcolor, 3)}
  </div>
</div>""", unsafe_allow_html=True)

    with col4:
        total_alerts = sum(len(r.key_alerts) for r in analysis.risk_reports)
        acolor = "#ff4757" if total_alerts >= 10 else \
                 "#ffa502" if total_alerts >= 5  else "#00d68f"
        st.markdown(f"""
<div class="kpi-card">
  <div style="font-size:0.75rem;color:var(--text-muted);
       font-family:'JetBrains Mono',monospace;letter-spacing:0.08em;
       text-transform:uppercase;margin-bottom:12px">Active Alerts</div>
  <div class="kpi-value" style="color:{acolor}">{total_alerts}</div>
  <div class="kpi-sublabel" style="color:var(--text-muted);margin-top:6px;
       font-size:0.65rem">ACROSS ALL PROJECTS</div>
  <div style="margin-top:10px">
    {score_bar(min(total_alerts * 5, 100), acolor, 3)}
  </div>
</div>""", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────
    chart_col, donut_col = st.columns([3, 2])

    with chart_col:
        st.markdown('<div class="section-header">Risk Score — All Projects</div>',
                    unsafe_allow_html=True)
        _render_score_chart(analysis.risk_reports)

    with donut_col:
        st.markdown('<div class="section-header">Risk Distribution</div>',
                    unsafe_allow_html=True)
        _render_donut_chart(analysis.risk_reports)

    # ── Project Cards + Alerts ─────────────────────────────────
    cards_col, alerts_col = st.columns([3, 2])

    with cards_col:
        st.markdown('<div class="section-header">Project Status Cards</div>',
                    unsafe_allow_html=True)
        for report in sorted(
            analysis.risk_reports,
            key=lambda r: r.overall_risk_score,
            reverse=True
        ):
            _render_project_card(report)

    with alerts_col:
        st.markdown('<div class="section-header">Active Alerts</div>',
                    unsafe_allow_html=True)
        _render_alerts_panel(analysis.risk_reports)

    # ── Market Intelligence ────────────────────────────────────
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,'
        'var(--border),transparent);margin:24px 0"></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-header">Market Intelligence</div>',
                unsafe_allow_html=True)
    _render_market_panel(analysis.market_analysis)


# ── Chart helpers ─────────────────────────────────────────────

def _render_score_chart(reports):
    sorted_r = sorted(reports, key=lambda r: r.overall_risk_score)
    names    = [r.project_code for r in sorted_r]
    scores   = [r.overall_risk_score for r in sorted_r]
    colors   = [risk_color(r.risk_level.value) for r in sorted_r]

    fig = go.Figure(go.Bar(
        x=scores, y=names,
        orientation="h",
        marker=dict(
            color=colors,
            opacity=0.85,
            line=dict(width=0),
        ),
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        textfont=dict(color="#8496b0", size=11,
                      family="JetBrains Mono"),
    ))

    for x, label, color in [
        (30, "MED", "#3b82f6"),
        (55, "HIGH", "#ffa502"),
        (75, "CRIT", "#ff4757"),
    ]:
        fig.add_vline(
            x=x, line_dash="dot",
            line_color=color, line_width=1,
            annotation_text=label,
            annotation_font_size=9,
            annotation_font_color=color,
        )

    fig.update_layout(
        xaxis=dict(range=[0, 108], showgrid=False,
                   tickfont=dict(color="#4a5a72", size=10,
                                 family="JetBrains Mono"),
                   zeroline=False),
        yaxis=dict(showgrid=False,
                   tickfont=dict(color="#8496b0", size=11,
                                 family="JetBrains Mono"),
                   tickmode="array",
                   tickvals=names),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=48, t=8, b=0),
        height=max(280, len(reports) * 22),
        showlegend=False,
        bargap=0.35,
    )
    st.plotly_chart(fig, width="stretch")


def _render_donut_chart(reports):
    level_counts = Counter(r.risk_level.value for r in reports)
    order  = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    labels = [l for l in order if l in level_counts]
    values = [level_counts[l] for l in labels]
    colors = [risk_color(l) for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.68,
        marker=dict(colors=colors, line=dict(color="#080c14", width=3)),
        textinfo="label+value",
        textfont=dict(color="#e8edf5", size=11,
                      family="Space Grotesk"),
        hovertemplate="%{label}: %{value} projects<extra></extra>",
    ))

    total = len(reports)
    fig.add_annotation(
        text=f"<b style='font-size:22px'>{total}</b><br>"
             f"<span style='font-size:10px;color:#4a5a72'>PROJECTS</span>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(color="#e8edf5", family="JetBrains Mono"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=8, b=0),
        height=280,
        showlegend=True,
        legend=dict(
            font=dict(color="#8496b0", size=11, family="Space Grotesk"),
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.0, y=0.5,
        ),
    )
    st.plotly_chart(fig, width="stretch")


def _render_project_card(report):
    color  = risk_color(report.risk_level.value)
    badge  = risk_badge(report.risk_level.value)
    alerts = len(report.key_alerts)

    top_cats = sorted(
        report.category_scores.items(),
        key=lambda x: x[1], reverse=True
    )[:4]

    cat_html = ""
    for cat, score in top_cats:
        c = risk_color(
            "CRITICAL" if score >= 75 else
            "HIGH"     if score >= 55 else
            "MEDIUM"   if score >= 30 else "LOW"
        )
        cat_html += (
            f'<span style="background:rgba(255,255,255,0.03);'
            f'border:1px solid var(--border);border-radius:5px;'
            f'padding:2px 8px;font-size:0.67rem;color:{c};'
            f'font-family:\'JetBrains Mono\',monospace;'
            f'letter-spacing:0.04em;margin-right:5px">'
            f'{cat[:3]} {score:.0f}</span>'
        )

    alert_dot = (
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'font-size:0.72rem;color:{"#ffa502" if alerts > 0 else "var(--text-muted)"}">'
        f'{"⚠" if alerts > 0 else "✓"} '
        f'{alerts} alert{"s" if alerts != 1 else ""}</span>'
    )

    st.markdown(f"""
<div class="project-card">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:10px">
    <div style="display:flex;align-items:center;gap:10px">
      <div style="width:3px;height:32px;background:{color};
           border-radius:2px;flex-shrink:0"></div>
      <div>
        <div style="font-weight:600;color:var(--text-primary);
             font-size:0.9rem;line-height:1.2">{report.project_name}</div>
        <div style="color:var(--text-muted);font-size:0.72rem;
             font-family:'JetBrains Mono',monospace;margin-top:1px">
          {report.project_code}
        </div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      {badge}
      <span style="font-size:1.5rem;font-weight:700;color:{color};
           font-family:'JetBrains Mono',monospace;line-height:1">
        {report.overall_risk_score:.0f}
      </span>
    </div>
  </div>
  {score_bar(report.overall_risk_score, color, 3)}
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-top:10px">
    <div>{cat_html}</div>
    {alert_dot}
  </div>
</div>
""", unsafe_allow_html=True)


def _render_alerts_panel(reports):
    all_alerts = []
    for report in reports:
        for alert in report.key_alerts:
            all_alerts.append({
                "code":  report.project_code,
                "level": report.risk_level.value,
                "text":  alert,
            })

    if not all_alerts:
        st.markdown("""
<div style="text-align:center;padding:32px 20px;color:var(--low)">
  <div style="font-size:1.5rem;margin-bottom:8px">✓</div>
  <div style="font-size:0.82rem">No active alerts</div>
</div>
""", unsafe_allow_html=True)
        return

    level_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_alerts.sort(key=lambda a: level_order.get(a["level"], 4))

    for alert in all_alerts[:12]:
        is_crit = alert["level"] == "CRITICAL"
        st.markdown(f"""
<div class="alert-box {'alert-critical' if is_crit else ''}">
  <span style="font-size:0.65rem;color:var(--text-muted);
       font-family:'JetBrains Mono',monospace">{alert['code']}</span>
  <div style="margin-top:3px;color:var(--text-secondary)">{alert['text']}</div>
</div>
""", unsafe_allow_html=True)


def _render_market_panel(market_analysis):
    score     = market_analysis.market_risk_score
    sentiment = market_analysis.overall_market_sentiment
    color     = risk_color(
        "CRITICAL" if score >= 75 else
        "HIGH"     if score >= 55 else
        "MEDIUM"   if score >= 30 else "LOW"
    )

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:12px;padding:22px;height:100%">
  <div style="font-size:0.67rem;color:var(--text-muted);letter-spacing:0.1em;
       text-transform:uppercase;font-family:'JetBrains Mono',monospace;
       margin-bottom:14px">Market Risk Score</div>
  <div style="font-size:3rem;font-weight:700;color:{color};
       font-family:'JetBrains Mono',monospace;line-height:1;margin-bottom:4px">
    {score:.0f}
    <span style="font-size:1.2rem;color:var(--text-muted);font-weight:400">/100</span>
  </div>
  <div style="font-size:0.78rem;font-weight:700;color:{color};
       letter-spacing:0.1em;text-transform:uppercase;
       font-family:'JetBrains Mono',monospace;margin-bottom:14px">
    {sentiment}
  </div>
  <div style="margin-bottom:12px">{score_bar(score, color, 4)}</div>
  <div style="font-size:0.8rem;color:var(--text-secondary);line-height:1.6">
    {market_analysis.it_sector_outlook[:220]}...
  </div>
</div>
""", unsafe_allow_html=True)

    with col2:
        for trend in market_analysis.key_trends:
            st.markdown(f"""
<div class="rp-trend-item"
     style="border-left-color:{color}">
  {trend}
</div>
""", unsafe_allow_html=True)
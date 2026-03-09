"""
run_analysis.py — Separate Synthetic vs Real Data Analysis
===========================================================
Two completely separate analysis modes:

  SYNTHETIC — uses only projects.json + market_signals.json (generated data)
              Internal data is IGNORED even if uploaded
              External feeds are IGNORED even if fetched

  REAL      — uses uploaded internal data + fetched external feeds
              Falls back to synthetic for projects with no real data uploaded
              Shows exactly which projects used real vs synthetic

After both are run, shows a side-by-side comparison of score changes.
"""

import streamlit as st
from frontend.state import State


# Session state keys
KEY_SYN_RESULT   = "analysis_synthetic"
KEY_REAL_RESULT  = "analysis_real"
KEY_SYN_RUNNING  = "analysis_syn_running"
KEY_REAL_RUNNING = "analysis_real_running"


def render_run_analysis():

    st.markdown("""
<div class="rp-page-header">
  <div class="rp-page-title">Run Portfolio Analysis</div>
  <div class="rp-page-subtitle">
    Two separate modes — Synthetic baseline · Real data analysis · Side-by-side comparison
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Mode cards ─────────────────────────────────────────────
    col_syn, col_real = st.columns(2)

    with col_syn:
        _render_synthetic_card()

    with col_real:
        _render_real_card()

    # ── Comparison section ─────────────────────────────────────
    syn  = st.session_state.get(KEY_SYN_RESULT)
    real = st.session_state.get(KEY_REAL_RESULT)

    if syn or real:
        st.markdown(
            '<div style="height:1px;background:linear-gradient(90deg,transparent,'
            'var(--border),transparent);margin:28px 0"></div>',
            unsafe_allow_html=True
        )

    if syn and real:
        _render_comparison(syn, real)
    elif syn:
        _render_single_result(syn, "🔵 Synthetic Analysis Results", "#3b82f6")
    elif real:
        _render_single_result(real, "⚡ Real Data Analysis Results", "#00d68f")

    # ── Pipeline steps ─────────────────────────────────────────
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,'
        'var(--border),transparent);margin:28px 0"></div>',
        unsafe_allow_html=True
    )
    _render_pipeline_steps()


# ============================================================
# SYNTHETIC MODE CARD
# ============================================================

def _render_synthetic_card():
    syn = st.session_state.get(KEY_SYN_RESULT)

    st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:14px;padding:20px 22px;height:100%;
     border-top:3px solid #3b82f6">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
    <span style="font-size:1.3rem">🔵</span>
    <div>
      <div style="font-weight:700;color:var(--text-primary);font-size:1rem">
        Synthetic Data Mode
      </div>
      <div style="font-size:0.72rem;color:var(--text-muted);margin-top:1px">
        Baseline · Demo · Always available
      </div>
    </div>
  </div>
  <div style="font-size:0.80rem;color:var(--text-secondary);
       line-height:1.7;margin-bottom:16px">
    Uses the <b style="color:var(--text-primary)">15 generated projects</b>
    and <b style="color:var(--text-primary)">20 synthetic market signals</b>
    from <code style="color:var(--accent);font-size:0.72rem">projects.json</code>.
    <br>
    Ignores any uploaded internal data and any fetched external feeds.
    Use this as your <b style="color:#3b82f6">baseline</b>.
  </div>
</div>
""", unsafe_allow_html=True)

    if syn:
        score = syn.portfolio_risk_score
        level = _get_level(score)
        color = _level_color(level)
        st.markdown(f"""
<div style="background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.2);
     border-radius:8px;padding:10px 14px;margin-top:8px;margin-bottom:8px">
  <div style="font-size:0.68rem;color:#3b82f6;font-family:'JetBrains Mono',monospace;
       letter-spacing:0.08em;margin-bottom:4px">LAST SYNTHETIC RESULT</div>
  <div style="display:flex;gap:16px;align-items:center">
    <div>
      <span style="font-size:1.6rem;font-weight:700;color:{color};
           font-family:'JetBrains Mono',monospace">{score:.0f}</span>
      <span style="font-size:0.8rem;color:var(--text-muted)">/100</span>
    </div>
    <div>
      <div style="font-size:0.75rem;color:var(--text-secondary)">
        {syn.high_risk_count} projects need attention
      </div>
      <div style="font-size:0.68rem;color:var(--text-muted)">
        {syn.total_projects_analyzed} projects · synthetic data only
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    btn_label = "▶  Run Synthetic Analysis" if not syn else "↻  Re-run Synthetic"
    if st.button(btn_label, type="primary", use_container_width=True,
                 key="run_synthetic",
                 disabled=st.session_state.get(KEY_SYN_RUNNING, False)):
        _run_synthetic()


# ============================================================
# REAL DATA MODE CARD
# ============================================================

def _render_real_card():
    from backend.data.realtime_data import InternalDataProcessor

    real        = st.session_state.get(KEY_REAL_RESULT)
    saved       = InternalDataProcessor.load_internal_data()
    ext_fetched = bool(st.session_state.get("live_ext_data"))
    has_data    = bool(saved) or ext_fetched

    # Data availability indicators
    int_indicator = (
        f'<span style="color:#00d68f">✓ {len(saved)} project(s) uploaded</span>'
        if saved else
        '<span style="color:var(--text-muted)">✗ No internal data uploaded</span>'
    )
    ext_indicator = (
        '<span style="color:#00d68f">✓ External feeds fetched</span>'
        if ext_fetched else
        '<span style="color:var(--text-muted)">✗ External feeds not fetched</span>'
    )

    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:14px;padding:20px 22px;height:100%;
     border-top:3px solid {'#00d68f' if has_data else '#ffa502'}">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
    <span style="font-size:1.3rem">⚡</span>
    <div>
      <div style="font-weight:700;color:var(--text-primary);font-size:1rem">
        Real Data Mode
      </div>
      <div style="font-size:0.72rem;color:var(--text-muted);margin-top:1px">
        Live · Accurate · Uses your actual KPIs
      </div>
    </div>
  </div>
  <div style="font-size:0.80rem;color:var(--text-secondary);
       line-height:1.7;margin-bottom:12px">
    Uses <b style="color:var(--text-primary)">uploaded internal KPIs</b>
    and <b style="color:var(--text-primary)">fetched external market data</b>.
    Projects without uploaded data still use synthetic as fallback.
    Compare results with Synthetic to see the <b style="color:#00d68f">real impact</b>.
  </div>
  <div style="font-size:0.75rem;font-family:'JetBrains Mono',monospace;
       display:flex;flex-direction:column;gap:4px;margin-bottom:14px">
    <div>{int_indicator}</div>
    <div>{ext_indicator}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if real:
        score = real.portfolio_risk_score
        level = _get_level(score)
        color = _level_color(level)
        st.markdown(f"""
<div style="background:rgba(0,214,143,0.06);border:1px solid rgba(0,214,143,0.2);
     border-radius:8px;padding:10px 14px;margin-top:8px;margin-bottom:8px">
  <div style="font-size:0.68rem;color:#00d68f;font-family:'JetBrains Mono',monospace;
       letter-spacing:0.08em;margin-bottom:4px">LAST REAL DATA RESULT</div>
  <div style="display:flex;gap:16px;align-items:center">
    <div>
      <span style="font-size:1.6rem;font-weight:700;color:{color};
           font-family:'JetBrains Mono',monospace">{score:.0f}</span>
      <span style="font-size:0.8rem;color:var(--text-muted)">/100</span>
    </div>
    <div>
      <div style="font-size:0.75rem;color:var(--text-secondary)">
        {real.high_risk_count} projects need attention
      </div>
      <div style="font-size:0.68rem;color:var(--text-muted)">
        {real.total_projects_analyzed} projects · real data
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    if not has_data:
        st.caption("Upload internal data or fetch external feeds in the 🌐 Live Data tab first.")

    btn_label = "⚡  Run Real Data Analysis" if not real else "↻  Re-run Real Analysis"
    if st.button(btn_label,
                 type="primary" if has_data else "secondary",
                 use_container_width=True,
                 key="run_real",
                 disabled=st.session_state.get(KEY_REAL_RUNNING, False) or not has_data):
        _run_real()


# ============================================================
# RUNNERS
# ============================================================

def _run_synthetic():
    """Runs analysis with internal data DISABLED."""
    st.session_state[KEY_SYN_RUNNING] = True
    manager = State.get_manager()
    if not manager:
        st.error("Risk Manager not initialized. Refresh the page.")
        st.session_state[KEY_SYN_RUNNING] = False
        return

    with st.spinner("Running synthetic analysis — using generated data only..."):
        try:
            # Temporarily disable internal data by renaming the file
            _toggle_internal_data(disable=True)

            result = manager.run_full_analysis()

            # Re-enable internal data
            _toggle_internal_data(disable=False)

            st.session_state[KEY_SYN_RESULT] = result
            State.set_analysis(result)  # dashboard/projects use this
            st.success(
                f"✅ Synthetic analysis complete — "
                f"Portfolio: {result.portfolio_risk_score:.0f}/100 · "
                f"{result.high_risk_count} projects need attention"
            )
            st.balloons()
        except Exception as e:
            _toggle_internal_data(disable=False)  # always re-enable
            st.error(f"Synthetic analysis failed: {e}")
        finally:
            st.session_state[KEY_SYN_RUNNING] = False
    st.rerun()


def _run_real():
    """Runs analysis with internal data ENABLED."""
    st.session_state[KEY_REAL_RUNNING] = True
    manager = State.get_manager()
    if not manager:
        st.error("Risk Manager not initialized. Refresh the page.")
        st.session_state[KEY_REAL_RUNNING] = False
        return

    with st.spinner("Running real data analysis — using uploaded KPIs + external feeds..."):
        try:
            result = manager.run_full_analysis()
            st.session_state[KEY_REAL_RESULT] = result
            State.set_analysis(result)  # update dashboard with latest
            st.success(
                f"⚡ Real data analysis complete — "
                f"Portfolio: {result.portfolio_risk_score:.0f}/100 · "
                f"{result.high_risk_count} projects need attention"
            )
        except Exception as e:
            st.error(f"Real data analysis failed: {e}")
        finally:
            st.session_state[KEY_REAL_RUNNING] = False
    st.rerun()


def _toggle_internal_data(disable: bool):
    """
    Temporarily renames internal_data.json so the scoring agent
    can't find it → forces pure synthetic run.
    Renamed back immediately after synthetic run completes.

    FIX: Uses the canonical absolute path from realtime_data.py
    instead of a relative path that breaks when CWD != risk_management/.
    """
    from backend.data.realtime_data import INTERNAL_DATA_PATH
    data_path     = INTERNAL_DATA_PATH
    disabled_path = INTERNAL_DATA_PATH.with_suffix(".json.disabled")

    if disable and data_path.exists():
        data_path.rename(disabled_path)
    elif not disable and disabled_path.exists():
        disabled_path.rename(data_path)


# ============================================================
# COMPARISON VIEW
# ============================================================

def _render_comparison(syn, real):
    st.markdown('<div class="section-header">📊 Comparison — Synthetic vs Real Data</div>',
                unsafe_allow_html=True)

    # Portfolio-level comparison
    syn_score  = syn.portfolio_risk_score
    real_score = real.portfolio_risk_score
    diff       = real_score - syn_score
    diff_color = "#ff4757" if diff > 0 else "#00d68f" if diff < 0 else "#8496b0"
    diff_icon  = "▲" if diff > 0 else "▼" if diff < 0 else "="
    diff_label = "Risk INCREASED with real data" if diff > 0 else \
                 "Risk DECREASED with real data" if diff < 0 else \
                 "No change between modes"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid rgba(59,130,246,0.3);
     border-radius:12px;padding:18px;text-align:center;
     border-top:3px solid #3b82f6">
  <div style="font-size:0.68rem;color:#3b82f6;font-family:'JetBrains Mono',monospace;
       letter-spacing:0.1em;margin-bottom:8px">SYNTHETIC PORTFOLIO</div>
  <div style="font-size:2.4rem;font-weight:700;color:{_level_color(_get_level(syn_score))};
       font-family:'JetBrains Mono',monospace;line-height:1">{syn_score:.1f}</div>
  <div style="font-size:0.72rem;color:var(--text-muted);margin-top:4px">
    {_get_level(syn_score)} · {syn.high_risk_count} at risk
  </div>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid rgba({_hex_to_rgb(diff_color)},0.3);
     border-radius:12px;padding:18px;text-align:center;
     border-top:3px solid {diff_color}">
  <div style="font-size:0.68rem;color:{diff_color};font-family:'JetBrains Mono',monospace;
       letter-spacing:0.1em;margin-bottom:8px">DIFFERENCE</div>
  <div style="font-size:2.4rem;font-weight:700;color:{diff_color};
       font-family:'JetBrains Mono',monospace;line-height:1">
    {diff_icon}{abs(diff):.1f}
  </div>
  <div style="font-size:0.68rem;color:var(--text-muted);margin-top:4px;line-height:1.4">
    {diff_label}
  </div>
</div>
""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid rgba(0,214,143,0.3);
     border-radius:12px;padding:18px;text-align:center;
     border-top:3px solid #00d68f">
  <div style="font-size:0.68rem;color:#00d68f;font-family:'JetBrains Mono',monospace;
       letter-spacing:0.1em;margin-bottom:8px">REAL DATA PORTFOLIO</div>
  <div style="font-size:2.4rem;font-weight:700;color:{_level_color(_get_level(real_score))};
       font-family:'JetBrains Mono',monospace;line-height:1">{real_score:.1f}</div>
  <div style="font-size:0.72rem;color:var(--text-muted);margin-top:4px">
    {_get_level(real_score)} · {real.high_risk_count} at risk
  </div>
</div>
""", unsafe_allow_html=True)

    # Per-project comparison table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Per-Project Score Changes</div>',
                unsafe_allow_html=True)

    # Build lookup dicts
    syn_scores  = {r.project_code: r.overall_risk_score for r in syn.risk_reports}
    real_scores = {r.project_code: r.overall_risk_score for r in real.risk_reports}

    # Check which had real data
    from backend.data.realtime_data import InternalDataProcessor
    saved_codes = {r.project_code for r in InternalDataProcessor.load_internal_data()}

    all_codes = sorted(set(list(syn_scores.keys()) + list(real_scores.keys())))

    rows = []
    for code in all_codes:
        s = syn_scores.get(code, 0)
        r = real_scores.get(code, 0)
        d = r - s
        rows.append((code, s, r, d, code in saved_codes))

    # Sort by absolute difference (most changed first)
    rows.sort(key=lambda x: abs(x[3]), reverse=True)

    for code, s, r, d, had_real in rows:
        d_color = "#ff4757" if d > 1 else "#00d68f" if d < -1 else "#8496b0"
        d_icon  = "▲" if d > 1 else "▼" if d < -1 else "─"
        data_badge = (
            '<span style="background:rgba(0,214,143,0.1);color:#00d68f;'
            'font-size:0.6rem;padding:1px 6px;border-radius:3px;'
            'font-family:\'JetBrains Mono\',monospace;'
            'border:1px solid rgba(0,214,143,0.2)">REAL</span>'
        ) if had_real else (
            '<span style="background:rgba(59,130,246,0.08);color:#3b82f6;'
            'font-size:0.6rem;padding:1px 6px;border-radius:3px;'
            'font-family:\'JetBrains Mono\',monospace;'
            'border:1px solid rgba(59,130,246,0.15)">SYNTH</span>'
        )

        # Score bar
        bar_s = f'width:{s:.0f}%'
        bar_r = f'width:{r:.0f}%'

        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:12px 16px;margin-bottom:6px">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:8px">
    <div style="display:flex;align-items:center;gap:8px">
      <span style="font-family:'JetBrains Mono',monospace;font-weight:700;
           color:var(--text-primary);font-size:0.84rem">{code}</span>
      {data_badge}
    </div>
    <div style="display:flex;align-items:center;gap:14px">
      <span style="font-size:0.78rem;color:#3b82f6;
           font-family:'JetBrains Mono',monospace">{s:.1f}</span>
      <span style="font-size:0.88rem;font-weight:700;color:{d_color};
           font-family:'JetBrains Mono',monospace">{d_icon} {abs(d):.1f}</span>
      <span style="font-size:0.78rem;color:#00d68f;
           font-family:'JetBrains Mono',monospace">{r:.1f}</span>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:3px">
    <div style="height:4px;background:rgba(59,130,246,0.15);border-radius:2px">
      <div style="{bar_s};height:4px;background:#3b82f6;border-radius:2px;
           max-width:100%"></div>
    </div>
    <div style="height:4px;background:rgba(0,214,143,0.1);border-radius:2px">
      <div style="{bar_r};height:4px;background:#00d68f;border-radius:2px;
           max-width:100%"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Legend
    st.markdown("""
<div style="display:flex;gap:16px;margin-top:8px;font-size:0.70rem;color:var(--text-muted)">
  <span><span style="color:#3b82f6">━</span> Synthetic score</span>
  <span><span style="color:#00d68f">━</span> Real data score</span>
  <span><span style="color:#ff4757">▲</span> Risk increased</span>
  <span><span style="color:#00d68f">▼</span> Risk decreased</span>
  <span><span style="color:#00d68f">REAL</span> Used uploaded data</span>
</div>
""", unsafe_allow_html=True)


def _render_single_result(result, title: str, color: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

    score = result.portfolio_risk_score
    cols  = st.columns(4)
    kpis  = [
        ("Portfolio Score",    f"{score:.1f}/100",                   color),
        ("Risk Level",         _get_level(score),                    _level_color(_get_level(score))),
        ("Projects at Risk",   str(result.high_risk_count),          "#ff4757" if result.high_risk_count > 3 else "#ffa502"),
        ("Projects Analyzed",  str(result.total_projects_analyzed),  "#8496b0"),
    ]
    for col, (label, value, c) in zip(cols, kpis):
        with col:
            st.markdown(f"""
<div class="kpi-card">
  <div style="font-size:0.68rem;color:var(--text-muted);
       font-family:'JetBrains Mono',monospace;letter-spacing:0.08em;
       text-transform:uppercase;margin-bottom:10px">{label}</div>
  <div style="font-size:1.6rem;font-weight:700;color:{c};
       font-family:'JetBrains Mono',monospace;line-height:1">{value}</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# PIPELINE STEPS
# ============================================================

def _render_pipeline_steps():
    st.markdown('<div class="section-header">Analysis Pipeline</div>',
                unsafe_allow_html=True)

    steps = [
        ("01", "📂", "Data Loading",
         "Synthetic: loads projects.json + market_signals.json · Real: loads uploaded internal KPIs"),
        ("02", "🌐", "Market Analysis Agent",
         "Synthetic: uses 20 generated signals · Real: also uses cached external feeds (RBI, World Bank, news)"),
        ("03", "📊", "Project Status Agent",
         "Evaluates schedule, budget, team, and client KPIs for all 15 projects"),
        ("04", "🔢", "Risk Scoring Agent × 15",
         "Synthetic: pure generated data · Real: uploaded KPIs override synthetic fields per project"),
        ("05", "📈", "Portfolio Aggregation",
         "Weighted average across all projects → stored in ChromaDB for AI Chat"),
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
       font-family:'JetBrains Mono',monospace;flex-shrink:0;margin-top:1px">{num}</div>
  <div>
    <div style="font-size:0.88rem;font-weight:600;color:var(--text-primary);
         margin-bottom:3px">{icon} {title}</div>
    <div style="font-size:0.8rem;color:var(--text-secondary);line-height:1.5">{desc}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def _get_level(score: float) -> str:
    if score >= 75: return "CRITICAL"
    if score >= 55: return "HIGH"
    if score >= 30: return "MEDIUM"
    return "LOW"


def _level_color(level: str) -> str:
    return {"CRITICAL": "#ff4757", "HIGH": "#ffa502",
            "MEDIUM": "#3b82f6", "LOW": "#00d68f"}.get(level, "#8496b0")


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
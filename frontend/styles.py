"""
styles.py — Global CSS Theming for RiskPulse AI
"""

def get_css() -> str:
    return """
<style>
/* ── Base theme ─────────────────────────────────── */
.stApp { background-color: #0f1117; color: #e2e8f0; }

/* ── Hide sidebar completely ────────────────────── */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── KPI metric cards ───────────────────────────── */
.kpi-card {
    background: #1e2130;
    border: 1px solid #2d3348;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    margin-bottom: 12px;
}
.kpi-value {
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 0.78rem;
    color: #8b96aa;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Risk level colors ──────────────────────────── */
.risk-critical { color: #e84545 !important; }
.risk-high     { color: #f59e0b !important; }
.risk-medium   { color: #3b82f6 !important; }
.risk-low      { color: #10b981 !important; }

/* ── Risk badge pills ───────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-critical { background: #3d1515; color: #e84545; border: 1px solid #e84545; }
.badge-high     { background: #3d2c0a; color: #f59e0b; border: 1px solid #f59e0b; }
.badge-medium   { background: #0d1f3d; color: #3b82f6; border: 1px solid #3b82f6; }
.badge-low      { background: #0d2b1f; color: #10b981; border: 1px solid #10b981; }

/* ── Project cards ──────────────────────────────── */
.project-card {
    background: #1e2130;
    border: 1px solid #2d3348;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}

/* ── Alert boxes ────────────────────────────────── */
.alert-box {
    background: #1e1a10;
    border-left: 4px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.88rem;
}
.alert-critical {
    background: #1e1010;
    border-left-color: #e84545;
}

/* ── Chat bubbles ───────────────────────────────── */
.chat-user {
    background: #1e3a5f;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    margin: 8px 0 8px 40px;
    font-size: 0.92rem;
}
.chat-assistant {
    background: #1e2130;
    border: 1px solid #2d3348;
    border-radius: 16px 16px 16px 4px;
    padding: 12px 16px;
    margin: 8px 40px 8px 0;
    font-size: 0.92rem;
}

/* ── Section headers ────────────────────────────── */
.section-header {
    font-size: 0.72rem;
    font-weight: 600;
    color: #8b96aa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid #2d3348;
}

/* ── Progress bars ──────────────────────────────── */
.progress-track {
    background: #2d3348;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
    margin: 4px 0;
}
.progress-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.4s ease;
}

/* ── Hide default Streamlit chrome ──────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Streamlit metric overrides ─────────────────── */
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* ── Tab styling ────────────────────────────────── */
[data-testid="stTabs"] {
    margin-top: 0;
}
</style>
"""


def risk_badge(level: str) -> str:
    level_lower = level.lower()
    return f'<span class="badge badge-{level_lower}">{level}</span>'


def risk_color(level: str) -> str:
    colors = {
        "CRITICAL": "#e84545",
        "HIGH":     "#f59e0b",
        "MEDIUM":   "#3b82f6",
        "LOW":      "#10b981",
    }
    return colors.get(level.upper(), "#8b96aa")


def score_bar(score: float, color: str, height: int = 8) -> str:
    return f"""
<div class="progress-track" style="height:{height}px">
  <div class="progress-fill"
       style="width:{score}%;background:{color};height:{height}px">
  </div>
</div>"""
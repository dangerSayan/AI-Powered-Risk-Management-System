"""
styles.py — Global CSS Theming for RiskPulse AI
Dark Command Center — Professional Risk Intelligence UI
"""

def get_css() -> str:
    return """
<style>
/* ── Google Fonts ───────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── CSS Variables ──────────────────────────────── */
:root {
    --bg-base:       #080c14;
    --bg-surface:    #0d1220;
    --bg-card:       #111827;
    --bg-card-hover: #141d2e;
    --bg-input:      #0d1220;
    --border:        #1e2a3d;
    --border-bright: #2a3a54;
    --text-primary:  #e8edf5;
    --text-secondary:#8496b0;
    --text-muted:    #4a5a72;
    --accent:        #00c2ff;
    --accent-dim:    rgba(0,194,255,0.08);
    --accent-glow:   rgba(0,194,255,0.25);
    --critical:      #ff4757;
    --high:          #ffa502;
    --medium:        #3b82f6;
    --low:           #00d68f;
    --critical-bg:   rgba(255,71,87,0.08);
    --high-bg:       rgba(255,165,2,0.08);
    --medium-bg:     rgba(59,130,246,0.08);
    --low-bg:        rgba(0,214,143,0.08);
    --font-main:    'Space Grotesk', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;
}

/* ── Base ───────────────────────────────────────── */
.stApp {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
}

/* ── Hide sidebar & chrome ──────────────────────── */
[data-testid="stSidebar"]       { display: none !important; }
[data-testid="collapsedControl"]{ display: none !important; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Remove default padding ─────────────────────── */
.block-container {
    padding-top: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px !important;
}

/* ── Tabs ───────────────────────────────────────── */
[data-testid="stTabs"] { margin-top: 0; }

[data-testid="stTabs"] > div:first-child {
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    padding: 0 0.5rem;
    gap: 0;
}

button[data-baseweb="tab"] {
    font-family: var(--font-main) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    padding: 14px 22px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em !important;
    background: transparent !important;
}

button[data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: var(--accent-dim) !important;
}

button[aria-selected="true"][data-baseweb="tab"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    background: var(--accent-dim) !important;
    font-weight: 600 !important;
}

/* ── Top navbar ─────────────────────────────────── */
.rp-navbar {
    background: linear-gradient(90deg, #080c14 0%, #0a1220 100%);
    border-bottom: 1px solid var(--border);
    padding: 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -2rem 0 -2rem;
    position: sticky;
    top: 0;
    z-index: 999;
}

.rp-navbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.rp-navbar-logo {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #0066ff 0%, #00c2ff 100%);
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    box-shadow: 0 0 16px rgba(0,194,255,0.35);
    flex-shrink: 0;
}

.rp-navbar-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    line-height: 1.2;
}

.rp-navbar-sub {
    font-size: 0.62rem;
    color: var(--text-muted);
    font-family: var(--font-mono);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.rp-navbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.rp-status-pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 14px;
    display: flex;
    align-items: center;
    gap: 7px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-secondary);
}

.rp-dot-live {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--low);
    box-shadow: 0 0 8px var(--low);
    animation: blink 2s infinite;
}

.rp-dot-off {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--critical);
}

@keyframes blink {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--low); }
    50%       { opacity: 0.5; box-shadow: 0 0 3px var(--low); }
}

/* ── Page header ─────────────────────────────────── */
.rp-page-header {
    padding: 26px 0 20px 0;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border);
}

.rp-page-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 0 0 4px 0;
}

.rp-page-subtitle {
    font-size: 0.83rem;
    color: var(--text-secondary);
    margin: 0;
}

/* ── KPI Cards ──────────────────────────────────── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.2s;
}

.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, var(--accent) 50%, transparent 100%);
    opacity: 0.4;
}

.kpi-card:hover {
    border-color: var(--border-bright);
    transform: translateY(-2px);
}

.kpi-value {
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
    font-family: var(--font-mono);
    letter-spacing: -0.03em;
    margin-bottom: 3px;
}

.kpi-sublabel {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 6px;
    font-family: var(--font-mono);
}

.kpi-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 500;
}

/* ── Section header ─────────────────────────────── */
.section-header {
    font-size: 0.67rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.13em;
    margin-bottom: 14px;
    padding-bottom: 9px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-header::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 11px;
    background: var(--accent);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── Project cards ──────────────────────────────── */
.project-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 8px;
    transition: all 0.2s ease;
    position: relative;
}

.project-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-bright);
    transform: translateX(2px);
}

/* ── Alert boxes ────────────────────────────────── */
.alert-box {
    background: rgba(255,165,2,0.05);
    border: 1px solid rgba(255,165,2,0.15);
    border-left: 3px solid var(--high);
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-bottom: 7px;
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.5;
    transition: background 0.2s;
}

.alert-box:hover { background: rgba(255,165,2,0.1); }

.alert-critical {
    background: rgba(255,71,87,0.05) !important;
    border-color: rgba(255,71,87,0.15) !important;
    border-left-color: var(--critical) !important;
}

.alert-critical:hover { background: rgba(255,71,87,0.1) !important; }

/* ── Risk badges ────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 9px;
    border-radius: 5px;
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: var(--font-mono);
}

.badge-critical { background: var(--critical-bg); color: var(--critical); border: 1px solid rgba(255,71,87,0.25); }
.badge-high     { background: var(--high-bg);     color: var(--high);     border: 1px solid rgba(255,165,2,0.25); }
.badge-medium   { background: var(--medium-bg);   color: var(--medium);   border: 1px solid rgba(59,130,246,0.25); }
.badge-low      { background: var(--low-bg);      color: var(--low);      border: 1px solid rgba(0,214,143,0.25); }

/* ── Chat bubbles ───────────────────────────────── */
.chat-user {
    background: linear-gradient(135deg, rgba(0,102,255,0.15), rgba(0,194,255,0.08));
    border: 1px solid rgba(0,194,255,0.15);
    border-radius: 14px 14px 4px 14px;
    padding: 13px 17px;
    margin: 10px 0 10px 48px;
    font-size: 0.9rem;
    line-height: 1.6;
}

.chat-assistant {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px 14px 14px 4px;
    padding: 13px 17px;
    margin: 10px 48px 10px 0;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ── Progress bars ──────────────────────────────── */
.progress-track {
    background: var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin: 4px 0;
}

.progress-fill {
    height: 100%;
    border-radius: 8px;
    position: relative;
    overflow: hidden;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    animation: shimmer 2.5s infinite;
}

@keyframes shimmer {
    to { left: 200%; }
}

/* ── Buttons ────────────────────────────────────── */
.stButton > button {
    font-family: var(--font-main) !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
    font-size: 0.85rem !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0055ee, #00aaff) !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(0,170,255,0.25) !important;
    color: white !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,194,255,0.35) !important;
}

.stButton > button[kind="secondary"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-secondary) !important;
}

.stButton > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Inputs ──────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: var(--font-main) !important;
    font-size: 0.88rem !important;
}

[data-testid="stChatInput"] textarea,
.stChatInput textarea {
    background: var(--bg-card) !important;
    border-color: var(--border-bright) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    font-family: var(--font-main) !important;
}

/* ── Streamlit alerts ───────────────────────────── */
.stAlert {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    font-family: var(--font-main) !important;
}

/* ── Spinner ─────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Scrollbar ──────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
"""


def risk_badge(level: str) -> str:
    level_lower = level.lower()
    return f'<span class="badge badge-{level_lower}">{level}</span>'


def risk_color(level: str) -> str:
    colors = {
        "CRITICAL": "#ff4757",
        "HIGH":     "#ffa502",
        "MEDIUM":   "#3b82f6",
        "LOW":      "#00d68f",
        "MARKET":   "#8496b0",
    }
    return colors.get(level.upper(), "#8496b0")


def score_bar(score: float, color: str, height: int = 6) -> str:
    return f"""
<div class="progress-track" style="height:{height}px">
  <div class="progress-fill"
       style="width:{min(score,100)}%;background:{color};height:{height}px">
  </div>
</div>"""
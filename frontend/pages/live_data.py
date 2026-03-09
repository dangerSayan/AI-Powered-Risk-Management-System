"""
live_data.py — Real-Time Data & Internal Integration Page
==========================================================
FIXES in this version:
  1. Clear button uses InternalDataProcessor.clear_internal_data() — no path bug
  2. Manual form uses free text project code — not locked to PRJ-xxx
  3. AI Smart Converter tab — paste ANY text, AI extracts structured data
  4. Internal data + external data feed into analysis via integration hooks
  5. FIX: CSV upload guard — file_id prevents reprocessing on every rerun
"""

import streamlit as st
import json
import os
from datetime import datetime
from frontend.state import State


KEY_EXT_DATA      = "live_ext_data"
KEY_LAST_FETCH    = "live_last_fetch"
KEY_FETCHING      = "live_is_fetching"
KEY_AI_RESULT     = "live_ai_result"
KEY_AI_LOADING    = "live_ai_loading"
KEY_CSV_PROCESSED = "live_csv_processed_id"   # FIX: guard against rerun loop


def render_live_data():

    st.markdown("""
<div class="rp-page-header">
  <div class="rp-page-title">Live Data & Integrations</div>
  <div class="rp-page-subtitle">
    Real-time external feeds · AI-powered data converter · Internal KPI upload · Integration connectors
  </div>
</div>
""", unsafe_allow_html=True)

    ext_tab, int_tab, hub_tab = st.tabs([
        "  🌐  External Market Feeds  ",
        "  🏢  Internal Data Upload  ",
        "  🔌  Integrations Hub  ",
    ])

    with ext_tab:
        _render_external_tab()

    with int_tab:
        _render_internal_tab()

    with hub_tab:
        _render_integrations_tab()


# ============================================================
# TAB 1 — EXTERNAL MARKET FEEDS
# ============================================================

def _render_external_tab():

    col_text, col_btn = st.columns([4, 1])
    with col_text:
        last_fetch = st.session_state.get(KEY_LAST_FETCH)
        if last_fetch:
            st.markdown(
                f'<div style="font-size:0.75rem;color:var(--text-muted);'
                f'font-family:\'JetBrains Mono\',monospace;padding:6px 0">'
                f'Last updated: {last_fetch}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="font-size:0.78rem;color:var(--text-muted);padding:6px 0">'
                'Click <b>Fetch Live Data</b> to pull real-time market signals. '
                'Results are cached for 1 hour and used in the next Run Analysis.</div>',
                unsafe_allow_html=True
            )

    with col_btn:
        fetch_btn = st.button(
            "⟳  Fetch Live Data",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get(KEY_FETCHING, False)
        )

    if fetch_btn:
        _do_fetch()

    ext_data = st.session_state.get(KEY_EXT_DATA)

    if not ext_data:
        _render_sources_preview()
        return

    _render_external_kpis(ext_data)
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,'
        'var(--border),transparent);margin:20px 0"></div>',
        unsafe_allow_html=True
    )

    st.markdown("""
<div style="background:rgba(0,194,255,0.05);border:1px solid rgba(0,194,255,0.2);
     border-radius:8px;padding:10px 14px;margin-bottom:16px;
     display:flex;align-items:center;gap:10px">
  <span style="font-size:1rem">⚡</span>
  <span style="font-size:0.78rem;color:var(--text-secondary)">
    This data is automatically used in the next
    <b style="color:var(--accent)">Run Analysis</b> —
    exchange rate and macro indicators enrich the market risk score.
  </span>
</div>
""", unsafe_allow_html=True)

    macro  = ext_data.get("macro", [])
    market = ext_data.get("market", [])
    tech   = ext_data.get("tech", [])
    news   = ext_data.get("news", [])

    if macro:
        st.markdown('<div class="section-header">Macro Indicators</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(macro), 4))
        for i, dp in enumerate(macro):
            with cols[i % len(cols)]:
                _render_data_tile(dp)

    if market:
        st.markdown('<div class="section-header">Market Data</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(market), 4))
        for i, dp in enumerate(market):
            with cols[i % len(cols)]:
                _render_data_tile(dp)

    if tech:
        st.markdown('<div class="section-header">Tech Trends</div>', unsafe_allow_html=True)
        for dp in tech:
            _render_tech_trends(dp)

    if news:
        st.markdown('<div class="section-header">IT News Feed</div>', unsafe_allow_html=True)
        neg = [n for n in news if n.sentiment == "negative"]
        pos = [n for n in news if n.sentiment == "positive"]
        neu = [n for n in news if n.sentiment == "neutral"]
        for dp in (neg + neu + pos)[:12]:
            _render_news_card(dp)


def _do_fetch():
    st.session_state[KEY_FETCHING] = True
    with st.spinner("Fetching live data from external sources..."):
        try:
            from backend.data.realtime_data import ExternalDataFetcher
            data = ExternalDataFetcher.fetch_all()
            st.session_state[KEY_EXT_DATA]   = data
            st.session_state[KEY_LAST_FETCH] = datetime.now().strftime("%d %b %Y %H:%M:%S")
            total = sum(len(v) for v in data.values())
            live  = sum(1 for items in data.values() for dp in items if dp.is_live)
            st.success(f"✅ Fetched {total} data points ({live} live) — will be used in next Run Analysis")
        except Exception as e:
            st.error(f"Fetch failed: {e}")
        finally:
            st.session_state[KEY_FETCHING] = False
    st.rerun()


def _render_sources_preview():
    sources = [
        ("🏦", "Reserve Bank of India",  "Repo rate, monetary policy",         "Free · No key"),
        ("🌍", "World Bank Open Data",   "India GDP, inflation, unemployment",  "Free · No key"),
        ("💱", "Frankfurter / ECB",      "USD/INR exchange rate, daily",        "Free · No key"),
        ("📈", "NSE / Yahoo Finance",    "Nifty IT, TCS, Infosys, Wipro",      "Free · pip install yfinance"),
        ("📰", "ET, Moneycontrol, NDTV", "IT sector news RSS feeds",            "Free · pip install feedparser"),
        ("💻", "GitHub Trending",        "Top programming languages today",     "Free · No key"),
    ]
    st.markdown('<div class="section-header">Available Data Sources</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (icon, name, desc, badge) in enumerate(sources):
        with cols[i % 2]:
            st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:14px 16px;margin-bottom:8px;
     display:flex;align-items:flex-start;gap:12px">
  <div style="font-size:1.4rem;flex-shrink:0">{icon}</div>
  <div>
    <div style="font-weight:600;color:var(--text-primary);font-size:0.88rem;margin-bottom:2px">{name}</div>
    <div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:6px">{desc}</div>
    <span style="background:var(--low-bg);color:var(--low);font-size:0.62rem;font-weight:700;
         padding:2px 8px;border-radius:4px;font-family:'JetBrains Mono',monospace;
         border:1px solid rgba(0,214,143,0.2)">{badge}</span>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_external_kpis(data):
    from frontend.styles import risk_color
    macro  = data.get("macro", [])
    market = data.get("market", [])
    news   = data.get("news", [])
    total     = sum(len(v) for v in data.values())
    live      = sum(1 for items in data.values() for d in items if d.is_live)
    neg_news  = sum(1 for d in news if d.sentiment == "negative")
    neg_color = "#ff4757" if neg_news >= 4 else "#ffa502" if neg_news >= 2 else "#00d68f"
    usd_inr   = next((d for d in market if "USD/INR" in d.label), None)
    rate_val  = f"₹{usd_inr.value}" if usd_inr else "—"
    rate_color = "#ff4757" if usd_inr and usd_inr.value > 86 else \
                 "#00d68f" if usd_inr else "#8496b0"

    cols = st.columns(4)
    kpis = [
        ("Data Points",      str(total),   "#3b82f6",  f"{live} live"),
        ("USD/INR",          rate_val,     rate_color, "Exchange rate"),
        ("Negative Signals", str(neg_news), neg_color, "of news items"),
        ("Sources Active",   str(len([k for k,v in data.items() if v])), "#00d68f", "data streams"),
    ]
    for col, (label, value, color, sub) in zip(cols, kpis):
        with col:
            st.markdown(f"""
<div class="kpi-card">
  <div style="font-size:0.68rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace;
       letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px">{label}</div>
  <div style="font-size:1.9rem;font-weight:700;color:{color};
       font-family:'JetBrains Mono',monospace;line-height:1;margin-bottom:3px">{value}</div>
  <div style="font-size:0.68rem;color:var(--text-muted)">{sub}</div>
</div>
""", unsafe_allow_html=True)


def _render_data_tile(dp):
    color = "#00d68f" if dp.sentiment == "positive" else \
            "#ff4757" if dp.sentiment == "negative" else "#8496b0"
    live_dot = (
        '<span style="display:inline-block;width:5px;height:5px;border-radius:50%;'
        'background:var(--low);box-shadow:0 0 6px var(--low);margin-right:4px;'
        'animation:blink 2s infinite"></span>' if dp.is_live else
        '<span style="display:inline-block;width:5px;height:5px;border-radius:50%;'
        'background:var(--text-muted);margin-right:4px"></span>'
    )
    val_display = f"{dp.value}{dp.unit}" if isinstance(dp.value, (int, float)) else str(dp.value)
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;
     padding:16px;margin-bottom:10px;border-top:2px solid {color}">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <div style="font-size:0.65rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace;
         display:flex;align-items:center">{live_dot}{dp.source}</div>
  </div>
  <div style="font-size:1.6rem;font-weight:700;color:{color};
       font-family:'JetBrains Mono',monospace;line-height:1;margin-bottom:4px">{val_display}</div>
  <div style="font-size:0.76rem;color:var(--text-secondary);line-height:1.4">{dp.label}</div>
  {f'<div style="font-size:0.68rem;color:var(--text-muted);margin-top:4px">{dp.error}</div>' if dp.error and dp.is_live else ""}
</div>
""", unsafe_allow_html=True)


def _render_tech_trends(dp):
    langs = dp.value if isinstance(dp.value, list) else [dp.value]
    pills = "".join(
        f'<span style="background:rgba(0,194,255,0.08);border:1px solid rgba(0,194,255,0.2);'
        f'color:var(--accent);font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;'
        f'padding:3px 10px;border-radius:5px;margin-right:6px;margin-bottom:6px;'
        f'display:inline-block">{lang}</span>' for lang in langs
    )
    live_dot = (
        '<span style="display:inline-block;width:5px;height:5px;border-radius:50%;'
        'background:var(--low);box-shadow:0 0 6px var(--low);margin-right:5px"></span>'
        if dp.is_live else ""
    )
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;
     padding:16px;margin-bottom:10px">
  <div style="font-size:0.68rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace;
       margin-bottom:10px;display:flex;align-items:center">{live_dot}{dp.source} · {dp.label}</div>
  <div>{pills}</div>
</div>
""", unsafe_allow_html=True)


def _render_news_card(dp):
    sc   = "#00d68f" if dp.sentiment == "positive" else \
           "#ff4757" if dp.sentiment == "negative" else "#8496b0"
    icon = "▼" if dp.sentiment == "negative" else \
           "▲" if dp.sentiment == "positive" else "●"
    url_html = (
        f'<a href="{dp.source_url}" target="_blank" '
        f'style="font-size:0.68rem;color:var(--accent);text-decoration:none">Read →</a>'
    ) if dp.source_url else ""
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:9px;
     padding:12px 14px;margin-bottom:7px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:5px">
    <div style="font-weight:600;color:var(--text-primary);font-size:0.84rem;
         line-height:1.4;flex:1;margin-right:12px">{dp.label}</div>
    <span style="color:{sc};font-size:0.68rem;font-weight:700;
         font-family:'JetBrains Mono',monospace;white-space:nowrap">
      {icon} {dp.sentiment.upper()}
    </span>
  </div>
  <div style="font-size:0.78rem;color:var(--text-secondary);line-height:1.5;margin-bottom:6px">{dp.value}</div>
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:0.65rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace">{dp.source}</span>
    {url_html}
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# TAB 2 — INTERNAL DATA UPLOAD
# ============================================================

def _render_internal_tab():
    from backend.data.realtime_data import InternalDataProcessor, SAMPLE_AI_INPUT, SAMPLE_JSON_TEMPLATE

    st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:16px 18px;margin-bottom:20px">
  <div style="font-size:0.88rem;color:var(--text-secondary);line-height:1.7">
    Upload your company's real project KPIs here. RiskPulse AI will use this data
    <b style="color:var(--text-primary)">instead of synthetic estimates</b> for those projects
    in the next Run Analysis — giving you accurate, real risk scores.
    <br><br>
    <b style="color:var(--accent)">✨ New:</b> Use the AI Converter — paste any messy text
    (email, meeting notes, Jira export, WhatsApp update) and the AI extracts structured data automatically.
  </div>
</div>
""", unsafe_allow_html=True)

    ai_tab, csv_tab, json_tab, manual_tab = st.tabs([
        "  ✨  AI Smart Converter  ",
        "  📂  CSV / Excel Upload  ",
        "  { }  JSON Paste  ",
        "  ✏️  Manual Entry  ",
    ])

    with ai_tab:
        _render_ai_converter_tab(SAMPLE_AI_INPUT)

    # ── CSV Upload ─────────────────────────────────────────────
    with csv_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
<div style="font-size:0.82rem;color:var(--text-secondary);margin-bottom:14px;line-height:1.7">
  Upload a CSV or Excel file. <b>Column names are flexible</b> — we accept common variations
  like <code>velocity</code>, <code>story_points</code>, <code>bugs</code>, <code>defects</code>, etc.
  Download the template to see all accepted column names.
</div>
""", unsafe_allow_html=True)

        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                "⬇  Download Template",
                data=InternalDataProcessor.get_template_csv(),
                file_name="riskpulse_internal_template.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload your CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Flexible column mapping — no exact column names required"
        )

        # ── FIX: file_id guard prevents processing on every rerun ──────
        if uploaded:
            file_id = f"{uploaded.name}_{uploaded.size}"
            already_processed = st.session_state.get(KEY_CSV_PROCESSED) == file_id

            if not already_processed:
                with st.spinner("Parsing file..."):
                    records = InternalDataProcessor.parse_csv_upload(uploaded.read(), uploaded.name)
                if records:
                    st.success(f"✅ Parsed {len(records)} project records")
                    _merge_and_save(records)
                    st.session_state[KEY_CSV_PROCESSED] = file_id  # mark done — won't fire again
                    st.rerun()
                else:
                    st.error("Could not parse file. Try the AI Converter tab instead — just paste the content.")
            else:
                st.info("✅ File already processed. Upload a different file, or use Clear Data below to reset.")

    # ── JSON Paste ─────────────────────────────────────────────
    with json_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        json_input = st.text_area(
            "JSON Input",
            value=SAMPLE_JSON_TEMPLATE,
            height=280,
            label_visibility="collapsed"
        )
        col1, _ = st.columns([1, 3])
        with col1:
            if st.button("✓  Parse & Save", type="primary",
                         use_container_width=True, key="parse_json"):
                records = InternalDataProcessor.parse_json_input(json_input)
                if records:
                    _merge_and_save(records)
                    st.success(f"✅ Saved {len(records)} records")
                    st.rerun()
                else:
                    st.error("Invalid JSON. Check the format.")

    # ── Manual Entry ───────────────────────────────────────────
    with manual_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        _render_manual_form()

    # ── Saved data section ─────────────────────────────────────
    saved = InternalDataProcessor.load_internal_data()
    if saved:
        st.markdown(
            '<div style="height:1px;background:linear-gradient(90deg,transparent,'
            'var(--border),transparent);margin:24px 0"></div>',
            unsafe_allow_html=True
        )

        st.markdown(f"""
<div style="background:rgba(0,214,143,0.05);border:1px solid rgba(0,214,143,0.2);
     border-radius:8px;padding:10px 14px;margin-bottom:16px;
     display:flex;align-items:center;gap:10px">
  <span style="font-size:1rem">⚡</span>
  <span style="font-size:0.78rem;color:var(--text-secondary)">
    <b style="color:var(--low)">{len(saved)} project records saved.</b>
    These will override synthetic data in the next
    <b style="color:var(--accent)">Run Analysis</b>.
  </span>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">Saved Internal Data</div>',
                    unsafe_allow_html=True)
        _render_internal_preview(saved)

        col1, _ = st.columns([1, 4])
        with col1:
            if st.button("🗑  Clear All Internal Data", key="clear_internal",
                         type="secondary", use_container_width=True):
                InternalDataProcessor.clear_internal_data()
                # Also reset CSV guard so the same file can be re-uploaded after clearing
                st.session_state.pop(KEY_CSV_PROCESSED, None)
                st.success("Internal data cleared.")
                st.rerun()


def _merge_and_save(new_records):
    """Merges new records with existing, deduplicating by project_code."""
    from backend.data.realtime_data import InternalDataProcessor
    existing = InternalDataProcessor.load_internal_data()
    new_codes = {r.project_code for r in new_records}
    kept = [e for e in existing if e.project_code not in new_codes]
    InternalDataProcessor.save_internal_data(kept + new_records)


def _render_ai_converter_tab(sample_text: str):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div style="background:rgba(0,194,255,0.04);border:1px solid rgba(0,194,255,0.15);
     border-radius:10px;padding:14px 16px;margin-bottom:16px">
  <div style="font-size:0.88rem;font-weight:600;color:var(--accent);margin-bottom:6px">
    ✨ AI Smart Converter — paste anything
  </div>
  <div style="font-size:0.80rem;color:var(--text-secondary);line-height:1.7">
    Don't fill forms. Just paste your raw project data in any format:
    a status update email, meeting notes, a Jira export paragraph,
    a WhatsApp message from your PM, or numbers copy-pasted from Excel.
    The AI reads it and extracts structured KPI data automatically.
  </div>
</div>
""", unsafe_allow_html=True)

    raw_input = st.text_area(
        "Paste your project data here (any format)",
        value=sample_text,
        height=260,
        help="Email, meeting notes, Jira export, WhatsApp message, Excel paste — anything works",
        label_visibility="collapsed",
        placeholder="Paste any project status text here..."
    )

    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        convert_btn = st.button(
            "✨  Convert with AI",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get(KEY_AI_LOADING, False)
        )
    with col2:
        if st.session_state.get(KEY_AI_RESULT):
            save_btn = st.button(
                "💾  Save Extracted Data",
                type="secondary",
                use_container_width=True,
                key="save_ai_result"
            )
            if save_btn:
                records = st.session_state[KEY_AI_RESULT]
                _merge_and_save(records)
                st.success(f"✅ Saved {len(records)} projects to analysis pipeline")
                st.session_state.pop(KEY_AI_RESULT, None)
                st.rerun()

    if convert_btn and raw_input.strip():
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            st.error("GROQ_API_KEY not found in .env — AI conversion needs it.")
            return

        st.session_state[KEY_AI_LOADING] = True
        with st.spinner("AI is reading your text and extracting structured data..."):
            try:
                from backend.data.realtime_data import InternalDataProcessor
                records = InternalDataProcessor.ai_convert(raw_input, groq_key)
                st.session_state[KEY_AI_RESULT] = records
                st.session_state[KEY_AI_LOADING] = False
                st.success(f"✅ AI extracted {len(records)} project records — review below, then click Save")
            except Exception as e:
                st.error(f"AI conversion failed: {e}")
                st.session_state[KEY_AI_LOADING] = False
        st.rerun()

    if st.session_state.get(KEY_AI_RESULT):
        st.markdown(
            '<div class="section-header">Extracted Data — Review Before Saving</div>',
            unsafe_allow_html=True
        )
        _render_internal_preview(st.session_state[KEY_AI_RESULT])


def _render_manual_form():
    from backend.data.realtime_data import InternalDataProcessor

    st.markdown("""
<div style="font-size:0.80rem;color:var(--text-secondary);margin-bottom:16px;line-height:1.6">
  Enter KPIs for one project at a time.
  Use <b>your own project code</b> — no restriction on format.
</div>
""", unsafe_allow_html=True)

    with st.form("manual_internal_form"):
        col1, col2 = st.columns(2)
        with col1:
            project_code  = st.text_input("Project Code", placeholder="e.g. PRJ-001, HDFC-MOB-01, Atlas")
            project_name  = st.text_input("Project Name (optional)", placeholder="e.g. Mobile Banking App")
            client_name   = st.text_input("Client Name (optional)", placeholder="e.g. HDFC Bank")
            sprint_vel    = st.number_input("Sprint Velocity (story points)", 0, 500, 0)
            open_bugs     = st.number_input("Open Bugs", 0, 10000, 0)
            open_tickets  = st.number_input("Open Tickets", 0, 10000, 0)
            open_risks    = st.number_input("Open Risk Items", 0, 500, 0)

        with col2:
            team_size     = st.number_input("Team Size", 0, 500, 0)
            delay_days    = st.number_input("Schedule Delay (days)", 0, 500, 0)
            budget_pct    = st.number_input("Budget Utilization %", 0.0, 200.0, 0.0)
            csat          = st.number_input("Customer Satisfaction / NPS (0-100)", 0.0, 100.0, 0.0)
            actual_hrs    = st.number_input("Actual Hours This Week", 0.0, 5000.0, 0.0)
            avail_hrs     = st.number_input("Team Available Hours This Week", 0.0, 5000.0, 0.0)
            inv_raised    = st.number_input("Invoices Raised This Month (₹)", 0.0, 1e9, 0.0, step=10000.0)
            inv_paid      = st.number_input("Invoices Paid This Month (₹)", 0.0, 1e9, 0.0, step=10000.0)

        notes = st.text_input("Notes (optional)")

        submitted = st.form_submit_button("💾  Save Entry", type="primary")

        if submitted:
            if not project_code.strip():
                st.error("Project Code is required.")
            else:
                kpis = {
                    "project_name":               project_name or None,
                    "client_name":                client_name  or None,
                    "sprint_velocity":            sprint_vel   or None,
                    "open_bugs":                  open_bugs    or None,
                    "open_tickets":               open_tickets or None,
                    "open_risks":                 open_risks   or None,
                    "team_size":                  team_size    or None,
                    "schedule_delay_days":        delay_days   or None,
                    "budget_utilization_pct":     budget_pct   or None,
                    "customer_satisfaction":      csat         or None,
                    "actual_hours_this_week":     actual_hrs   or None,
                    "team_available_hours":       avail_hrs    or None,
                    "invoices_raised_this_month": inv_raised   or None,
                    "invoices_paid_this_month":   inv_paid     or None,
                    "notes":                      notes,
                }
                record = InternalDataProcessor.manual_to_internal(project_code, kpis)
                _merge_and_save([record])
                st.success(f"✅ Saved data for {project_code}")
                st.rerun()


def _render_internal_preview(records):
    if not records:
        return
    for rec in records:
        util = None
        if rec.actual_hours_this_week and rec.team_available_hours and rec.team_available_hours > 0:
            util = (rec.actual_hours_this_week / rec.team_available_hours) * 100

        inv_health = None
        if rec.invoices_raised_this_month and rec.invoices_raised_this_month > 0:
            if rec.invoices_paid_this_month is not None:
                inv_health = (rec.invoices_paid_this_month / rec.invoices_raised_this_month) * 100

        pills = []
        if rec.sprint_velocity:         pills.append(("Velocity", f"{rec.sprint_velocity:.0f} pts", "#00d68f" if rec.sprint_velocity > 30 else "#ffa502"))
        if rec.open_bugs:               pills.append(("Bugs", str(rec.open_bugs), "#ff4757" if rec.open_bugs > 20 else "#ffa502" if rec.open_bugs > 5 else "#00d68f"))
        if rec.open_tickets:            pills.append(("Tickets", str(rec.open_tickets), "#ffa502"))
        if rec.schedule_delay_days:     pills.append(("Delay", f"{rec.schedule_delay_days}d", "#ff4757" if rec.schedule_delay_days > 10 else "#ffa502"))
        if rec.budget_utilization_pct:  pills.append(("Budget", f"{rec.budget_utilization_pct:.0f}%", "#ff4757" if rec.budget_utilization_pct > 85 else "#ffa502" if rec.budget_utilization_pct > 70 else "#00d68f"))
        if rec.customer_satisfaction:   pills.append(("CSAT", f"{rec.customer_satisfaction:.0f}", "#ff4757" if rec.customer_satisfaction < 40 else "#ffa502" if rec.customer_satisfaction < 65 else "#00d68f"))
        if util:                        pills.append(("Utilization", f"{util:.0f}%", "#ffa502" if util < 80 else "#00d68f"))
        if inv_health is not None:      pills.append(("Payment", f"{inv_health:.0f}%", "#ff4757" if inv_health < 50 else "#ffa502" if inv_health < 80 else "#00d68f"))

        pill_html = "".join(
            f'<span style="background:rgba({_hex_to_rgb(c)},0.1);border:1px solid rgba({_hex_to_rgb(c)},0.3);'
            f'color:{c};font-size:0.68rem;padding:3px 9px;border-radius:5px;'
            f'font-family:\'JetBrains Mono\',monospace;margin-right:5px;margin-bottom:4px;display:inline-block">'
            f'{label}: {val}</span>'
            for label, val, c in pills
        )

        src_colors = {
            "AI Converted": ("#a78bfa", "rgba(167,139,250,0.1)"),
            "Manual Form":  ("#3b82f6", "rgba(59,130,246,0.1)"),
        }
        sc, sbg = src_colors.get(
            rec.source_system.split(":")[0],
            ("#8496b0", "rgba(132,150,176,0.1)")
        )

        name_line = f" — {rec.project_name}" if rec.project_name else ""
        client_line = f" · {rec.client_name}" if rec.client_name else ""

        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;
     padding:14px 16px;margin-bottom:8px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <div>
      <span style="font-weight:700;color:var(--text-primary);
           font-family:'JetBrains Mono',monospace;font-size:0.88rem">{rec.project_code}</span>
      <span style="font-size:0.80rem;color:var(--text-secondary)">{name_line}{client_line}</span>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <span style="background:{sbg};color:{sc};font-size:0.62rem;font-weight:600;
           padding:2px 8px;border-radius:4px;font-family:'JetBrains Mono',monospace;
           border:1px solid rgba(132,150,176,0.2)">{rec.source_system}</span>
      <span style="font-size:0.62rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace">
        {rec.uploaded_at[:16]}
      </span>
    </div>
  </div>
  <div style="flex-wrap:wrap;margin-bottom:{8 if rec.notes else 0}px">{pill_html}</div>
  {'<div style="font-size:0.75rem;color:var(--text-muted);margin-top:6px">' + rec.notes + '</div>' if rec.notes else ''}
</div>
""", unsafe_allow_html=True)


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


# ============================================================
# TAB 3 — INTEGRATIONS HUB
# ============================================================

def _render_integrations_tab():
    from backend.data.realtime_data import INTEGRATION_STUBS

    st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:10px;padding:16px 18px;margin-bottom:20px">
  <div style="font-size:0.88rem;color:var(--text-secondary);line-height:1.7">
    Connect your existing tools for <b style="color:var(--text-primary)">automatic data sync</b>
    — no manual uploads needed. Add API credentials to your
    <code style="background:rgba(0,194,255,0.08);color:var(--accent);
    padding:1px 5px;border-radius:3px">.env</code> file and
    these connectors pull live data on every analysis run.
    <br>
    <span style="color:var(--text-muted);font-size:0.78rem">
      All marked <b style="color:#ffa502">Planned</b> —
      wire them in when you're ready to connect real systems.
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

    for name, config in INTEGRATION_STUBS.items():
        _render_integration_card(name, config)


def _render_integration_card(name: str, config: dict):
    fields_html = "".join(
        f'<span style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.15);'
        f'color:#3b82f6;font-size:0.65rem;padding:2px 7px;border-radius:4px;'
        f'font-family:\'JetBrains Mono\',monospace;margin-right:5px;margin-bottom:4px;'
        f'display:inline-block">{f}</span>'
        for f in config.get("fields", [])
    )
    docs_html = (
        f'<a href="{config["docs"]}" target="_blank" '
        f'style="font-size:0.72rem;color:var(--accent);text-decoration:none;'
        f'font-family:\'JetBrains Mono\',monospace">Docs →</a>'
    ) if config.get("docs") else ""
    icons = {
        "Jira": "🟦", "GitHub": "🐙", "Freshdesk": "🎫",
        "Zoho Books / QuickBooks": "💰", "Google Sheets": "📊",
        "SAP / Oracle ERP": "🏭",
    }
    icon = icons.get(name, "🔌")
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;
     padding:18px 20px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
    <div style="display:flex;align-items:center;gap:12px">
      <div style="font-size:1.5rem">{icon}</div>
      <div>
        <div style="font-weight:700;color:var(--text-primary);font-size:0.92rem">{name}</div>
        <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:2px">{config['description']}</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;flex-shrink:0">
      <span style="background:rgba(255,165,2,0.1);color:#ffa502;font-size:0.62rem;font-weight:700;
           padding:3px 9px;border-radius:5px;font-family:'JetBrains Mono',monospace;
           border:1px solid rgba(255,165,2,0.25)">PLANNED</span>
      {docs_html}
    </div>
  </div>
  <div style="margin-bottom:10px">{fields_html}</div>
  <div style="background:rgba(0,0,0,0.2);border-radius:6px;padding:8px 12px;
       font-size:0.72rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace">
    {config['setup']}
  </div>
</div>
""", unsafe_allow_html=True)
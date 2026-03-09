"""
realtime_data.py — Real-Time External & Internal Data Fetcher
==============================================================
Fetches live data from FREE public sources:

EXTERNAL (no API key needed):
  1. RSS/News feeds — Economic Times IT, Moneycontrol, NASSCOM
  2. World Bank API — India GDP, inflation indicators
  3. Frankfurter / ECB — USD/INR rate
  4. Yahoo Finance (yfinance) — Nifty IT index + TCS/Infosys/Wipro
  5. RBI — India policy rate
  6. GitHub Trending — tech stack trend signals

INTERNAL (company uploads their own data):
  1. AI Smart Converter — paste ANY format, AI converts to our schema
  2. CSV/Excel upload — auto-mapped, no exact column names needed
  3. JSON paste — flexible schema
  4. Manual form — free text project code entry

RISK ANALYSIS INTEGRATION:
  - Internal data enriches risk scores via get_enriched_project_data()
  - External macro/market signals feed into market_analysis_agent
  - All data tagged with is_live flag so analysis knows what's real vs synthetic
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from backend.models.schemas import MarketSignal
from datetime import datetime
from dataclasses import dataclass, asdict, field
from loguru import logger


# ── Canonical save path (single source of truth) ─────────────
# realtime_data.py lives at: backend/data/realtime_data.py
# So parent = backend/data, parent.parent = backend, parent.parent.parent = risk_management
# internal_data.json saved at: risk_management/data/internal_data.json
_THIS_FILE  = Path(__file__).resolve()
_BACKEND_DATA_DIR = _THIS_FILE.parent          # backend/data/
_PROJECT_ROOT     = _THIS_FILE.parent.parent.parent  # risk_management/
DATA_DIR          = _PROJECT_ROOT / "data"
INTERNAL_DATA_PATH = DATA_DIR / "internal_data.json"
CACHE_DIR          = DATA_DIR / "realtime_cache"
CACHE_TTL          = 3600  # 1 hour


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class DataPoint:
    """One piece of real-time data from any source."""
    source:      str
    category:    str          # "macro", "market", "internal", "news", "tech"
    label:       str
    value:       Any
    unit:        str = ""
    sentiment:   str = "neutral"
    severity:    str = "low"
    timestamp:   str = field(default_factory=lambda: datetime.now().isoformat())
    source_url:  str = ""
    is_live:     bool = True
    error:       str = ""


@dataclass
class InternalProjectData:
    """
    Internal project KPIs uploaded by the company.
    project_code is FREE TEXT — no restriction to PRJ-xxx format.
    Companies can use their own codes: HDFC-MOB-01, TCS-ERP-2024, etc.
    """
    project_code:               str
    source_system:              str    # "AI Converted", "CSV", "JSON", "Manual"
    project_name:               Optional[str]  = None
    client_name:                Optional[str]  = None
    sprint_velocity:            Optional[float] = None
    open_bugs:                  Optional[int]   = None
    open_tickets:               Optional[int]   = None
    actual_hours_this_week:     Optional[float] = None
    team_available_hours:       Optional[float] = None
    invoices_raised_this_month: Optional[float] = None
    invoices_paid_this_month:   Optional[float] = None
    team_size:                  Optional[int]   = None
    schedule_delay_days:        Optional[int]   = None
    budget_utilization_pct:     Optional[float] = None
    open_risks:                 Optional[int]   = None
    customer_satisfaction:      Optional[float] = None  # NPS or CSAT score
    custom_kpis:                Dict[str, Any]  = field(default_factory=dict)
    uploaded_at:                str = field(default_factory=lambda: datetime.now().isoformat())
    notes:                      str = ""
    raw_input:                  str = ""   # stores original pasted text for audit


# ============================================================
# CACHE
# ============================================================

def _cache_key(name: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{name}.json"


def _read_cache(name: str) -> Optional[Any]:
    path = _cache_key(name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if time.time() - data["ts"] < CACHE_TTL:
            return data["value"]
    except Exception:
        pass
    return None


def _write_cache(name: str, value: Any):
    try:
        _cache_key(name).write_text(json.dumps({"ts": time.time(), "value": value}))
    except Exception:
        pass


# ============================================================
# EXTERNAL DATA FETCHERS
# ============================================================

class ExternalDataFetcher:

    RSS_FEEDS = {
        "Economic Times IT":     "https://economictimes.indiatimes.com/tech/information-tech/rssfeeds/13357270.cms",
        "Moneycontrol Tech":     "https://www.moneycontrol.com/rss/technology.xml",
        "NDTV Gadgets":          "https://feeds.feedburner.com/NdtvGadgets360",
        "LiveMint Tech":         "https://www.livemint.com/rss/technology",
        "Hindu BusinessLine IT": "https://www.thehindubusinessline.com/info-tech/?service=rss",
    }

    IT_KEYWORDS = [
        "IT", "tech", "software", "cloud", "digital", "startup",
        "layoff", "hiring", "salary", "attrition", "outsourcing",
        "AI", "artificial intelligence", "cybersecurity", "data",
        "fintech", "SaaS", "ERP", "infosys", "wipro", "TCS",
        "NASSCOM", "RBI", "rupee", "inflation", "GDP"
    ]

    NEGATIVE_WORDS = [
        "layoff", "cut", "loss", "decline", "fall", "crash", "risk",
        "breach", "hack", "penalty", "fine", "delay", "slowdown",
        "recession", "inflation", "attrition", "resign", "fraud"
    ]

    POSITIVE_WORDS = [
        "growth", "hire", "expand", "profit", "revenue", "invest",
        "launch", "innovation", "record", "surge", "boost", "win",
        "award", "partnership", "deal", "contract"
    ]

    @classmethod
    def fetch_news(cls, max_items: int = 15) -> List[DataPoint]:
        cached = _read_cache("rss_news")
        if cached:
            return [DataPoint(**d) for d in cached]

        results = []
        try:
            import feedparser
            for feed_name, url in cls.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:4]:
                        title   = entry.get("title", "")
                        summary = entry.get("summary", "")[:200]
                        link    = entry.get("link", "")
                        combined = (title + " " + summary).lower()
                        if not any(kw.lower() in combined for kw in cls.IT_KEYWORDS):
                            continue
                        neg = sum(1 for w in cls.NEGATIVE_WORDS if w in combined)
                        pos = sum(1 for w in cls.POSITIVE_WORDS if w in combined)
                        sentiment = "negative" if neg > pos else \
                                    "positive" if pos > neg else "neutral"
                        results.append(DataPoint(
                            source=feed_name, category="news",
                            label=title[:80], value=summary,
                            sentiment=sentiment,
                            severity="high" if neg >= 2 else "medium" if neg == 1 else "low",
                            source_url=link, is_live=True,
                        ))
                    if len(results) >= max_items:
                        break
                except Exception as e:
                    logger.warning(f"RSS feed failed ({feed_name}): {e}")
        except ImportError:
            results = cls._fallback_news()

        _write_cache("rss_news", [asdict(d) for d in results])
        return results[:max_items]

    @classmethod
    def _fallback_news(cls) -> List[DataPoint]:
        return [DataPoint(
            source="Static Fallback", category="news",
            label="Live news unavailable — install feedparser",
            value="Run: pip install feedparser to enable live RSS news feeds.",
            sentiment="neutral", severity="low", is_live=False,
            error="feedparser not installed"
        )]

    WB_INDICATORS = {
        "NY.GDP.MKTP.KD.ZG": ("India GDP Growth Rate", "%", "macro"),
        "FP.CPI.TOTL.ZG":    ("India Inflation Rate",  "%", "macro"),
        "SL.UEM.TOTL.ZS":    ("India Unemployment Rate", "%", "macro"),
    }

    @classmethod
    def fetch_world_bank(cls) -> List[DataPoint]:
        cached = _read_cache("world_bank")
        if cached:
            return [DataPoint(**d) for d in cached]

        results = []
        try:
            import requests
            for code, (label, unit, category) in cls.WB_INDICATORS.items():
                url = f"https://api.worldbank.org/v2/country/IN/indicator/{code}?format=json&mrv=1"
                try:
                    r = requests.get(url, timeout=8)
                    r.raise_for_status()
                    data = r.json()
                    if data and len(data) > 1 and data[1]:
                        item  = data[1][0]
                        value = item.get("value")
                        year  = item.get("date", "")
                        if value is not None:
                            if label == "India GDP Growth Rate":
                                sentiment = "positive" if value > 6 else "neutral" if value > 4 else "negative"
                            elif label == "India Inflation Rate":
                                sentiment = "positive" if value < 4 else "neutral" if value < 6 else "negative"
                            else:
                                sentiment = "neutral"
                            results.append(DataPoint(
                                source="World Bank", category=category,
                                label=f"{label} ({year})", value=round(float(value), 2),
                                unit=unit, sentiment=sentiment, severity="low",
                                source_url=f"https://data.worldbank.org/indicator/{code}?locations=IN",
                                is_live=True,
                            ))
                except Exception as e:
                    logger.warning(f"World Bank {code} failed: {e}")
        except ImportError:
            pass

        if not results:
            results = [
                DataPoint(source="World Bank", category="macro",
                          label="India GDP Growth Rate (2023)", value=8.2,
                          unit="%", sentiment="positive", is_live=False,
                          error="API unavailable — showing last known value"),
                DataPoint(source="World Bank", category="macro",
                          label="India Inflation Rate (2023)", value=5.4,
                          unit="%", sentiment="neutral", is_live=False),
            ]

        _write_cache("world_bank", [asdict(d) for d in results])
        return results

    @classmethod
    def fetch_rbi_rate(cls) -> List[DataPoint]:
        cached = _read_cache("rbi_rate")
        if cached:
            return [DataPoint(**d) for d in cached]

        results = []
        try:
            import requests
            url = "https://api.rbi.org.in/api/v1/KeyRates"
            r = requests.get(url, timeout=8, headers={"Accept": "application/json"})
            r.raise_for_status()
            data = r.json()
            for item in data.get("data", []):
                if "Repo" in item.get("name", ""):
                    rate = float(item.get("value", 6.5))
                    results.append(DataPoint(
                        source="Reserve Bank of India", category="macro",
                        label="RBI Repo Rate", value=rate, unit="%",
                        sentiment="neutral" if rate <= 6.5 else "negative",
                        severity="medium",
                        source_url="https://www.rbi.org.in",
                        is_live=True,
                    ))
                    break
        except Exception as e:
            results = [DataPoint(
                source="Reserve Bank of India", category="macro",
                label="RBI Repo Rate (last known)", value=6.5, unit="%",
                sentiment="neutral", severity="low", is_live=False, error=str(e)
            )]

        _write_cache("rbi_rate", [asdict(d) for d in results])
        return results

    @classmethod
    def fetch_exchange_rate(cls) -> List[DataPoint]:
        cached = _read_cache("exchange_rate")
        if cached:
            return [DataPoint(**d) for d in cached]

        results = []
        try:
            import requests
            r = requests.get("https://api.frankfurter.app/latest?from=USD&to=INR", timeout=8)
            r.raise_for_status()
            data = r.json()
            rate = data["rates"]["INR"]
            results.append(DataPoint(
                source="Frankfurter / ECB", category="market",
                label=f"USD/INR Rate ({data['date']})", value=round(rate, 2),
                unit="₹",
                sentiment="negative" if rate > 86 else "neutral" if rate > 83 else "positive",
                severity="medium" if rate > 86 else "low",
                source_url="https://www.frankfurter.app", is_live=True,
            ))
        except Exception as e:
            results = [DataPoint(
                source="ECB / Frankfurter", category="market",
                label="USD/INR Rate (fallback)", value=84.20,
                unit="₹", sentiment="neutral", is_live=False, error=str(e)
            )]

        _write_cache("exchange_rate", [asdict(d) for d in results])
        return results

    @classmethod
    def fetch_nifty_it(cls) -> List[DataPoint]:
        cached = _read_cache("nifty_it")
        if cached:
            return [DataPoint(**d) for d in cached]

        results = []
        try:
            import yfinance as yf
            ticker = yf.Ticker("^CNXIT")
            hist   = ticker.history(period="5d")
            if not hist.empty:
                latest = hist["Close"].iloc[-1]
                prev   = hist["Close"].iloc[-2] if len(hist) > 1 else latest
                change = ((latest - prev) / prev) * 100
                results.append(DataPoint(
                    source="NSE / Yahoo Finance", category="market",
                    label="Nifty IT Index", value=round(latest, 0), unit="points",
                    sentiment="positive" if change > 0.5 else "negative" if change < -0.5 else "neutral",
                    severity="medium" if abs(change) > 2 else "low",
                    source_url="https://finance.yahoo.com/quote/%5ECNXIT/",
                    is_live=True, error=f"Day change: {change:+.2f}%"
                ))
                for sym, name in [("INFY.NS","Infosys"),("TCS.NS","TCS"),("WIPRO.NS","Wipro")]:
                    try:
                        h = yf.Ticker(sym).history(period="2d")
                        if len(h) >= 2:
                            c  = h["Close"].iloc[-1]
                            p  = h["Close"].iloc[-2]
                            ch = ((c - p) / p) * 100
                            results.append(DataPoint(
                                source="NSE / Yahoo Finance", category="market",
                                label=f"{name} Stock", value=round(c, 1), unit="₹",
                                sentiment="positive" if ch > 0 else "negative",
                                severity="low", is_live=True, error=f"{ch:+.2f}% today"
                            ))
                    except Exception:
                        pass
        except ImportError:
            results = [DataPoint(
                source="NSE (fallback)", category="market",
                label="Nifty IT Index", value=37842, unit="points",
                sentiment="neutral", is_live=False,
                error="Install yfinance for live data: pip install yfinance"
            )]
        except Exception as e:
            results = [DataPoint(
                source="NSE (fallback)", category="market",
                label="Nifty IT Index", value=37842, unit="points",
                sentiment="neutral", is_live=False, error=str(e)
            )]

        _write_cache("nifty_it", [asdict(d) for d in results])
        return results

    @classmethod
    def fetch_github_trends(cls) -> List[DataPoint]:
        cached = _read_cache("github_trends")
        if cached:
            return [DataPoint(**d) for d in cached]

        results = []
        try:
            import requests
            from bs4 import BeautifulSoup
            r = requests.get("https://github.com/trending",
                             headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            r.raise_for_status()
            soup  = BeautifulSoup(r.text, "html.parser")
            langs = []
            for repo in soup.select("article.Box-row")[:10]:
                lang_el = repo.select_one("[itemprop='programmingLanguage']")
                if lang_el:
                    lang = lang_el.text.strip()
                    if lang and lang not in langs:
                        langs.append(lang)
            if langs:
                results.append(DataPoint(
                    source="GitHub Trending", category="tech",
                    label="Trending Languages Today", value=langs[:6],
                    sentiment="positive", severity="low",
                    source_url="https://github.com/trending", is_live=True,
                ))
        except Exception as e:
            results = [DataPoint(
                source="GitHub Trending", category="tech",
                label="Trending Languages (cached)",
                value=["Python", "TypeScript", "Rust", "Go", "Java"],
                sentiment="neutral", is_live=False, error=str(e)
            )]

        _write_cache("github_trends", [asdict(d) for d in results])
        return results

    @classmethod
    def fetch_all(cls) -> Dict[str, List[DataPoint]]:
        logger.info("🌐 Fetching all external real-time data...")
        results = {"news": [], "macro": [], "market": [], "tech": []}
        for category, fetcher in [
            ("news",   cls.fetch_news),
            ("macro",  cls.fetch_world_bank),
            ("macro",  cls.fetch_rbi_rate),
            ("market", cls.fetch_exchange_rate),
            ("market", cls.fetch_nifty_it),
            ("tech",   cls.fetch_github_trends),
        ]:
            try:
                items = fetcher()
                results[category].extend(items)
            except Exception as e:
                logger.error(f"{fetcher.__name__} failed: {e}")
        total = sum(len(v) for v in results.values())
        logger.info(f"🌐 External fetch complete: {total} data points")
        return results


# ============================================================
# INTERNAL DATA PROCESSOR
# ============================================================

class InternalDataProcessor:
    """
    Processes company-uploaded internal data.
    Uses AI (Claude via Groq) to convert ANY input format.
    """

    # ── AI Smart Converter ────────────────────────────────────

    @staticmethod
    def ai_convert(raw_text: str, groq_api_key: str) -> List["InternalProjectData"]:
        """
        Sends ANY raw text to the LLM and asks it to extract
        structured project KPI data. The user can paste:
          - A Jira export paragraph
          - A WhatsApp message from the PM
          - A status update email
          - A table copied from Excel
          - A meeting notes dump
          - Anything
        The LLM figures out the mapping automatically.
        """
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = """You are a data extraction expert for IT project management.
Your job is to extract structured project KPI data from ANY kind of input text.

The user will paste raw text — it could be:
- A status update email
- Meeting notes  
- A table copied from Excel/Jira/spreadsheet
- A WhatsApp message from a project manager
- A dump of numbers in any format

Extract ALL projects you can find and return ONLY a valid JSON array.
Each object must have these fields (use null if not found):
{
  "project_code": "string — project ID, code, or name if no ID",
  "project_name": "string or null",
  "client_name": "string or null",
  "sprint_velocity": number or null,
  "open_bugs": integer or null,
  "open_tickets": integer or null,
  "actual_hours_this_week": number or null,
  "team_available_hours": number or null,
  "invoices_raised_this_month": number or null,
  "invoices_paid_this_month": number or null,
  "team_size": integer or null,
  "schedule_delay_days": integer or null,
  "budget_utilization_pct": number or null,
  "open_risks": integer or null,
  "customer_satisfaction": number or null,
  "notes": "any extra info as a short string"
}

Rules:
- Return ONLY the JSON array, no explanation, no markdown, no backticks
- If the input mentions budget used %, map to budget_utilization_pct
- If the input mentions NPS or CSAT, map to customer_satisfaction
- If the input mentions "X days behind", map to schedule_delay_days
- If the input mentions "X open issues/tickets/bugs", map appropriately
- If there is only one project in the text, return an array with one object
- Infer project_code from project name if no explicit code given
- For monetary values, keep them as raw numbers (no currency symbols)"""

        try:
            llm = ChatGroq(
                api_key=groq_api_key,
                model_name="llama-3.3-70b-versatile",
                temperature=0,
                max_tokens=2000,
            )
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Extract project data from this text:\n\n{raw_text}")
            ])
            raw_json = response.content.strip()
            # Strip markdown if LLM adds it despite instructions
            raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                parsed = [parsed]

            results = []
            for item in parsed:
                code = str(item.get("project_code") or item.get("project_name") or "UNKNOWN")
                results.append(InternalProjectData(
                    project_code=code.strip(),
                    source_system="AI Converted",
                    project_name=item.get("project_name"),
                    client_name=item.get("client_name"),
                    sprint_velocity=_safe_float(item.get("sprint_velocity")),
                    open_bugs=_safe_int(item.get("open_bugs")),
                    open_tickets=_safe_int(item.get("open_tickets")),
                    actual_hours_this_week=_safe_float(item.get("actual_hours_this_week")),
                    team_available_hours=_safe_float(item.get("team_available_hours")),
                    invoices_raised_this_month=_safe_float(item.get("invoices_raised_this_month")),
                    invoices_paid_this_month=_safe_float(item.get("invoices_paid_this_month")),
                    team_size=_safe_int(item.get("team_size")),
                    schedule_delay_days=_safe_int(item.get("schedule_delay_days")),
                    budget_utilization_pct=_safe_float(item.get("budget_utilization_pct")),
                    open_risks=_safe_int(item.get("open_risks")),
                    customer_satisfaction=_safe_float(item.get("customer_satisfaction")),
                    notes=item.get("notes", ""),
                    raw_input=raw_text[:500],
                ))
            logger.info(f"🤖 AI converted {len(results)} projects from raw text")
            return results

        except Exception as e:
            logger.error(f"AI conversion failed: {e}")
            raise

    # ── CSV/Excel Upload ──────────────────────────────────────

    @staticmethod
    def parse_csv_upload(file_bytes: bytes, filename: str) -> List["InternalProjectData"]:
        """
        Parses CSV/Excel. Column names are flexible —
        we try common variations so companies don't need exact names.
        """
        results = []
        try:
            import pandas as pd
            import io

            if filename.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(io.BytesIO(file_bytes))
            else:
                df = pd.read_csv(io.BytesIO(file_bytes))

            # Normalize column names
            df.columns = [c.strip().lower()
                           .replace(" ", "_")
                           .replace("-", "_")
                           .replace("/", "_")
                          for c in df.columns]

            # Flexible column mapping — accept common variations
            col_map = {
                "project_code":               ["project_code","code","proj_code","id","project_id","proj_id"],
                "project_name":               ["project_name","name","project","proj_name"],
                "client_name":                ["client_name","client","customer","account"],
                "sprint_velocity":            ["sprint_velocity","velocity","story_points","sp_completed","points_completed"],
                "open_bugs":                  ["open_bugs","bugs","bug_count","defects","open_defects"],
                "open_tickets":               ["open_tickets","tickets","issues","open_issues","jira_tickets"],
                "actual_hours_this_week":     ["actual_hours_this_week","actual_hours","hours_worked","logged_hours"],
                "team_available_hours":       ["team_available_hours","available_hours","capacity","planned_hours"],
                "invoices_raised_this_month": ["invoices_raised_this_month","invoices_raised","billed","revenue_billed","amount_billed"],
                "invoices_paid_this_month":   ["invoices_paid_this_month","invoices_paid","payments_received","amount_received","paid"],
                "team_size":                  ["team_size","team","headcount","members"],
                "schedule_delay_days":        ["schedule_delay_days","delay_days","days_delayed","days_behind","behind_schedule"],
                "budget_utilization_pct":     ["budget_utilization_pct","budget_utilization","budget_used_pct","burn_rate_pct"],
                "open_risks":                 ["open_risks","risks","risk_count","open_risk_items"],
                "customer_satisfaction":      ["customer_satisfaction","nps","csat","satisfaction","nps_score","csat_score"],
                "notes":                      ["notes","comments","remarks","status","status_notes"],
            }

            def _get_col(field_name):
                for alias in col_map.get(field_name, [field_name]):
                    if alias in df.columns:
                        return alias
                return None

            for _, row in df.iterrows():
                code_col = _get_col("project_code")
                code     = str(row[code_col]).strip() if code_col else "UNKNOWN"
                if code in ("nan", "None", ""):
                    continue

                def _val(field):
                    col = _get_col(field)
                    if col is None:
                        return None
                    v = row.get(col)
                    return None if str(v) in ("nan", "None", "") else v

                # Extra columns → custom_kpis
                known_cols = set()
                for aliases in col_map.values():
                    known_cols.update(aliases)
                custom = {
                    k: (float(v) if str(v).replace('.','').replace('-','').isdigit() else str(v))
                    for k, v in row.items()
                    if k not in known_cols and str(v) not in ("nan","None","")
                }

                results.append(InternalProjectData(
                    project_code=code,
                    source_system=f"CSV: {filename}",
                    project_name=str(_val("project_name") or ""),
                    client_name=str(_val("client_name") or ""),
                    sprint_velocity=_safe_float(_val("sprint_velocity")),
                    open_bugs=_safe_int(_val("open_bugs")),
                    open_tickets=_safe_int(_val("open_tickets")),
                    actual_hours_this_week=_safe_float(_val("actual_hours_this_week")),
                    team_available_hours=_safe_float(_val("team_available_hours")),
                    invoices_raised_this_month=_safe_float(_val("invoices_raised_this_month")),
                    invoices_paid_this_month=_safe_float(_val("invoices_paid_this_month")),
                    team_size=_safe_int(_val("team_size")),
                    schedule_delay_days=_safe_int(_val("schedule_delay_days")),
                    budget_utilization_pct=_safe_float(_val("budget_utilization_pct")),
                    open_risks=_safe_int(_val("open_risks")),
                    customer_satisfaction=_safe_float(_val("customer_satisfaction")),
                    notes=str(_val("notes") or ""),
                    custom_kpis=custom,
                ))

            logger.info(f"📊 Parsed {len(results)} projects from {filename}")
        except Exception as e:
            logger.error(f"CSV parse failed: {e}")
        return results

    @staticmethod
    def parse_json_input(json_str: str) -> List["InternalProjectData"]:
        results = []
        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                code = str(item.get("project_code") or item.get("code") or "UNKNOWN")
                results.append(InternalProjectData(
                    project_code=code,
                    source_system="Manual JSON",
                    project_name=item.get("project_name"),
                    client_name=item.get("client_name"),
                    sprint_velocity=_safe_float(item.get("sprint_velocity")),
                    open_bugs=_safe_int(item.get("open_bugs")),
                    open_tickets=_safe_int(item.get("open_tickets")),
                    actual_hours_this_week=_safe_float(item.get("actual_hours_this_week")),
                    team_available_hours=_safe_float(item.get("team_available_hours")),
                    invoices_raised_this_month=_safe_float(item.get("invoices_raised_this_month")),
                    invoices_paid_this_month=_safe_float(item.get("invoices_paid_this_month")),
                    team_size=_safe_int(item.get("team_size")),
                    schedule_delay_days=_safe_int(item.get("schedule_delay_days")),
                    budget_utilization_pct=_safe_float(item.get("budget_utilization_pct")),
                    open_risks=_safe_int(item.get("open_risks")),
                    customer_satisfaction=_safe_float(item.get("customer_satisfaction")),
                    custom_kpis=item.get("custom_kpis", {}),
                    notes=item.get("notes", ""),
                ))
        except Exception as e:
            logger.error(f"JSON parse failed: {e}")
        return results

    @staticmethod
    def manual_to_internal(project_code: str, kpis: dict) -> "InternalProjectData":
        return InternalProjectData(
            project_code=project_code.strip(),
            source_system="Manual Form",
            project_name=kpis.get("project_name"),
            client_name=kpis.get("client_name"),
            sprint_velocity=_safe_float(kpis.get("sprint_velocity")),
            open_bugs=_safe_int(kpis.get("open_bugs")),
            open_tickets=_safe_int(kpis.get("open_tickets")),
            actual_hours_this_week=_safe_float(kpis.get("actual_hours_this_week")),
            team_available_hours=_safe_float(kpis.get("team_available_hours")),
            invoices_raised_this_month=_safe_float(kpis.get("invoices_raised_this_month")),
            invoices_paid_this_month=_safe_float(kpis.get("invoices_paid_this_month")),
            team_size=_safe_int(kpis.get("team_size")),
            schedule_delay_days=_safe_int(kpis.get("schedule_delay_days")),
            budget_utilization_pct=_safe_float(kpis.get("budget_utilization_pct")),
            open_risks=_safe_int(kpis.get("open_risks")),
            customer_satisfaction=_safe_float(kpis.get("customer_satisfaction")),
            notes=kpis.get("notes", ""),
        )

    # ── Persistence ───────────────────────────────────────────

    @staticmethod
    def save_internal_data(data: List["InternalProjectData"]):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        INTERNAL_DATA_PATH.write_text(
            json.dumps([asdict(d) for d in data], indent=2)
        )
        logger.info(f"💾 Saved {len(data)} internal data records to {INTERNAL_DATA_PATH}")

    @staticmethod
    def load_internal_data() -> List["InternalProjectData"]:
        if not INTERNAL_DATA_PATH.exists():
            return []
        try:
            raw = json.loads(INTERNAL_DATA_PATH.read_text())
            return [InternalProjectData(**r) for r in raw]
        except Exception as e:
            logger.error(f"Failed to load internal data: {e}")
            return []

    @staticmethod
    def clear_internal_data():
        """Deletes internal data file. Single authoritative method."""
        if INTERNAL_DATA_PATH.exists():
            INTERNAL_DATA_PATH.unlink()
            logger.info("🗑 Internal data cleared")

    @staticmethod
    def get_template_csv() -> str:
        return (
            "project_code,project_name,client_name,"
            "sprint_velocity,open_bugs,open_tickets,"
            "actual_hours_this_week,team_available_hours,"
            "invoices_raised_this_month,invoices_paid_this_month,"
            "team_size,schedule_delay_days,budget_utilization_pct,"
            "open_risks,customer_satisfaction,notes\n"
            "PRJ-001,Project Atlas,Tata Steel,"
            "42,12,28,320,400,2500000,2000000,8,5,68,3,72,On track\n"
            "PRJ-003,Project Nova,Bajaj Finserv,"
            "18,31,67,400,400,3500000,0,12,18,89,8,34,Client payment overdue\n"
            "MY-PROJECT,Mobile App v2,HDFC Bank,"
            "35,8,22,280,320,1800000,1800000,6,0,55,2,81,Healthy\n"
        )


# ============================================================
# RISK ANALYSIS INTEGRATION
# ============================================================

def get_enriched_project_data(project_code: str) -> Optional[Dict[str, Any]]:
    """
    Called by risk_scoring_agent during analysis.
    Returns internal KPI data for a project if uploaded, else None.
    The agent uses this to override/supplement synthetic data.
    """
    records = InternalDataProcessor.load_internal_data()
    # Match by exact code OR by name (case-insensitive)
    for rec in records:
        if (rec.project_code.upper() == project_code.upper() or
            (rec.project_name and rec.project_name.upper() == project_code.upper())):
            return asdict(rec)
    return None


def get_external_market_context() -> Dict[str, Any]:
    """
    Called by market_analysis_agent during analysis.
    Returns cached external data to enrich market risk scoring.
    Returns empty dict if no fetch has been done.
    """
    context = {}

    # Exchange rate
    cached_fx = _read_cache("exchange_rate")
    if cached_fx:
        for dp in cached_fx:
            if "USD/INR" in dp.get("label", ""):
                context["usd_inr"] = dp.get("value")
                context["usd_inr_sentiment"] = dp.get("sentiment")
                break

    # World Bank macro
    cached_wb = _read_cache("world_bank")
    if cached_wb:
        for dp in cached_wb:
            if "GDP" in dp.get("label", ""):
                context["gdp_growth"] = dp.get("value")
            if "Inflation" in dp.get("label", ""):
                context["inflation"] = dp.get("value")

    # News sentiment
    cached_news = _read_cache("rss_news")
    if cached_news:
        neg = sum(1 for d in cached_news if d.get("sentiment") == "negative")
        total = len(cached_news)
        context["news_negative_pct"] = round((neg / total * 100) if total else 0, 1)
        context["news_count"] = total

    return context


def load_uploaded_projects():
    """
    Convert uploaded internal_data.json into project dicts
    compatible with the risk system.
    """

    records = InternalDataProcessor.load_internal_data()

    if not records:
        return []

    projects = []

    for row in records:

        projects.append({
            "id": row.project_code,
            "name": row.project_name or row.project_code,
            "client": row.client_name or "Unknown Client",
            "type": "Digital Transformation Program",
            "description": row.notes or "Uploaded internal project",
            "start_date": "2026-01-01",
            "planned_end_date": "2026-12-31",
            "actual_completion_pct": 50,
            "days_behind_schedule": row.schedule_delay_days or 0,
            "team_size": row.team_size or 5,
            "resignations_last_30_days": 0,
            "budget_inr": 50000000,
            "amount_spent_inr": 20000000,
            "projected_overrun_inr": 0,
            "payment_overdue_days": 0,
            "pending_invoices_inr": 0,
            "client_satisfaction_score": (
                (row.customer_satisfaction or 50) / 10
            ),
            "days_since_last_client_contact": 5
        })

    logger.info(f"📂 Loaded {len(projects)} uploaded projects")

    return projects





def build_market_signals_from_external(external_data: dict):
    """
    Converts DataPoint objects from ExternalDataFetcher
    into MarketSignal objects for the MarketAnalysisAgent.
    """

    signals = []

    for category in external_data.values():

        for dp in category:

            try:
                signals.append(
                    MarketSignal(
                        signal_type=dp.category,
                        source=dp.source,
                        headline=dp.label,
                        summary=str(dp.value),
                        sentiment=dp.sentiment,
                        relevance_score=0.7,
                        impact_on_it="Derived from real-time external data source",
                        severity=dp.severity,
                        date=dp.timestamp[:10]
                    )
                )

            except Exception as e:
                logger.warning(f"Signal conversion failed: {e}")

    logger.info(f"🌍 Built {len(signals)} REAL market signals")

    return signals



# ============================================================
# HELPERS
# ============================================================

def _safe_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _safe_int(v) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


# ============================================================
# INTEGRATION STUBS (shown in UI)
# ============================================================

INTEGRATION_STUBS = {
    "Jira": {
        "status": "stub",
        "description": "Sync sprint velocity, open tickets, and bug counts automatically.",
        "fields": ["sprint_velocity", "open_bugs", "open_tickets", "epic_progress"],
        "setup": "Add JIRA_BASE_URL and JIRA_API_TOKEN to your .env file",
        "docs": "https://developer.atlassian.com/cloud/jira/platform/rest/v3/",
    },
    "GitHub": {
        "status": "stub",
        "description": "Track open PRs, commit velocity, and deployment frequency.",
        "fields": ["open_prs", "commit_velocity", "deployment_frequency"],
        "setup": "Add GITHUB_TOKEN to your .env file",
        "docs": "https://docs.github.com/en/rest",
    },
    "Freshdesk": {
        "status": "stub",
        "description": "Track client ticket volume, SLA breaches, and response times.",
        "fields": ["open_tickets", "sla_breaches", "avg_resolution_time"],
        "setup": "Add FRESHDESK_API_KEY and FRESHDESK_DOMAIN to your .env file",
        "docs": "https://developers.freshdesk.com/api/",
    },
    "Zoho Books / QuickBooks": {
        "status": "stub",
        "description": "Sync invoice status and payment tracking automatically.",
        "fields": ["invoices_raised", "invoices_paid", "overdue_amount"],
        "setup": "Add ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET to your .env file",
        "docs": "https://www.zoho.com/books/api/v3/",
    },
    "Google Sheets": {
        "status": "stub",
        "description": "Publish a Google Sheet and we read KPI data from it automatically.",
        "fields": ["any columns matching our schema"],
        "setup": "Publish your sheet and paste the CSV export URL",
        "docs": "https://developers.google.com/sheets/api",
    },
    "SAP / Oracle ERP": {
        "status": "stub",
        "description": "Enterprise ERP integration via REST API or database export.",
        "fields": ["financials", "resource_hours", "procurement"],
        "setup": "Contact your admin for API credentials",
        "docs": "https://api.sap.com/",
    },
}


# ── Sample text for AI converter demo ─────────────────────────
SAMPLE_AI_INPUT = """Project Status Update — Week 47

Project Nova (PRJ-003) — Bajaj Finserv AI Platform
Team size: 12 | Sprint 14 velocity: 18 story points (was 32 last sprint)
Open bugs: 31 critical, 14 minor | Open Jira tickets: 67
Hours logged this week: 400/400 (team fully utilized but velocity low)
Invoice of ₹35 lakhs raised but NOT paid — overdue 45 days
Budget burn: 89% used, only 60% work delivered
NPS from client: 34 (very low, client escalating)
Currently 18 days behind schedule on ML model delivery
Open risks: 8 items including key resource dependency on lead data scientist

Project Helix (PRJ-002) — HDFC Mobile Banking
Team: 8 members | Sprint velocity: 38 points (healthy)
Bugs: 5 open | Tickets: 15
Actual hours: 280, available: 320
Invoices raised: ₹18L, paid: ₹18L (all clear)
0 days delay | Budget at 55% | NPS: 82 | Open risks: 2"""

SAMPLE_JSON_TEMPLATE = """{
  "project_code": "PRJ-001",
  "project_name": "Project Atlas",
  "client_name": "Tata Steel",
  "sprint_velocity": 42,
  "open_bugs": 12,
  "open_tickets": 28,
  "actual_hours_this_week": 320,
  "team_available_hours": 400,
  "invoices_raised_this_month": 2500000,
  "invoices_paid_this_month": 2000000,
  "team_size": 8,
  "schedule_delay_days": 5,
  "budget_utilization_pct": 68,
  "open_risks": 3,
  "customer_satisfaction": 72,
  "notes": "Sprint 14 complete. Minor delays on API integration."
}"""
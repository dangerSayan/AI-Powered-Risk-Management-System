<div align="center">

# RiskPulse AI

### AI-Powered IT Project Risk Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/LLM-Groq%20llama--3.3--70b-f55036?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange?style=for-the-badge)](https://www.trychroma.com)
[![Pydantic](https://img.shields.io/badge/Schemas-Pydantic%20v2-e92063?style=for-the-badge)](https://docs.pydantic.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**A production-grade, multi-agent AI system that monitors multiple IT projects, scores risk across 7 dimensions, generates intelligent alerts, and answers natural language questions about your portfolio — all in real time.**

[Features](#-features) · [Architecture](#-architecture) · [Tech Stack](#-tech-stack) · [Quick Start](#-quick-start) · [Usage Guide](#-usage-guide) · [File Structure](#-file-structure) · [Configuration](#-configuration) · [API Reference](#-api-reference)

---

![Dashboard Preview](https://img.shields.io/badge/UI-Dark%20Command%20Center-0d1117?style=flat-square) ![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square) ![Agents](https://img.shields.io/badge/Agents-3%20AI%20Agents%20%2B%20Orchestrator-blue?style=flat-square) ![Projects](https://img.shields.io/badge/Projects-15%20Monitored-purple?style=flat-square)

</div>

---

## 📋 Table of Contents

1. [What is RiskPulse AI?](#-what-is-riskpulse-ai)
2. [The Problem It Solves](#-the-problem-it-solves)
3. [Features](#-features)
4. [Architecture](#-architecture)
5. [Tech Stack](#-tech-stack)
6. [Quick Start](#-quick-start)
7. [Full Installation Guide](#-full-installation-guide)
8. [Usage Guide](#-usage-guide)
9. [File Structure](#-file-structure)
10. [Configuration](#-configuration)
11. [Risk Scoring Formula](#-risk-scoring-formula)
12. [Data Pipeline](#-data-pipeline)
13. [Real Data Upload](#-real-data-upload)
14. [API Reference (Key Classes)](#-api-reference-key-classes)
15. [AI Chat & RAG System](#-ai-chat--rag-system)
16. [Live Data Sources](#-live-data-sources)
17. [Troubleshooting](#-troubleshooting)
18. [Known Limitations](#-known-limitations)
19. [Roadmap](#-roadmap)
20. [Contributing](#-contributing)
21. [License](#-license)

---

## 🤖 What is RiskPulse AI?

RiskPulse AI is a **multi-agent AI system** that automates IT project portfolio risk management. It continuously monitors 15 live IT projects, scores them across 7 risk dimensions using a weighted formula, generates prioritized alerts and mitigation strategies, and stores everything in a vector database so a conversational AI chatbot can answer questions like:

> _"Which projects need my attention today?"_
> _"What's driving the high risk score on Project Atlas?"_
> _"How does market volatility affect our banking sector projects?"_

This is the kind of system that large IT companies like TCS, Infosys, and Wipro operate manually with dedicated PMO (Project Management Office) analyst teams. RiskPulse AI **automates the entire workflow** using Generative AI, RAG, and a multi-agent architecture.

### In Plain English

Imagine managing 15 software projects simultaneously — each with teams, budgets, deadlines, and clients. Things go wrong: engineers resign, payments are delayed, market conditions shift. Normally, a manager manually checks each project every day, reads reports, and makes judgment calls.

RiskPulse AI does this automatically in under 2 seconds:

1. Reads all project KPIs (delays, budgets, team health, client satisfaction)
2. Reads live market signals (economic data, IT sector trends, external feeds)
3. Runs AI agents that score each project's risk from 0 to 100
4. Generates specific, evidence-backed alerts ("client payment 75 days overdue")
5. Recommends prioritized action steps with timelines and owners
6. Stores everything in ChromaDB so the AI chatbot can answer any question

**Total time to get a complete portfolio risk picture: under 2 seconds.**

---

## 🎯 The Problem It Solves

Traditional IT project risk management has five critical failures:

| Problem                     | Description                                              | How RiskPulse AI Solves It                                              |
| --------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Reactive, not proactive** | Managers know about a problem after it becomes a crisis  | Continuous scoring flags issues at 5 days, not 50 days                  |
| **Manual and slow**         | Risk reports take hours in Excel/PowerPoint              | Full analysis in < 2 seconds, always up to date                         |
| **Siloed information**      | Finance, HR, and delivery teams don't share data         | All dimensions scored together in one unified model                     |
| **Market signals ignored**  | No cross-domain intelligence                             | Real-time economic data (RBI rates, GDP, sector news) feeds into scores |
| **Knowledge not queryable** | Answering "what should I do today?" requires manual work | Ask the AI chatbot in natural language, get an answer instantly         |

---

## ✨ Features

### Core Analysis Engine

- **Multi-Agent Risk Analysis** — orchestrated by a central ProjectRiskManager
- **Dynamic Project Portfolio** — synthetic mode monitors 15 generated projects, real mode analyzes any uploaded projects
- **7-Dimension Risk Framework** — Schedule, Financial, Resource, Technical, Market, Operational, Compliance
- **Weighted Risk Formula** — configurable weights per dimension (see Risk Scoring Formula)
- **4 Risk Levels** — LOW (0–29), MEDIUM (30–54), HIGH (55–74), CRITICAL (75–100)
- **Automatic Alert Generation** — schedule delays, budget overruns, resource gaps, SLA breaches
- **Portfolio Risk Score** — weighted aggregation highlighting critical projects

### Dual Analysis Modes

RiskPulse AI supports two analysis pipelines.

**🔵 Synthetic Mode**

- Uses 15 generated IT projects
- Uses generated market signals
- Always available for demos and testing

**⚡ Real Data Mode**

- Uses uploaded real project records
- Uses **live external market data only**
- Market signals are dynamically constructed from:
  - economic indicators
  - financial markets
  - news sentiment
  - currency movements

Synthetic signals are **not used in real mode**.

### Real Data Upload (4 Methods)

- **✨ AI Smart Converter** — paste any text (emails, status reports, free-form notes) and Groq LLM extracts structured KPIs automatically
- **CSV/Excel Upload** — flexible column mapping, tolerates messy headers
- **JSON Paste** — paste raw JSON for developer use
- **Manual Form** — free-text input per project field

### Live External Data (No API Key Required)

- **USD/INR Exchange Rate** — Frankfurter/ECB API
- **India GDP & Inflation** — World Bank Open Data API
- **RBI Repo Rate** — Reserve Bank of India DBIE
- **Nifty IT, TCS, Infosys, Wipro Stock Prices** — Yahoo Finance (yfinance)
- **IT Sector News** — RSS feeds from Economic Times, Moneycontrol, NDTV Business
- **GitHub Trending Languages** — GitHub trending page scraper
- All feeds cached for 1 hour in `risk_management/data/realtime_cache/`

## 🌐 Real Market Intelligence Pipeline

When running **Real Data Analysis**, the system builds market intelligence entirely from live external data.

Pipeline:

External APIs  
↓  
ExternalDataFetcher  
↓  
build_market_signals_from_external()  
↓  
MarketAnalysisAgent  
↓  
Market Risk Score

### Data Sources Used

- World Bank economic indicators (GDP growth, inflation)
- Currency exchange rates (USD/INR)
- Financial markets (Nifty IT index)
- Technology sector news feeds
- GitHub technology trends

Each signal is converted into a structured `MarketSignal` object containing:

- signal type
- sentiment
- relevance score
- sector impact
- description

This allows the **MarketAnalysisAgent** to score real-world risk conditions affecting IT projects.

This architecture ensures that **real analysis uses only real external signals** rather than synthetic market data.

### AI Chat (RAG-Powered)

- **Retrieval-Augmented Generation** — answers are grounded in actual project data, not hallucinated
- **ChromaDB Vector Store** — risk reports stored as semantic embeddings
- **Context-aware responses** — chatbot knows the current state of all 15 projects
- **Topic filtering** — only answers risk management questions, politely declines off-topic queries
- **Suggested questions** — pre-built question buttons for common queries

### Professional Dashboard

- **Dark Command Center UI** — Space Grotesk + JetBrains Mono typography
- **Interactive Plotly charts** — bar charts, radar charts, donut charts
- **KPI cards** — portfolio score, high-risk count, market risk, active alerts
- **Per-project deep dive** — radar chart across 7 dimensions, evidence cards, action plan
- **Real vs Synthetic comparison** — per-project score change table with badges

### Debug & Observability

- **🔍 Debug Panel** — shows exact matching status between uploaded data and project codes
- **Terminal logging** — every agent logs what it matched, what it overrode, and why (Loguru)
- **Per-project data source labels** — `REAL DATA` vs `SYNTHETIC` badge on every project in comparison view
- **Manual code tester** — test any project code against uploaded records instantly

---

## 🏗️ Architecture

RiskPulse AI is built in three layers with a clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LAYER 1: FRONTEND                           │
│                      Streamlit Web Application                      │
│                                                                     │
│  🏠 Dashboard  📋 Projects  🌐 Live Data  💬 AI Chat  📄 Reports  ⚙️ Analysis  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  user triggers analysis
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         LAYER 2: AGENTS                             │
│                                                                     │
│   ProjectRiskManager (Orchestrator)                                 │
│        │                                                            │
│        ├── MarketAnalysisAgent   reads 20 signals → market_context  │
│        ├── ProjectStatusAgent    reads 15 projects → health scores  │
│        └── RiskScoringAgent ×15  scores each project → RiskReport   │
│                                                                     │
│   Each agent is a pure Python class. No LLM frameworks in agents.  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  stores results
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LAYER 3: RAG PIPELINE                          │
│                                                                     │
│   sentence-transformers/all-MiniLM-L6-v2  →  text embeddings        │
│   ChromaDB (local persistent store)       →  vector storage         │
│   Groq / llama-3.3-70b-versatile          →  chat answer generation │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Design Pattern

RiskPulse AI follows an **Orchestrator Multi-Agent Architecture**.

Instead of agents calling each other directly, a central orchestrator coordinates the workflow.

This design ensures:

- deterministic execution
- easy debugging
- clear responsibility boundaries
- fast performance

Agents never communicate directly.

The workflow is controlled by **ProjectRiskManager**.

### Agent Responsibilities

| Agent                   | File                       | Role                                                             |
| ----------------------- | -------------------------- | ---------------------------------------------------------------- |
| **ProjectRiskManager**  | `risk_manager.py`          | Orchestrator controlling the full analysis pipeline              |
| **MarketAnalysisAgent** | `market_analysis_agent.py` | Analyzes external economic signals and computes market risk      |
| **ProjectStatusAgent**  | `project_status_agent.py`  | Evaluates internal project health indicators                     |
| **RiskScoringAgent**    | `risk_scoring_agent.py`    | Combines market + internal signals to produce final risk reports |

### Reporting Layer

Instead of a separate Reporting Agent, RiskPulse AI provides reporting through two components:

**Streamlit Dashboard**

- interactive charts
- project risk cards
- alerts and mitigation strategies
- portfolio risk overview

**RAG Chatbot**

- natural language interface to the risk reports
- powered by ChromaDB vector retrieval
- grounded answers using project data

> **Why pure Python agents instead of LangChain agents?**
> Determinism. LangChain agents use LLM reasoning to decide what tools to call next, which is non-deterministic and slow. The risk scoring formula must be consistent and explainable. Pure Python agents are fast (< 2 seconds for 15 projects), testable, and auditable.

### Data Flow (Step-by-Step)

```
                        ┌─────────────────┐
                        │  projects.json   │  15 synthetic IT projects
                        │ market_signals   │  20 market indicators
                        │ internal_data    │  your real uploaded KPIs
                        └────────┬────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   MarketAnalysisAgent    │
                    │  Reads all 20 signals    │
                    │  Outputs: volatility,    │
                    │  competitor threat,      │
                    │  regulatory risk, etc.   │
                    └────────────┬────────────┘
                                 │  market_context dict
                                 │
             ┌───────────────────▼───────────────────┐
             │         ProjectStatusAgent             │
             │  Reads each of 15 projects             │
             │  Computes: schedule%, financial%,      │
             │  resource%, technical%, operational%   │
             └───────────────────┬───────────────────┘
                                 │  health scores per project
                                 │
        ┌────────────────────────▼────────────────────────┐
        │           RiskScoringAgent (×15 projects)        │
        │                                                   │
        │  1. Try to match project code → internal_data    │
        │  2. If match: inject real KPIs over synthetic     │
        │  3. Score 7 dimensions with weighted formula      │
        │  4. Generate alerts + mitigation strategies       │
        │  5. Tag report: used_real_data = True/False       │
        └────────────────────────┬────────────────────────┘
                                 │  15 × RiskReport
                                 │
              ┌──────────────────▼──────────────────┐
              │     Portfolio Aggregation            │
              │  Weighted average → portfolio score  │
              │  Count HIGH + CRITICAL projects      │
              │  Build PortfolioAnalysisResult       │
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │          RAG Pipeline                │
              │  Serialize reports → text chunks     │
              │  Embed with all-MiniLM-L6-v2         │
              │  Store in ChromaDB                   │
              │  Available for AI Chat queries       │
              └─────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component           | Technology                             | Version | Why Chosen                                                                 |
| ------------------- | -------------------------------------- | ------- | -------------------------------------------------------------------------- |
| **Language**        | Python                                 | 3.10+   | Ecosystem for AI/ML, async support, type hints                             |
| **Web UI**          | Streamlit                              | 1.32+   | Pure Python dashboards, no frontend code needed                            |
| **Charts**          | Plotly                                 | 5.x     | Interactive, export-ready charts natively in Streamlit                     |
| **Data Models**     | Pydantic                               | v2      | Type-safe schemas, automatic validation, zero silent bugs                  |
| **AI Agents**       | Pure Python classes                    | —       | Deterministic, fast, testable — no LLM needed for scoring                  |
| **LLM (Chat)**      | Groq · llama-3.3-70b-versatile         | —       | Free tier, extremely fast inference (< 1s response), OpenAI-compatible API |
| **LLM Framework**   | LangChain + langchain-groq             | 0.3+    | Connects Groq to the RAG pipeline                                          |
| **Embeddings**      | sentence-transformers/all-MiniLM-L6-v2 | —       | Runs locally on CPU, no API key needed, 384-dim vectors                    |
| **Vector Database** | ChromaDB                               | 0.4+    | Local persistent store, no server needed, semantic search                  |
| **Logging**         | Loguru                                 | 0.7+    | Structured, colored, timestamped logs with zero config                     |
| **Config**          | python-dotenv                          | —       | API keys in `.env`, never hardcoded                                        |
| **External Data**   | yfinance + feedparser + requests       | —       | Stock prices, RSS news, economic APIs                                      |
| **Fonts**           | Space Grotesk + JetBrains Mono         | —       | Google Fonts CDN, professional dark-theme aesthetic                        |

### LLM Provider Abstraction

The system is built with **one-line provider switching** via `.env`:

```env
# Current: Groq (fast, free, cloud)
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here

# Future: Switch to AWS Bedrock (enterprise, no usage limits)
LLM_PROVIDER=bedrock
AWS_REGION=ap-south-1
```

Nothing else in the codebase changes. This is configured in `config/llm_config.py`.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/dangerSayan/AI-Powered-Risk-Management-System.git
cd AI-Powered-Risk-Management-System/risk_management

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file (copy the template)
copy .env.example .env          # Windows
# cp .env.example .env          # Mac/Linux

# 5. Add your Groq API key to .env
# Get free key at: https://console.groq.com
# Edit .env and set: GROQ_API_KEY=your_key_here

# 6. Generate synthetic project data (first time only)
python -m backend.data.data_generator

# 7. Run the application
streamlit run app.py

# 8. Open in browser
# → http://localhost:8501
```

---

## 📦 Full Installation Guide

### Prerequisites

| Requirement  | Minimum                              | Recommended              |
| ------------ | ------------------------------------ | ------------------------ |
| Python       | 3.10                                 | 3.11+                    |
| RAM          | 4 GB                                 | 8 GB                     |
| Disk         | 2 GB free                            | 5 GB free                |
| OS           | Windows 10 / Ubuntu 20.04 / macOS 12 | Any modern OS            |
| Groq API Key | Required for AI Chat                 | Free at console.groq.com |

### Step 1 — Clone the Repository

```bash
git clone https://github.com/dangerSayan/AI-Powered-Risk-Management-System.git
cd AI-Powered-Risk-Management-System/risk_management
```

### Step 2 — Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3 — Install Python Dependencies

```bash
cd risk_management
pip install -r requirements.txt
```

This installs approximately 50 packages. The largest are:

- `torch` (for sentence-transformers embeddings, ~2GB download on first run)
- `chromadb`
- `streamlit`
- `langchain-groq`
- `yfinance`

> ⚠️ **First run**: `sentence-transformers` will automatically download the `all-MiniLM-L6-v2` model (~90MB) on first use. This is a one-time download.

### Step 4 — Configure Environment Variables

```bash
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux
```

Open `.env` in a text editor and fill in:

```env
# === REQUIRED ===
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx   # Get at console.groq.com (free)

# === LLM Configuration ===
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile

# === ChromaDB ===
CHROMA_PERSIST_DIR=./data/chromadb
CHROMA_COLLECTION_NAME=risk_reports

# === Embeddings (runs locally, no key needed) ===
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# === App Settings ===
APP_NAME=RiskPulse AI
APP_VERSION=1.0.0
LOG_LEVEL=INFO
```

### Step 5 — Generate Synthetic Data

```bash
python -m backend.data.data_generator
```

This creates:

- `backend/data/generated/projects.json` — 15 realistic IT project records
- `backend/data/generated/market_signals.json` — 20 market signal records

You only need to run this once unless you want fresh data.

### Step 6 — Run the Application

```bash
streamlit run app.py
```

The terminal will show:

```
  You can now view your Streamlit app in your browser.
  Local URL:  http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open `http://localhost:8501` in your browser.

---

## 📖 Usage Guide

### Tab 1 — 🏠 Dashboard

The main overview screen. Shows after you run an analysis.

**What you see:**

- **4 KPI Cards** at the top: Portfolio Risk Score, Projects at Risk, Market Risk Score, Active Alerts
- **Bar Chart** — all 15 projects scored with LOW/MEDIUM/HIGH/CRITICAL threshold lines
- **Donut Chart** — distribution of risk levels across the portfolio
- **Project Cards** — compact view of each project with risk badge, score bar, and top alerts
- **Market Intelligence** — economic signals affecting the portfolio

**How to use:**

1. First click **⚙️ Run Analysis** tab and run an analysis
2. Come back to Dashboard — everything populates automatically
3. Click any project card to jump to its detailed view in the Projects tab

### Tab 2 — 📋 Projects

Deep-dive view for each of the 15 projects.

**What you see per project:**

- Header with project code, name, risk level badge, and overall score
- **Executive Summary** — one-paragraph AI-generated summary of the project's risk situation
- **Active Alerts** — color-coded by severity (CRITICAL=red, HIGH=orange, MEDIUM=yellow, LOW=green)
- **Radar Chart** — spider web visualization across 7 risk dimensions
- **Category Bars** — horizontal bars for each dimension score
- **Evidence Cards** — "what drove this score" — specific data points with their risk contribution
- **Mitigation Action Plan** — prioritized steps with estimated impact, owner, and timeline

**How to navigate:**

- Use the tabs at the top of the Projects page to switch between projects
- Projects are sorted by risk score (highest risk first)

### Tab 3 — 🌐 Live Data

Upload your real project data and fetch external market feeds.

**Sub-tabs:**

#### 📡 External Feeds

Click **"🔄 Fetch All Live Data"** to pull:

- USD/INR rate (Frankfurter API)
- India GDP growth, inflation, unemployment (World Bank API)
- RBI Repo Rate (RBI DBIE)
- Nifty IT, TCS, Infosys, Wipro prices (Yahoo Finance)
- IT sector news headlines (RSS feeds)
- GitHub trending languages

Data is cached for 1 hour. No API keys required for any of these sources.

#### ✨ AI Smart Converter

Paste any unstructured text about a project — emails, status reports, meeting notes — and the Groq LLM will extract structured KPIs automatically.

**Example input:**

```
Project Nexus update: We're running about 3 weeks behind on the API integration
module. Budget is looking tight — we've used about 87% of our allocation with
2 months left. The client NPS dropped to 28 last month and we had 2 SLA
breaches. We still have 3 open positions we can't fill.
```

**Output:** A structured record with `schedule_delay_days=21`, `budget_utilized_pct=87`, `nps_score=28`, `sla_breaches_count=2`, `open_positions=3` that gets saved and matched during real analysis.

#### 📁 CSV/Excel Upload

Upload a spreadsheet of project KPIs. The system uses flexible column mapping — it recognizes common variations like `"delay"`, `"days_behind"`, `"schedule_delay"` all as `schedule_delay_days`.

**Required column:** `project_code` (must match the code in projects.json, e.g., `PROJ-001`)

**All other columns are optional.** Only the fields you provide will override synthetic data.

#### 📋 JSON Paste

For developers: paste a JSON array of `InternalDataRecord` objects directly.

#### ✏️ Manual Form

Fill in individual fields for a specific project using text inputs.

### Tab 4 — 💬 AI Chat

Conversational interface powered by RAG (Retrieval-Augmented Generation).

**How it works:**

1. You type a question
2. The system converts your question to an embedding vector
3. ChromaDB finds the most relevant risk report chunks
4. Groq (llama-3.3-70b) generates an answer grounded in those chunks
5. The answer is displayed with context about which data it used

**Example questions:**

- "Which project has the highest financial risk?"
- "What's driving the schedule delays on Project Atlas?"
- "How does the current market situation affect our portfolio?"
- "Give me a prioritized list of actions for this week"
- "Which projects have SLA breaches?"

> ⚠️ The chatbot requires you to run an analysis first (so data exists in ChromaDB). You also need a valid `GROQ_API_KEY` in your `.env`.

### Tab 5 — 📄 Reports

View detailed text reports for each project and the market intelligence summary.

**What's available:**

- Full project risk report (all 7 dimensions, all alerts, all mitigations)
- Portfolio summary report
- Market intelligence report
- Agent execution log (shows which agents ran, timing, confidence)

### Tab 6 — ⚙️ Run Analysis

The control panel for triggering analysis runs.

**Two modes:**

| Mode         | Button                      | What it uses                                        | When to use                      |
| ------------ | --------------------------- | --------------------------------------------------- | -------------------------------- |
| 🔵 Synthetic | "▶ Run Synthetic Analysis"  | Generated projects.json only — ignores any uploads  | Baseline, demo, presentations    |
| ⚡ Real Data | "⚡ Run Real Data Analysis" | Uploaded KPIs override synthetic fields per project | When you've uploaded actual data |

**After running both modes**, a comparison table appears showing:

- Portfolio score: Synthetic vs Real
- Per-project: which ones changed, by how much, with REAL/SYNTH badges
- Sorted by biggest change (most impacted projects first)

**🔍 Debug Panel** — click to expand and see:

- Exact contents of your `internal_data.json`
- Which projects matched and which didn't (per last real analysis)
- A code tester: type any project code to instantly check if it matches

---

## 📁 File Structure

```
risk_management/
│
├── app.py                              ← Entry point. 6-tab Streamlit application.
├── requirements.txt                    ← All Python packages with pinned versions.
├── .env                                ← Your API keys and config (NEVER commit this).
├── .env.example                        ← Safe template showing all required variables.
├── .gitignore                          ← Excludes .env, __pycache__, chromadb, cache.
│
├── config/
│   ├── __init__.py
│   └── llm_config.py                   ← LLM + embeddings setup. One-line provider switch.
│                                          Reads GROQ_API_KEY, LLM_MODEL from .env.
│                                          Initializes ChatGroq and HuggingFaceEmbeddings.
│
├── backend/
│   ├── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                  ← All Pydantic v2 data models:
│   │                                      ProjectData, RiskReport, RiskScores,
│   │                                      MitigationStrategy, PortfolioAnalysisResult,
│   │                                      InternalDataRecord, MarketSignal
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_generator.py           ← Generates 15 projects + 20 market signals.
│   │   │                                  Run once: python -m backend.data.data_generator
│   │   ├── realtime_data.py            ← All real data logic:
│   │   │                                  - INTERNAL_DATA_PATH (canonical absolute path)
│   │   │                                  - InternalDataProcessor (load/save/parse/clear)
│   │   │                                  - get_enriched_project_data() (matching function)
│   │   │                                  - External feed fetchers (World Bank, RBI, etc.)
│   │   └── generated/
│   │       ├── projects.json           ← 15 IT project records (auto-generated).
│   │       └── market_signals.json     ← 20 market signal records (auto-generated).
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── risk_manager.py             ← Orchestrator. Coordinates all agents.
│   │   │                                  run_full_analysis() is the main entry point.
│   │   ├── market_analysis_agent.py    ← Reads market signals → market_context dict.
│   │   │                                  Scores volatility, competitor threat,
│   │   │                                  regulatory risk, sector health.
│   │   ├── risk_scoring_agent.py       ← 7-dimension weighted risk scoring.
│   │   │                                  Real data matching + injection.
│   │   │                                  Generates alerts + mitigation strategies.
│   │   └── project_status_agent.py     ← Project health assessment.
│   │                                      Evaluates schedule, budget, team, client KPIs.
│   │
│   └── rag/
│       ├── __init__.py
│       └── rag_pipeline.py             ← ChromaDB storage + RAG-powered chat.
│                                          store_analysis_results() → embeds + stores
│                                          answer_question() → retrieve + generate
│
├── frontend/
│   ├── __init__.py
│   ├── state.py                        ← Session state management.
│   │                                      State.get_manager(), State.set_analysis(),
│   │                                      State.get_analysis(), State.init_rag()
│   ├── styles.py                       ← Global CSS for dark Command Center theme.
│   │                                      Space Grotesk + JetBrains Mono fonts.
│   │                                      CSS variables for colors, shadows, borders.
│   │
│   └── pages/
│       ├── __init__.py
│       ├── dashboard.py                ← 🏠 Dashboard tab: KPI cards, charts, alerts.
│       ├── projects.py                 ← 📋 Projects tab: radar charts, evidence, actions.
│       ├── chat.py                     ← 💬 AI Chat tab: conversation UI, RAG integration.
│       ├── reports.py                  ← 📄 Reports tab: detailed text reports.
│       ├── live_data.py                ← 🌐 Live Data tab: external feeds + upload forms.
│       └── run_analysis.py             ← ⚙️ Run Analysis tab: synthetic/real runners + debug.
│
└── data/
    ├── chromadb/                       ← ChromaDB vector database (auto-created).
    ├── internal_data.json              ← Your uploaded real project KPIs (auto-created).
    ├── internal_data.json.disabled     ← Temporary rename during synthetic runs.
    └── realtime_cache/                 ← External feed cache files (auto-created).
        ├── world_bank_cache.json
        ├── rbi_cache.json
        ├── stocks_cache.json
        └── news_cache.json
```

---

## ⚙️ Configuration

### `.env` File — All Variables

```env
# ═══════════════════════════════════════════════════
# REQUIRED — Groq API Key
# Get yours free at: https://console.groq.com
# ═══════════════════════════════════════════════════
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ═══════════════════════════════════════════════════
# LLM Configuration
# ═══════════════════════════════════════════════════
LLM_PROVIDER=groq
# Options: groq | bedrock | huggingface

LLM_MODEL=llama-3.3-70b-versatile
# Other Groq models: llama-3.1-8b-instant, mixtral-8x7b-32768

# ═══════════════════════════════════════════════════
# ChromaDB Vector Database
# ═══════════════════════════════════════════════════
CHROMA_PERSIST_DIR=./data/chromadb
CHROMA_COLLECTION_NAME=risk_reports

# ═══════════════════════════════════════════════════
# Embedding Model (runs locally, no key needed)
# ═══════════════════════════════════════════════════
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ═══════════════════════════════════════════════════
# App Settings
# ═══════════════════════════════════════════════════
APP_NAME=RiskPulse AI
APP_VERSION=1.0.0
LOG_LEVEL=INFO
# Options: DEBUG | INFO | WARNING | ERROR
```

### `.gitignore` — What Gets Excluded

```
.env                    # API keys — NEVER commit
.venv/                  # Virtual environment
__pycache__/            # Python bytecode
*.pyc
data/chromadb/          # Vector DB (regenerated)
data/internal_data*     # User's uploaded data
data/realtime_cache/    # External data cache
backend/data/generated/ # Auto-generated synthetic data
*.log
```

---

## 📐 Risk Scoring Formula

### 7 Dimensions and Their Weights

| Dimension        | Weight  | Key Inputs                                                                      |
| ---------------- | ------- | ------------------------------------------------------------------------------- |
| Schedule Risk    | **22%** | Delay days, milestone completion %, deadline risk score                         |
| Financial Risk   | **20%** | Budget utilized %, cost variance %, burn rate, revenue at risk                  |
| Resource Risk    | **20%** | Team utilization %, open positions, contractor dependency %                     |
| Technical Risk   | **12%** | Defect rate, test coverage %, tech debt score, change requests                  |
| Market Risk      | **10%** | Market volatility index, competitor threat level, regulatory change probability |
| Operational Risk | **10%** | NPS score, SLA breaches count, stakeholder satisfaction                         |
| Compliance Risk  | **6%**  | Open audit findings, license issues, GDPR risk score                            |

### Formula

```
Overall Score =
  (Schedule  × 0.22) +
  (Financial × 0.20) +
  (Resource  × 0.20) +
  (Technical × 0.12) +
  (Market    × 0.10) +
  (Operational × 0.10) +
  (Compliance × 0.06)
```

### Risk Levels

| Level    | Score Range | Color               | Meaning                                                  |
| -------- | ----------- | ------------------- | -------------------------------------------------------- |
| LOW      | 0 – 29      | 🟢 Green `#00d68f`  | Project is healthy, no immediate action needed           |
| MEDIUM   | 30 – 54     | 🔵 Blue `#3b82f6`   | Some risk areas need monitoring, plan mitigations        |
| HIGH     | 55 – 74     | 🟠 Orange `#ffa502` | Significant issues, escalation recommended within 1 week |
| CRITICAL | 75 – 100    | 🔴 Red `#ff4757`    | Immediate executive attention and intervention required  |

### Scoring Logic Per Dimension

Each dimension scores 0–100 and is capped at 100. Example for Schedule Risk:

```python
# Delay contribution
if delay_days > 60:   score += 40   # Very late
elif delay_days > 30: score += 25   # Late
elif delay_days > 14: score += 15   # Slightly late
elif delay_days > 0:  score += 8    # Minor delay

# Milestone completion contribution
completion = milestones_completed / milestones_total
if completion < 0.30:   score += 35   # Less than 30% done
elif completion < 0.50: score += 22
elif completion < 0.70: score += 12
elif completion < 0.90: score += 5

# Deadline risk (from project attributes)
score += min(deadline_risk_score * 0.25, 25)
```

---

## 🔄 Data Pipeline

### Synthetic Data Generation

`backend/data/data_generator.py` generates:

**15 IT Projects** covering:

- Enterprise ERP implementations
- Cloud migration projects
- AI/ML platform development
- Mobile banking applications
- Digital transformation programs
- Cybersecurity infrastructure
- DevOps automation platforms

Each project has 30+ fields covering all 7 risk dimensions, with realistic India IT sector context (INR budgets, Indian client names, realistic delay scenarios).

**20 Market Signals** including:

- Nifty IT index performance
- USD/INR exchange rate volatility
- BFSI sector health index
- IT hiring market conditions
- Cloud spending forecast changes
- Regulatory compliance updates
- Global supply chain disruption index

### Real Data Injection

When you upload data and run **⚡ Real Data Analysis**, here's exactly what happens for each project:

```
1. RiskScoringAgent loads internal_data.json
2. For project code "PROJ-001":
   a. Strip + uppercase the code: "PROJ-001"
   b. Search all uploaded records for matching project_code (case-insensitive)
   c. If no code match, try matching by project_name (case-insensitive)
   d. If match found: inject non-None fields from the record over the synthetic values
   e. Tag project._real_data = matched_record
   f. Score using the now-overridden field values
   g. Set RiskReport.used_real_data = True, data_source_label = "REAL DATA"
3. If no match: score using synthetic values only, tag SYNTHETIC
```

**Fields that real data can override:**

| Field                       | Type  | Description                              |
| --------------------------- | ----- | ---------------------------------------- |
| `project_code`              | str   | Must match project code in projects.json |
| `project_name`              | str   | Alternative match if code doesn't match  |
| `schedule_delay_days`       | int   | Days behind schedule                     |
| `milestones_completed`      | int   | Number of milestones done                |
| `milestones_total`          | int   | Total planned milestones                 |
| `budget_utilized_pct`       | float | % of budget spent                        |
| `burn_rate_monthly`         | float | Monthly spend rate                       |
| `cost_variance_pct`         | float | % over/under planned cost                |
| `team_utilization_pct`      | float | % of team capacity being used            |
| `open_positions`            | int   | Unfilled headcount                       |
| `contractor_dependency_pct` | float | % of team that are contractors           |
| `defect_rate`               | float | Defects per sprint/cycle                 |
| `test_coverage_pct`         | float | % of code covered by tests               |
| `technical_debt_score`      | float | 0–100 tech debt rating                   |
| `change_requests_pending`   | int   | Open change requests                     |
| `nps_score`                 | float | Client Net Promoter Score                |
| `sla_breaches_count`        | int   | Number of SLA breaches                   |
| `stakeholder_satisfaction`  | float | 0–100 satisfaction rating                |

---

## 📤 Real Data Upload

### Method 1 — AI Smart Converter (Recommended)

Paste any text. The Groq LLM reads the text and converts it into structured project KPI data.

The AI Smart Converter uses a prompt-engineered extraction pipeline that transforms unstructured content (emails, meeting notes, reports) into structured fields matching the `InternalDataRecord` schema.

This allows users to ingest project updates without manually entering data.

**Works with:**

- Project status emails
- Weekly status reports
- Meeting notes
- Slack/Teams messages copy-pasted
- Excel cell contents

**Example prompt sent to Groq:**

```
Extract project KPI data from the following text. Return ONLY valid JSON matching
the InternalDataRecord schema. Include project_code if mentioned.

Text: [your pasted text]
```

### Method 2 — CSV/Excel Upload

Your CSV can have any column names. The system uses fuzzy mapping:

| Your column name                                       | Maps to                |
| ------------------------------------------------------ | ---------------------- |
| `delay`, `days_behind`, `schedule_delay`, `delay_days` | `schedule_delay_days`  |
| `budget_used`, `budget_%`, `budget_pct`, `spend_pct`   | `budget_utilized_pct`  |
| `nps`, `net_promoter`, `client_nps`                    | `nps_score`            |
| `sla_breach`, `sla_violations`, `breaches`             | `sla_breaches_count`   |
| `team_util`, `utilization`, `capacity_used`            | `team_utilization_pct` |
| `open_roles`, `vacancies`, `open_hc`                   | `open_positions`       |

> **Critical:** One column must be `project_code` (or a recognized variant). This is used to match your data to the project in `projects.json`.

**Example valid CSV:**

```csv
project_code,schedule_delay_days,budget_utilized_pct,nps_score,sla_breaches_count
PROJ-001,18,79,42,1
PROJ-005,61,94,12,4
PROJ-009,0,55,68,0
```

### Method 3 — JSON Paste

```json
[
  {
    "project_code": "PROJ-001",
    "schedule_delay_days": 18,
    "budget_utilized_pct": 79.0,
    "nps_score": 42.0,
    "sla_breaches_count": 1,
    "open_positions": 2,
    "team_utilization_pct": 88.5
  }
]
```

### Method 4 — Manual Form

Fill individual fields in the UI form. Good for updating a single project.

### Troubleshooting Real Data Matching

If your real data isn't showing up after running real analysis:

1. Open the **🔍 Debug Panel** in the Run Analysis tab
2. Check what codes are saved in `internal_data.json`
3. Compare against the project codes shown in the Projects tab
4. Use the **"Test a project code"** input to verify a specific code

**Common issues:**

| Issue                             | Cause                        | Fix                                                                        |
| --------------------------------- | ---------------------------- | -------------------------------------------------------------------------- |
| All projects show SYNTHETIC       | No matching codes            | Make sure `project_code` in your CSV exactly matches codes like `PROJ-001` |
| Zero records in debug panel       | Upload didn't save           | Check error message after upload; look for write permission issues         |
| Some projects match, some don't   | Inconsistent code formatting | Ensure codes match case-insensitively — `proj-001` will match `PROJ-001`   |
| File uploaded but button disabled | `has_data` check failing     | Verify `InternalDataProcessor.load_internal_data()` returns records        |

---

## 🤖 API Reference (Key Classes)

### `ProjectRiskManager`

**File:** `backend/agents/risk_manager.py`

The main orchestrator. Initializes all agents and runs the full pipeline.

```python
from backend.agents.risk_manager import ProjectRiskManager

manager = ProjectRiskManager()
result = manager.run_full_analysis()
# result: PortfolioAnalysisResult
```

**Methods:**

- `run_full_analysis() → PortfolioAnalysisResult` — runs all agents, returns complete portfolio result

---

### `RiskScoringAgent`

**File:** `backend/agents/risk_scoring_agent.py`

Scores a single project. Handles real data matching internally.

```python
agent = RiskScoringAgent()
report = agent.analyze_project(project_data, market_context)
# report: RiskReport
# report.used_real_data: True if matched internal data
# report.data_source_label: "REAL DATA" or "SYNTHETIC"
```

---

### `InternalDataProcessor`

**File:** `backend/data/realtime_data.py`

Handles all internal data file operations.

```python
from backend.data.realtime_data import InternalDataProcessor, INTERNAL_DATA_PATH

# Load all uploaded records
records = InternalDataProcessor.load_internal_data()
# returns: List[InternalDataRecord]

# Save records (merges with existing)
InternalDataProcessor.save_internal_data(records)

# Parse CSV/Excel file bytes
records = InternalDataProcessor.parse_csv_upload(file_bytes, filename)

# Clear all uploaded data
InternalDataProcessor.clear_internal_data()

# The canonical absolute path to internal_data.json
print(INTERNAL_DATA_PATH)
# → C:\Users\...\risk_management\data\internal_data.json
```

---

### `RAGPipeline`

**File:** `backend/rag/rag_pipeline.py`

Manages ChromaDB storage and RAG-powered question answering.

```python
from backend.rag.rag_pipeline import RAGPipeline

rag = RAGPipeline()
rag.initialize()

# Store analysis results in ChromaDB
rag.store_analysis_results(portfolio_result)

# Answer a question using RAG
answer = rag.answer_question("Which project has the highest financial risk?")
```

---

### Pydantic Schemas

All data flows through typed schemas defined in `backend/models/schemas.py`:

```python
# The full portfolio analysis result
class PortfolioAnalysisResult(BaseModel):
    portfolio_risk_score:     float
    risk_level:               RiskLevel
    risk_reports:             List[RiskReport]
    total_projects_analyzed:  int
    high_risk_count:          int
    critical_count:           int
    analysis_timestamp:       str
    market_summary:           dict
    real_data_project_count:  int    # How many used uploaded data

# One project's risk report
class RiskReport(BaseModel):
    project_code:             str
    project_name:             str
    overall_risk_score:       float
    risk_level:               RiskLevel
    risk_scores:              RiskScores
    mitigation_strategies:    List[MitigationStrategy]
    used_real_data:           bool   # True if real data was matched
    data_source_label:        str    # "REAL DATA" or "SYNTHETIC"

# The 7-dimension scores
class RiskScores(BaseModel):
    schedule_risk:     float
    financial_risk:    float
    resource_risk:     float
    technical_risk:    float
    market_risk:       float
    operational_risk:  float
    compliance_risk:   float
```

---

## 💬 AI Chat & RAG System

### How RAG Works in RiskPulse AI

1. **Storage** (after each analysis run):
   - Each project's `RiskReport` is serialized to a structured text chunk
   - The portfolio summary is stored as a separate chunk
   - `sentence-transformers/all-MiniLM-L6-v2` converts each chunk to a 384-dimensional vector
   - All vectors + text are stored in ChromaDB at `./data/chromadb/`

2. **Retrieval** (when you ask a question):
   - Your question is embedded using the same model
   - ChromaDB finds the top-k most semantically similar chunks (default k=3)
   - Retrieved chunks are assembled into a context block

3. **Generation** (Groq + llama-3.3-70b):
   - System prompt: "You are a risk management AI. Answer ONLY from the provided context. Do not hallucinate."
   - User prompt: `[context chunks]\n\nQuestion: [your question]`
   - Groq generates the answer in ~0.5 seconds

### ChromaDB Collection Structure

Each document in ChromaDB has:

- **content**: The full text of a risk report section
- **metadata**: `{"project_code": "PROJ-001", "timestamp": "...", "type": "project_report"}`
- **embedding**: 384-dimensional float vector

### What the Chatbot Knows

After running analysis, the chatbot has access to:

- Overall risk score and level for all 15 projects
- All 7 dimension scores per project
- All active alerts with severity, description, and affected amounts
- All mitigation strategies with priority, owner, and timeline
- Portfolio-level summary and market intelligence
- Which projects used real uploaded data

### Topic Filtering

The chatbot will politely decline questions not related to project risk management:

```
User: "What's the capital of France?"
Bot: "I'm specialized in IT project risk management.
      Please ask me about project risks, scores, alerts,
      or mitigation strategies."
```

---

## 🌍 Live Data Sources

All external sources are fetched without API keys using public APIs.

| Source                   | Data                          | API Endpoint                                                  | Cache TTL |
| ------------------------ | ----------------------------- | ------------------------------------------------------------- | --------- |
| Frankfurter / ECB        | USD/INR exchange rate         | `api.frankfurter.app/latest?to=INR`                           | 1 hour    |
| World Bank Open Data     | India GDP growth rate         | `api.worldbank.org/v2/country/IN/indicator/NY.GDP.MKTP.KD.ZG` | 1 hour    |
| World Bank Open Data     | India inflation rate          | `api.worldbank.org/v2/country/IN/indicator/FP.CPI.TOTL.ZG`    | 1 hour    |
| World Bank Open Data     | India unemployment            | `api.worldbank.org/v2/country/IN/indicator/SL.UEM.TOTL.ZS`    | 1 hour    |
| RBI DBIE                 | India repo rate               | `dbie.rbi.org.in/DBIE/dbie.rbi`                               | 1 hour    |
| Yahoo Finance (yfinance) | Nifty IT, TCS, Infosys, Wipro | yfinance Python library                                       | 1 hour    |
| Economic Times RSS       | IT sector news                | `economictimes.indiatimes.com/tech/rssfeeds`                  | 1 hour    |
| Moneycontrol RSS         | Business news                 | `moneycontrol.com/rss/latestnews.xml`                         | 1 hour    |
| NDTV Business RSS        | Business headlines            | `feeds.feedburner.com/ndtvprofit-latest`                      | 1 hour    |
| GitHub Trending          | Top programming languages     | `github.com/trending` (scraping)                              | 1 hour    |

Cache files are stored in `risk_management/data/realtime_cache/` and invalidated after 1 hour, after which fresh data is fetched on next request.

---

## 🔧 Troubleshooting

### App Won't Start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

```bash
# Make sure your virtual environment is activated
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Mac/Linux

# Then install
pip install -r requirements.txt
```

**Error:** `streamlit: command not found`

```bash
# Run via python module instead
python -m streamlit run app.py
```

---

### ChromaDB Errors

**Error:** `Collection risk_reports already exists` or dimension mismatch

```bash
# Delete and regenerate the vector database
rmdir /s data\chromadb    # Windows
rm -rf data/chromadb       # Mac/Linux

# Then restart the app and re-run analysis
```

---

### AI Chat Not Working

**Symptom:** Chat shows "LLM not available" or gives generic responses

1. Check your `.env` has `GROQ_API_KEY=gsk_...`
2. Verify the key is valid at [console.groq.com](https://console.groq.com)
3. Make sure you have run an analysis first (so ChromaDB has data)
4. Check terminal for error messages

---

### Real Data Not Being Used

**Symptom:** After uploading data and running Real Analysis, the Debug Panel shows "ZERO projects used real data"

1. Open the **🔍 Debug Panel** in the Run Analysis tab
2. Check the "Your uploaded internal records" table — are records there?
3. Check the "project_code" column — does it match exactly? (e.g., `PROJ-001` not `proj001` or `P001`)
4. Use the **"Test a project code"** input to verify

**Common fix:**

```
Wrong:  proj-001, P001, Project Atlas, Atlas
Right:  PROJ-001  (must match the code shown in the Projects tab)
```

---

### Embeddings Slow on First Run

The `sentence-transformers` model (~90MB) downloads automatically on first run. This is a one-time download stored in your HuggingFace cache directory (`~/.cache/huggingface/`). Subsequent runs are fast.

---

### Windows Long Path Issues

If you see file path errors on Windows:

```powershell
# Enable long paths in Windows (run as Administrator)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

---

## ⚠️ Known Limitations

| Limitation                | Description                                                         | Planned Fix                                   |
| ------------------------- | ------------------------------------------------------------------- | --------------------------------------------- |
| **Synthetic data**        | Projects are generated, not pulled from real tools like Jira or SAP | Connect to real project management APIs in v2 |
| **No authentication**     | Anyone with the URL can access the dashboard                        | Add login with Streamlit-Authenticator        |
| **ChromaDB accumulation** | Each analysis run adds chunks; no deduplication                     | Add collection reset before each store        |
| **Single-user**           | Designed for one user; no multi-tenancy                             | Session isolation for cloud deployment        |
| **No scheduling**         | Analysis must be triggered manually                                 | Add APScheduler for automated runs            |
| **English only**          | UI and chat are English-only                                        | i18n layer for multi-language support         |

---

## 🗺️ Roadmap

### v1.1 (Next)

- [ ] Reset ChromaDB collection before storing (prevent accumulation)
- [ ] Add email alerts for CRITICAL projects (SMTP integration)
- [ ] Export portfolio report as PDF
- [ ] Add Jira API connector for real schedule data

### v1.2

- [ ] User authentication (Streamlit-Authenticator)
- [ ] GitHub Actions CI pipeline with pytest tests
- [ ] Docker containerization for easy deployment
- [ ] Slack webhook alerts

### v2.0

- [ ] Deploy to AWS/Azure with real URL
- [ ] Multi-tenant architecture (separate data per organization)
- [ ] Connect to SAP, MS Project, ServiceNow APIs
- [ ] Switch LLM to AWS Bedrock (Claude 3 Sonnet) for enterprise SLA

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Setup for Development

```bash
git clone https://github.com/dangerSayan/AI-Powered-Risk-Management-System.git
cd AI-Powered-Risk-Management-System/risk_management
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### Project Conventions

- **Schemas first** — any new data type goes in `backend/models/schemas.py` as a Pydantic model
- **Agents are pure Python** — no LLM calls inside agents (scoring is deterministic)
- **Log everything** — use `from loguru import logger` and log every significant action
- **Absolute paths only** — never use `Path("relative/path")` — always use `Path(__file__).resolve()`
- **Real data is additive** — real data overlays synthetic, never replaces the base project structure

### Submitting Changes

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly: `streamlit run app.py` and verify all 6 tabs work
5. Commit: `git commit -m "feat: add your feature description"`
6. Push and open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Sayan Bose

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙏 Acknowledgments

| Library / Service                                  | Use in this Project          |
| -------------------------------------------------- | ---------------------------- |
| [Streamlit](https://streamlit.io)                  | Web application framework    |
| [Groq](https://groq.com)                           | Ultra-fast LLM inference API |
| [ChromaDB](https://www.trychroma.com)              | Local vector database        |
| [sentence-transformers](https://sbert.net)         | Text embedding model         |
| [LangChain](https://langchain.com)                 | LLM application framework    |
| [Pydantic](https://docs.pydantic.dev)              | Data validation library      |
| [Plotly](https://plotly.com)                       | Interactive chart library    |
| [Loguru](https://loguru.readthedocs.io)            | Python logging library       |
| [World Bank Open Data](https://data.worldbank.org) | Economic indicators API      |
| [Frankfurter](https://www.frankfurter.app)         | Currency exchange rate API   |
| [yfinance](https://github.com/ranaroussi/yfinance) | Yahoo Finance data           |

---

<div align="center">

**Built with ❤️ by Sayan Bose**

_RiskPulse AI — Turning project data into actionable intelligence_

[![GitHub](https://img.shields.io/badge/GitHub-View%20Source-181717?style=for-the-badge&logo=github)](https://github.com/dangerSayan/AI-Powered-Risk-Management-System)

</div>

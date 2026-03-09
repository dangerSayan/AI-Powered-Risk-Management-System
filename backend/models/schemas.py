"""
schemas.py — Data Blueprints for RiskPulse AI
==============================================
Every piece of data in this system has a strict
shape defined here using Pydantic.

Why Pydantic?
- Validates data automatically
- Gives clear errors when data is wrong
- Converts Python objects to/from JSON easily
- Makes the codebase self-documenting

Rule: If a concept exists in our business domain,
it gets a schema. No raw dictionaries anywhere.
"""

# uuid generates unique IDs automatically
# datetime handles dates and times
# typing gives us List, Dict, Optional
# enum gives us Enum for fixed value lists
# pydantic gives us BaseModel and Field

import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================
# SECTION 1 — ENUMS
# Fixed lists of allowed values.
# If a value isn't in the Enum, Pydantic throws an error.
# ============================================================

class RiskLevel(str, Enum):
    """
    The four risk levels a project can be at.
    Inherits from str so it serializes to JSON as a string.

    LOW      → Score 0–29   → Green  → Monitor normally
    MEDIUM   → Score 30–54  → Blue   → Watch closely
    HIGH     → Score 55–74  → Amber  → Action needed
    CRITICAL → Score 75–100 → Red    → Emergency response
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProjectStatus(str, Enum):
    """
    Current delivery status of a project.
    This is different from RiskLevel — a project can be
    ON_TRACK but still have HIGH risk due to market conditions.
    """
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    DELAYED = "DELAYED"
    CRITICAL = "CRITICAL"
    COMPLETED = "COMPLETED"


class RiskCategory(str, Enum):
    """
    The 7 categories we score risk across.
    Each has a different weight in the final score formula.

    SCHEDULE    → 22% weight — Is timeline being met?
    FINANCIAL   → 20% weight — Is money healthy?
    RESOURCE    → 20% weight — Is team stable?
    TECHNICAL   → 12% weight — Is tech stack risky?
    MARKET      → 10% weight — Is external world stable?
    OPERATIONAL → 10% weight — Is client relationship healthy?
    COMPLIANCE  → 6%  weight — Any contract/legal risks?
    """
    FINANCIAL = "FINANCIAL"
    RESOURCE = "RESOURCE"
    SCHEDULE = "SCHEDULE"
    TECHNICAL = "TECHNICAL"
    MARKET = "MARKET"
    COMPLIANCE = "COMPLIANCE"
    OPERATIONAL = "OPERATIONAL"


class ProjectType(str, Enum):
    """
    Type of IT project.
    Used by Technical Risk scoring — some types are
    inherently more complex than others.
    e.g. Cloud Migration is riskier than a simple website.
    """
    WEB_DEVELOPMENT       = "Web Development"
    MOBILE_APP            = "Mobile App"
    DATA_ENGINEERING      = "Data Engineering"
    CLOUD_MIGRATION       = "Cloud Migration & Modernization"
    AI_ML                 = "AI/ML Platform Development"
    CYBERSECURITY         = "Cybersecurity & SOC Implementation"
    ERP_IMPLEMENTATION    = "Enterprise ERP Implementation"
    DATA_WAREHOUSE        = "Data Warehouse & Analytics Platform"
    HEALTHCARE_IS         = "Healthcare Information System"
    SUPPLY_CHAIN          = "Supply Chain Management System"
    DEVOPS_PLATFORM       = "DevOps & Internal Developer Platform"
    ECOMMERCE             = "E-commerce Platform Revamp"
    IOT_SMART_FACTORY     = "IoT & Smart Factory Implementation"
    HR_TECH               = "HR Tech & Gig Worker Platform"
    EDTECH_LMS            = "EdTech Learning Management System"
    FINTECH_GATEWAY       = "Fintech Payment Gateway"
    DIGITAL_TRANSFORMATION = "Digital Transformation Program"
    MOBILE_BANKING        = "Mobile Banking Application"


# ============================================================
# SECTION 2 — TEAM MEMBER
# Represents one person working on a project.
# ============================================================

class TeamMember(BaseModel):
    """
    One team member on a project.

    id              → Unique identifier, auto-generated
    name            → Full name
    role            → Job title (Backend Dev, QA, etc.)
    seniority       → Junior / Mid / Senior / Lead
    is_active       → False means they have resigned
    resignation_risk → 0.0 to 1.0 — how likely to leave soon
                       Calculated by Status Agent based on
                       seniority, workload, and market signals
    """
    id: str = Field(
        # default_factory means: run this function to get default value
        # lambda: ... is an anonymous function
        # uuid.uuid4() generates a random unique ID like "a3f9b2c1"
        # [:8] takes only first 8 characters
        default_factory=lambda: str(uuid.uuid4())[:8]
    )
    name: str
    role: str
    seniority: str  # "Junior", "Mid", "Senior", "Lead"
    is_active: bool = True
    resignation_risk: float = Field(
        default=0.0,
        ge=0.0,  # ge = greater than or equal to 0
        le=1.0   # le = less than or equal to 1
    )


# ============================================================
# SECTION 3 — FINANCIAL METRICS
# All money-related data for one project.
# Kept separate from Project so financial logic stays clean.
# ============================================================

class FinancialMetrics(BaseModel):
    """
    Financial health of a project.

    total_budget          → Original approved budget in INR
    spent_to_date         → How much has been spent so far
    projected_total       → AI-estimated final cost at current burn rate
    last_payment_date     → When did client last pay us
    payment_delay_days    → How many days late is the current payment
    payment_amount_pending → How much money client still owes
    burn_rate_monthly     → How much money is being spent per month
    """
    total_budget: float
    spent_to_date: float
    projected_total: float
    last_payment_date: Optional[date] = None  # Optional = can be None
    payment_delay_days: int = 0
    payment_amount_pending: float = 0.0
    burn_rate_monthly: float = 0.0

    @property
    def budget_utilization(self) -> float:
        """
        What percentage of budget has been spent.
        Calculated on the fly — never stored.

        Example: spent 80 lakh out of 100 lakh = 80%
        If this number is higher than current progress %,
        we're burning money faster than delivering work.
        """
        if self.total_budget <= 0:
            return 0.0
        return (self.spent_to_date / self.total_budget) * 100

    @property
    def is_over_budget(self) -> bool:
        """
        True if the projected final cost exceeds the budget.
        We check projected_total (not spent_to_date) because
        we want to catch overruns BEFORE they fully happen.
        """
        return self.projected_total > self.total_budget


# ============================================================
# SECTION 4 — PROJECT
# The main entity. Everything in RiskPulse revolves around
# analyzing Project objects.
# ============================================================

class Project(BaseModel):
    """
    One IT project being monitored.

    Uses TeamMember and FinancialMetrics as nested objects.
    This is called composition — building complex schemas
    from simpler, reusable ones.
    """

    # ── Identity ──────────────────────────────────────────────
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str                    # "Project Atlas"
    code: str                    # "PRJ-001" — short reference code
    client: str                  # "TCS", "Infosys" etc.
    project_type: ProjectType    # from our Enum above
    description: str             # one paragraph about the project

    # ── Timeline ──────────────────────────────────────────────
    start_date: date             # when project kicked off
    planned_end_date: date       # original deadline
    current_progress_percent: float = Field(
        ge=0,   # can't be below 0%
        le=100  # can't be above 100%
    )
    schedule_delay_days: int = 0  # 0 = on time, 30 = 1 month late

    # ── Team ──────────────────────────────────────────────────
    # List[TeamMember] means a list of TeamMember objects
    team: List[TeamMember] = []
    team_size_planned: int       # how many people were supposed to be on it
    resignations_last_30_days: int = 0  # key risk indicator

    # ── Financial ─────────────────────────────────────────────
    # FinancialMetrics is a nested object — stored inside Project
    financials: FinancialMetrics

    # ── Technical ─────────────────────────────────────────────
    # List[str] means a list of strings
    tech_stack: List[str] = []            # ["Python", "AWS", "React"]
    external_dependencies: List[str] = [] # ["Stripe API", "Salesforce"]

    # ── Client Health ─────────────────────────────────────────
    status: ProjectStatus = ProjectStatus.ON_TRACK
    client_satisfaction_score: float = Field(
        default=8.0,
        ge=0,   # 0 = completely unhappy
        le=10   # 10 = perfect satisfaction
    )
    # How many days since we last had a call/meeting with client
    # 0 = talked today, 14 = no contact in 2 weeks (risky!)
    last_client_communication_days: int = 0

    # ── Extended Client & Risk Fields ──────────────────────────
    nps_score: int = 0                    # Net Promoter Score
    sla_breaches_count: int = 0           # Number of SLA breaches
    change_requests_pending: int = 0      # Pending change requests
    key_person_dependency: bool = False   # Single point of failure risk
    contractor_count: int = 0             # Number of contractors

    # ── Metadata ──────────────────────────────────────────────
    # datetime.now is called at object creation time
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ============================================================
# SECTION 5 — RISK SCHEMAS
# These are the OUTPUT of the Risk Scoring Agent.
# ============================================================

class RiskFactor(BaseModel):
    """
    One specific risk identified in a project.

    Example: Financial Risk
    ├── category     = RiskCategory.FINANCIAL
    ├── description  = "Budget utilization and payment status"
    ├── impact_score = 72.0  (out of 100)
    ├── probability  = 0.85  (85% chance this becomes a real problem)
    ├── weight       = 0.20  (Financial = 20% of overall score)
    └── evidence     = [
            "Payment delayed 60 days (+39 pts)",
            "Projected 18% over budget (+27 pts)"
        ]

    The evidence list is crucial — it makes the score EXPLAINABLE.
    A manager can see exactly which facts drove the score up.
    """
    category: RiskCategory
    description: str
    impact_score: float = Field(ge=0, le=100)
    probability: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = []  # list of human-readable reasons


class MitigationStrategy(BaseModel):
    """
    One recommended action to reduce a specific risk.

    priority                  → 1 = do this first
    action                    → what exactly to do
    owner                     → who should do it (role, not name)
    timeline                  → "Immediate", "1 week", "2 weeks"
    estimated_risk_reduction  → how many points this drops the score
    effort                    → Low / Medium / High — how hard is it
    """
    priority: int
    action: str
    owner: str
    timeline: str
    estimated_risk_reduction: float  # in score points
    effort: str  # "Low", "Medium", "High"


class RiskReport(BaseModel):
    """
    The complete risk output for ONE project.
    This is what gets stored in ChromaDB and shown in the UI.

    Generated by: Risk Scoring Agent
    Consumed by:  Frontend, RAG Pipeline, Risk Manager
    """

    # ── Identity ──────────────────────────────────────────────
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    project_id: str
    project_name: str
    project_code: str

    # ── Scores ────────────────────────────────────────────────
    overall_risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    previous_risk_score: Optional[float] = None  # for trend tracking
    risk_trend: str = "STABLE"  # "UP", "DOWN", or "STABLE"

    # ── Breakdown ─────────────────────────────────────────────
    risk_factors: List[RiskFactor] = []
    # Dict maps category name → score
    # Example: {"FINANCIAL": 72.0, "SCHEDULE": 45.0, ...}
    category_scores: Dict[str, float] = {}

    # ── Actions ───────────────────────────────────────────────
    mitigation_strategies: List[MitigationStrategy] = []

    # ── Narrative ─────────────────────────────────────────────
    # These are the text summaries generated for humans to read
    executive_summary: str = ""  # 2-3 sentence overview
    detailed_analysis: str = ""  # full markdown breakdown
    key_alerts: List[str] = []   # urgent bullet points

    # ── Metadata ──────────────────────────────────────────────
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = "RiskPulse AI"

    # NEW FIELD
    real_data: Optional[Dict[str, Any]] = None


# ============================================================
# SECTION 6 — MARKET SCHEMAS
# External world data — economy, industry, news signals.
# Used by Market Analysis Agent.
# ============================================================

class MarketSignal(BaseModel):
    """
    One piece of market intelligence.

    signal_type    → "news", "economic_indicator", "industry_trend"
    source         → "NASSCOM", "RBI", "Economic Times"
    headline       → the main news line
    summary        → 1-2 sentence explanation
    sentiment      → "positive", "negative", "neutral"
    relevance_score → 0 to 1 — how much does this affect IT projects
    impact_on_it   → plain English explanation of the impact
    """
    signal_type: str = "news"                    # default — not in new data
    source: str
    headline: str
    summary: str = ""                            # optional now
    sentiment: str
    relevance_score: float = Field(default=0.7, ge=0.0, le=1.0)  # default 0.7
    impact_on_it: str = ""
    published_date: datetime = Field(default_factory=datetime.now)
    # NEW fields from data_generator
    severity: str = "medium"
    affected_sectors: List[str] = []
    description: str = ""
    date: str = ""


class MarketAnalysis(BaseModel):
    """
    The compiled market picture.
    Output of the Market Analysis Agent.

    overall_market_sentiment → "BEARISH", "CAUTIOUS", "NEUTRAL", "BULLISH"
    market_risk_score        → 0-100, fed into each project's Market score
    signals                  → all individual signals analyzed
    key_trends               → list of trend summaries
    it_sector_outlook        → paragraph about IT sector health
    """
    overall_market_sentiment: str
    market_risk_score: float = Field(ge=0, le=100)
    signals: List[MarketSignal] = []
    key_trends: List[str] = []
    it_sector_outlook: str
    analyzed_at: datetime = Field(default_factory=datetime.now)


# ============================================================
# SECTION 7 — SYSTEM RESULT AND CHAT SCHEMAS
# The top-level outputs of a full analysis run.
# ============================================================

class AgentOutput(BaseModel):
    """
    Metadata about what one agent did during a run.
    Used for logging, debugging, and showing in the UI.

    agent_name          → which agent ran
    task_completed      → what it did in plain English
    output              → the key results as a dict
    confidence          → 0 to 1, how confident the agent is
    processing_time_seconds → performance tracking
    errors              → any non-fatal issues encountered
    """
    agent_name: str
    task_completed: str
    output: Dict[str, Any]  # Any = any Python type
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time_seconds: float = 0.0
    errors: List[str] = []


class SystemAnalysisResult(BaseModel):
    """
    The complete output of one full analysis pipeline run.
    Contains everything — all project reports + market data.

    This is what gets:
    - Stored in st.session_state for the UI to read
    - Passed to the RAG pipeline for storage in ChromaDB
    - Referenced by the chatbot to answer questions
    """
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])

    # Core outputs
    risk_reports: List[RiskReport]        # one per project
    market_analysis: MarketAnalysis       # one per run

    # Agent execution logs
    agent_outputs: List[AgentOutput] = []

    # Portfolio-level metrics
    portfolio_risk_score: float           # weighted average across all projects
    most_critical_project: Optional[str] = None  # "PRJ-005 - Project Zenith (81/100)"
    total_projects_analyzed: int
    high_risk_count: int                  # number of HIGH + CRITICAL projects

    analyzed_at: datetime = Field(default_factory=datetime.now)


class ChatMessage(BaseModel):
    """
    One message in the chatbot conversation.

    role               → "user" = you typed it
                         "assistant" = AI responded
    content            → the actual message text
    timestamp          → when was it sent
    referenced_projects → which project codes were mentioned
    context_used       → did the RAG pipeline find relevant context
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    referenced_projects: List[str] = []
    context_used: bool = False
"""
data_generator.py — Synthetic IT Project Data
==============================================
Creates 5 realistic IT projects covering all risk scenarios.

Why synthetic data?
- No real client data needed
- Full control over risk scenarios
- Consistent demo results
- Easy to swap for real DB later

Generated files:
- backend/data/generated/projects.json
- backend/data/generated/market_signals.json
"""

import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

# Import our schemas — the blueprints we built in Step 3
from backend.models.schemas import (
    Project,
    TeamMember,
    FinancialMetrics,
    ProjectStatus,
    ProjectType,
    MarketSignal
)

# Seed makes random numbers consistent
# Same seed = same "random" data every time
# This means our project scores won't change between runs
random.seed(42)


# ============================================================
# REFERENCE DATA
# These are the lookup lists used when generating projects.
# In a real system, these would come from your HR system,
# your CRM, your finance system, etc.
# ============================================================

# Indian IT companies as our clients
CLIENTS = [
    "Infosys Ltd",
    "Tata Consultancy Services",
    "Wipro Technologies",
    "HCL Technologies",
    "Tech Mahindra",
    "Capgemini India",
    "Cognizant India",
    "LTIMindtree",
]

# Tech stacks per project type
# When we create a project, we pick the right stack for its type
TECH_STACKS = {
    ProjectType.WEB_DEVELOPMENT:    ["React", "Node.js", "PostgreSQL", "Redis", "Docker", "AWS S3"],
    ProjectType.MOBILE_APP:         ["Flutter", "Firebase", "Kotlin", "Swift", "REST APIs", "AWS Cognito"],
    ProjectType.DATA_ENGINEERING:   ["Python", "Apache Spark", "Kafka", "Airflow", "Snowflake", "dbt"],
    ProjectType.CLOUD_MIGRATION:    ["AWS", "Terraform", "Docker", "Kubernetes", "Jenkins", "CloudWatch"],
    ProjectType.AI_ML:              ["Python", "TensorFlow", "MLflow", "FastAPI", "PostgreSQL", "Pandas"],
    ProjectType.CYBERSECURITY:      ["Python", "SIEM Tools", "Nessus", "Splunk", "IAM", "Zero Trust"],
    ProjectType.ERP_IMPLEMENTATION: ["SAP S/4HANA", "Oracle ERP", "Java", "REST APIs", "Oracle DB"],
}

# All possible roles on an IT project team
ROLES = [
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Data Engineer",
    "QA Engineer",
    "Business Analyst",
    "Tech Lead",
    "Scrum Master",
    "Solution Architect"
]

# Indian developer first names for realistic team data
FIRST_NAMES = [
    "Arjun", "Priya", "Rahul", "Sneha", "Vikram",
    "Ananya", "Karthik", "Divya", "Rohit", "Meera",
    "Aditya", "Pooja", "Suresh", "Kavitha", "Nikhil"
]

# Indian developer last names
LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Nair",
    "Iyer", "Reddy", "Joshi", "Gupta", "Mehta",
    "Pillai", "Rao", "Verma", "Shah", "Chatterjee"
]


# ============================================================
# HELPER FUNCTION 1 — generate_team()
# Creates a list of TeamMember objects for a project.
# ============================================================

def generate_team(team_size: int, resignations: int) -> list:
    """
    Creates team_size members, where the first 'resignations'
    members are marked as resigned (is_active = False).

    Why this approach?
    By making the resigned members the "first" ones,
    the data is consistent — same project always has
    the same people resigned.

    Args:
        team_size:    total number of people planned
        resignations: how many have resigned

    Returns:
        List of TeamMember objects
    """
    team = []
    seniority_levels = ["Junior", "Mid", "Senior", "Lead"]

    for i in range(team_size):
        # First 'resignations' members are inactive (resigned)
        is_active = (i >= resignations)

        # Senior/Lead resignations hurt more
        # We assign seniority in order so early members
        # (who resign) are more senior
        if i < resignations:
            # Resigned members — tend to be Senior/Lead
            seniority = random.choice(["Senior", "Lead"])
        else:
            # Active members — mix of all levels
            seniority = random.choice(seniority_levels)

        member = TeamMember(
            name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            role=random.choice(ROLES),
            seniority=seniority,
            is_active=is_active,
            # Resigned members have risk=1.0 (already happened)
            # Active members have some ongoing risk
            resignation_risk=1.0 if not is_active else round(
                random.uniform(0.1, 0.5), 2
            )
        )
        team.append(member)

    return team


# ============================================================
# HELPER FUNCTION 2 — generate_financials()
# Creates FinancialMetrics for a project.
# ============================================================

def generate_financials(
    budget: float,
    progress_percent: float,
    payment_delay_days: int,
    scenario: str
) -> FinancialMetrics:
    """
    Creates realistic financial data based on scenario type.

    Three scenarios:
    - "on_track"    → spending matches progress, no overrun
    - "over_budget" → spending ahead of progress, overrun expected
    - "critical"    → severe overspend, late payments

    Args:
        budget:             total approved budget in INR
        progress_percent:   how complete the project is (0-100)
        payment_delay_days: how many days client payment is late
        scenario:           "on_track", "over_budget", or "critical"

    Returns:
        FinancialMetrics object
    """
    from datetime import date, timedelta

    # Base spend: what you'd expect given current progress
    expected_spend = budget * (progress_percent / 100)

    if scenario == "on_track":
        # Actual spend is very close to expected
        actual_spent = expected_spend * random.uniform(0.92, 1.05)
        projected = budget * random.uniform(0.97, 1.03)

    elif scenario == "over_budget":
        # Spending faster than progress — overrun coming
        actual_spent = expected_spend * random.uniform(1.15, 1.35)
        projected = budget * random.uniform(1.12, 1.28)

    else:  # critical
        # Serious overspend
        actual_spent = expected_spend * random.uniform(1.35, 1.55)
        projected = budget * random.uniform(1.28, 1.45)

    # Monthly burn rate: total budget divided by project duration months
    # We assume 10-14 month projects on average
    burn_rate = budget / random.uniform(10, 14)

    # Last payment was 30 days before the delay started
    last_payment = date.today() - timedelta(days=payment_delay_days + 30)

    return FinancialMetrics(
        total_budget=round(budget, 2),
        spent_to_date=round(min(actual_spent, budget * 1.5), 2),
        projected_total=round(projected, 2),
        last_payment_date=last_payment,
        payment_delay_days=payment_delay_days,
        # Pending amount is a portion of total budget
        payment_amount_pending=round(budget * random.uniform(0.08, 0.25), 2),
        burn_rate_monthly=round(burn_rate, 2)
    )


# ============================================================
# MAIN FUNCTION — create_projects()
# Builds all 5 Project objects with carefully designed
# risk scenarios.
# ============================================================

def create_projects() -> list:
    """
    Creates 5 IT projects with different risk profiles.

    The design intent:
    - PRJ-001: HIGH risk  (cloud migration problems)
    - PRJ-002: LOW risk   (AI/ML project going well)
    - PRJ-003: CRITICAL   (web dev with team collapse)
    - PRJ-004: LOW risk   (data engineering nearly complete)
    - PRJ-005: CRITICAL   (mobile app disaster scenario)

    Returns:
        List of 5 Project objects
    """
    today = date.today()

    # Each tuple contains all the config for one project:
    # (code, name, type, description,
    #  start_offset_days, duration_months,
    #  budget_inr, progress_pct, schedule_delay_days,
    #  team_size, resignations, payment_delay_days,
    #  financial_scenario, client_satisfaction, days_since_client_call)
    projects_config = [

        # ── PRJ-001: Project Atlas ──────────────────────────
        # Cloud migration that's struggling
        # 2 senior resignations + 25-day delay + budget overrun
        (
            "PRJ-001",
            "Project Atlas",
            ProjectType.CLOUD_MIGRATION,
            (
                "Large-scale AWS cloud migration for a legacy core banking "
                "system with 200+ microservices. Involves lift-and-shift of "
                "on-premise infrastructure to AWS with zero downtime requirement."
            ),
            -180,           # started 180 days ago
            12,             # 12 month project
            4_500_000,      # ₹45 lakh budget
            45,             # 45% done
            25,             # 25 days behind schedule
            12,             # 12 team members planned
            2,              # 2 have resigned
            60,             # client payment 60 days late
            "over_budget",
            6.5,            # client satisfaction 6.5/10
            12              # no client call for 12 days
        ),

        # ── PRJ-002: Project Helix ──────────────────────────
        # AI/ML project running smoothly
        # Healthy team, on schedule, client happy
        (
            "PRJ-002",
            "Project Helix",
            ProjectType.AI_ML,
            (
                "AI-driven predictive analytics platform for supply chain "
                "optimization. Uses ML models to forecast demand, detect "
                "anomalies, and recommend inventory adjustments in real time."
            ),
            -90,            # started 90 days ago
            8,              # 8 month project
            2_800_000,      # ₹28 lakh budget
            65,             # 65% done — ahead of schedule!
            0,              # no delay
            8,              # 8 team members
            0,              # no resignations
            10,             # payment only 10 days late (normal)
            "on_track",
            8.8,            # very happy client
            3               # talked 3 days ago
        ),

        # ── PRJ-003: Project Nova ───────────────────────────
        # Web development project in serious trouble
        # Most resignations, low client satisfaction
        (
            "PRJ-003",
            "Project Nova",
            ProjectType.WEB_DEVELOPMENT,
            (
                "Enterprise customer self-service portal with real-time "
                "analytics dashboards, ticket management, and integration "
                "with Salesforce CRM and SAP billing systems."
            ),
            -120,           # started 120 days ago
            10,             # 10 month project
            1_800_000,      # ₹18 lakh budget
            30,             # only 30% done
            40,             # 40 days behind — serious
            10,             # 10 team members planned
            3,              # 3 resigned — worst team loss
            45,             # 45 day payment delay
            "over_budget",
            5.5,            # unhappy client
            18              # 18 days no contact — very risky
        ),

        # ── PRJ-004: Project Orion ──────────────────────────
        # Data engineering project nearly complete
        # Stable team, good financials, almost done
        (
            "PRJ-004",
            "Project Orion",
            ProjectType.DATA_ENGINEERING,
            (
                "End-to-end data lake implementation with real-time "
                "streaming pipelines using Apache Kafka and Spark. "
                "Includes historical data migration and BI dashboard setup."
            ),
            -240,           # started 240 days ago
            9,              # 9 month project
            3_200_000,      # ₹32 lakh budget
            88,             # 88% complete — almost done!
            0,              # no delay
            9,              # 9 team members
            0,              # no resignations
            5,              # almost no payment delay
            "on_track",
            9.1,            # very satisfied client
            2               # talked 2 days ago
        ),

        # ── PRJ-005: Project Zenith ─────────────────────────
        # Mobile app project in critical state
        # Worst delay + worst payment delay combination
        (
            "PRJ-005",
            "Project Zenith",
            ProjectType.MOBILE_APP,
            (
                "Cross-platform mobile banking app for retail customers "
                "with biometric authentication, UPI integration, and "
                "real-time transaction alerts. iOS and Android delivery."
            ),
            -150,           # started 150 days ago
            14,             # 14 month project
            2_200_000,      # ₹22 lakh budget
            20,             # only 20% done — very behind
            55,             # 55 days behind — critical
            11,             # 11 team members
            2,              # 2 resignations
            75,             # 75 day payment delay — worst
            "over_budget",
            5.0,            # very unhappy client
            22              # 22 days no contact — alarming
        ),
    ]

    projects = []

    for config in projects_config:
        (
            code, name, ptype, description,
            start_offset, duration_months,
            budget, progress, delay_days,
            team_size, resignations, payment_delay,
            fin_scenario, client_score, client_comms
        ) = config

        # Calculate dates
        start_date = today + timedelta(days=start_offset)
        planned_end = start_date + timedelta(days=duration_months * 30)

        # Calculate elapsed time percentage
        # This tells us: "how far through the project are we TIME-wise?"
        total_days = max((planned_end - start_date).days, 1)
        elapsed_days = max((today - start_date).days, 0)
        time_elapsed_pct = (elapsed_days / total_days) * 100

        # Determine project status based on delay and team issues
        # This mirrors how a real PMO would classify projects
        if delay_days > 45 or resignations >= 3:
            status = ProjectStatus.CRITICAL
        elif delay_days > 20 or resignations >= 2:
            status = ProjectStatus.DELAYED
        elif progress >= (time_elapsed_pct - 10):
            # Progress is within 10% of expected → on track
            status = ProjectStatus.ON_TRACK
        else:
            status = ProjectStatus.AT_RISK

        # Build the Project object using our schema
        project = Project(
            code=code,
            name=name,
            client=random.choice(CLIENTS),
            project_type=ptype,
            description=description,
            start_date=start_date,
            planned_end_date=planned_end,
            current_progress_percent=float(progress),
            schedule_delay_days=delay_days,
            team=generate_team(team_size, resignations),
            team_size_planned=team_size,
            resignations_last_30_days=resignations,
            financials=generate_financials(
                budget, progress, payment_delay, fin_scenario
            ),
            tech_stack=TECH_STACKS.get(ptype, ["Python", "Docker"]),
            external_dependencies=random.sample(
                ["AWS", "Azure", "Salesforce", "SAP", "Stripe", "Twilio", "Razorpay"],
                k=2  # pick 2 random dependencies
            ),
            status=status,
            client_satisfaction_score=float(client_score),
            last_client_communication_days=client_comms
        )
        projects.append(project)

    return projects


# ============================================================
# MARKET SIGNALS
# 6 realistic signals reflecting current Indian IT market.
# Mix of negative and positive to create a CAUTIOUS outlook.
# ============================================================

def generate_market_signals() -> list:
    """
    Returns 6 realistic market signals that affect IT projects.

    These are written to reflect real conditions in the
    Indian IT industry — NASSCOM reports, RBI decisions,
    BFSI sector behavior, talent market trends.

    In production: these would come from NewsAPI, Bloomberg,
    Alpha Vantage, and NASSCOM data feeds.
    """
    signals = [
        {
            "signal_type": "economic_indicator",
            "source": "Reserve Bank of India",
            "headline": "RBI holds repo rate at 6.5% amid global uncertainty",
            "summary": (
                "RBI maintains rates but signals caution. IT spending "
                "budgets at large corporates expected to face scrutiny in H2."
            ),
            "sentiment": "negative",
            "relevance_score": 0.75,
            "impact_on_it": (
                "Client budget freezes likely. IT project approvals "
                "and renewals may slow down in banking sector."
            ),
        },
        {
            "signal_type": "industry_trend",
            "source": "NASSCOM Quarterly Report",
            "headline": "Indian IT sector revenue growth slows to 6.5% YoY from 11.2%",
            "summary": (
                "Discretionary IT spending cut by major BFSI and retail clients. "
                "Cloud migration projects being deferred to next fiscal year."
            ),
            "sentiment": "negative",
            "relevance_score": 0.90,
            "impact_on_it": (
                "Project delays and budget cuts expected in cloud and "
                "digital transformation segments."
            ),
        },
        {
            "signal_type": "news",
            "source": "Economic Times Technology",
            "headline": "Mid-level tech talent attrition rises to 18.3% in Q2",
            "summary": (
                "Competition from GCCs and product startups pushing "
                "mid-senior developer attrition to 18-month highs."
            ),
            "sentiment": "negative",
            "relevance_score": 0.85,
            "impact_on_it": (
                "Resource risk increases across all active projects. "
                "Replacement hiring taking 6-8 weeks on average."
            ),
        },
        {
            "signal_type": "economic_indicator",
            "source": "Bloomberg India Desk",
            "headline": "USD/INR stabilizes at 83.5 — rupee shows resilience",
            "summary": (
                "Rupee stabilization reduces forex risk for IT exporters. "
                "Offshore delivery model remains cost-competitive."
            ),
            "sentiment": "positive",
            "relevance_score": 0.60,
            "impact_on_it": (
                "Positive for offshore delivery margins. "
                "Cost competitiveness with global peers maintained."
            ),
        },
        {
            "signal_type": "industry_trend",
            "source": "Gartner IT Spending Forecast 2024",
            "headline": "AI/ML project investments surge 34% globally in 2024",
            "summary": (
                "Despite slowdown in traditional IT, GenAI and ML projects "
                "are accelerating with strong client willingness to invest."
            ),
            "sentiment": "positive",
            "relevance_score": 0.80,
            "impact_on_it": (
                "AI/ML projects are well-funded and protected from budget cuts. "
                "Strong tailwind for teams with ML capabilities."
            ),
        },
        {
            "signal_type": "news",
            "source": "Moneycontrol Markets",
            "headline": "BFSI sector IT budgets cut 15-20% after Q2 NPA spike",
            "summary": (
                "Banking clients reducing discretionary IT spends significantly. "
                "Core banking upgrades continue but new initiatives on hold."
            ),
            "sentiment": "negative",
            "relevance_score": 0.88,
            "impact_on_it": (
                "Payment delays and scope reductions in banking IT projects. "
                "Cloud migration timelines likely to slip by 1-2 quarters."
            ),
        },
    ]
    return signals


# ============================================================
# SAVE AND LOAD FUNCTIONS
# save_data()     → generates everything and saves to JSON files
# load_projects() → reads projects.json back as Project objects
# load_market_signals() → reads market_signals.json
# ============================================================

def save_data():
    """
    Generates all data and saves to JSON files.
    Creates the generated/ directory if it doesn't exist.
    Called once at app startup or when you want fresh data.
    """

    # Create the output directory
    # parents=True means create parent folders too if needed
    # exist_ok=True means don't error if folder already exists
    data_dir = Path("backend/data/generated")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate and save projects
    projects = create_projects()

    # model_dump(mode='json') converts the Pydantic object
    # to a dict that can be serialized to JSON
    # mode='json' ensures dates become strings not Python objects
    projects_data = [p.model_dump(mode="json") for p in projects]

    with open(data_dir / "projects.json", "w") as f:
        # indent=2 makes the JSON human-readable
        # default=str handles any remaining non-serializable objects
        json.dump(projects_data, f, indent=2, default=str)

    print(f"✅ Saved {len(projects)} projects to backend/data/generated/projects.json")

    # Generate and save market signals
    signals = generate_market_signals()

    with open(data_dir / "market_signals.json", "w") as f:
        json.dump(signals, f, indent=2, default=str)

    print(f"✅ Saved {len(signals)} market signals to backend/data/generated/market_signals.json")

    return projects, signals


def load_projects() -> list:
    """
    Loads projects from the saved JSON file.
    If file doesn't exist, generates data first.

    Why load from file instead of regenerating every time?
    Because regenerating means random.seed() runs again,
    which could change values. Loading from file gives
    consistent data across runs.

    Returns:
        List of Project objects
    """
    data_path = Path("backend/data/generated/projects.json")

    # If file doesn't exist, generate it first
    if not data_path.exists():
        print("📁 No project data found. Generating...")
        save_data()

    with open(data_path, "r") as f:
        raw_data = json.load(f)

    projects = []
    for raw in raw_data:

        # Convert nested dicts back into Pydantic objects
        # JSON stores TeamMember as a dict — we rebuild the object
        raw["team"] = [TeamMember(**m) for m in raw.get("team", [])]

        # Same for FinancialMetrics
        raw["financials"] = FinancialMetrics(**raw["financials"])

        # Convert date strings back to Python date objects
        # JSON stores dates as "2024-01-15" strings
        for date_field in ["start_date", "planned_end_date"]:
            if isinstance(raw.get(date_field), str):
                # Split on T in case it includes time component
                raw[date_field] = date.fromisoformat(
                    raw[date_field].split("T")[0]
                )

        projects.append(Project(**raw))

    return projects


def load_market_signals() -> list:
    """
    Loads market signals from the saved JSON file.
    Returns raw dicts (not Pydantic objects) because
    the Market Analysis Agent parses them itself.
    """
    data_path = Path("backend/data/generated/market_signals.json")

    if not data_path.exists():
        print("📁 No market signal data found. Generating...")
        save_data()

    with open(data_path, "r") as f:
        return json.load(f)


# ============================================================
# QUICK TEST
# Run this file directly to generate data and verify it works:
# python -m backend.data.data_generator
# ============================================================

if __name__ == "__main__":
    print("\n🚀 Generating RiskPulse AI test data...\n")

    projects, signals = save_data()

    print("\n📊 Projects Created:")
    print("-" * 60)
    for p in projects:
        print(
            f"  {p.code} | {p.name:<20} | "
            f"Progress: {p.current_progress_percent:>3.0f}% | "
            f"Delay: {p.schedule_delay_days:>2}d | "
            f"Status: {p.status.value}"
        )

    print("\n📈 Market Signals Created:")
    print("-" * 60)
    for s in signals:
        icon = "🔴" if s["sentiment"] == "negative" else "🟢"
        print(f"  {icon} [{s['source'][:20]:<20}] {s['headline'][:50]}")

    print("\n✅ Data generation complete!")
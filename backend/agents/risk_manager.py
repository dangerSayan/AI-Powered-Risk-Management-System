"""
risk_manager.py — Project Risk Manager (Orchestrator Agent)
===========================================================
The boss agent. Coordinates all specialist agents and
produces one unified SystemAnalysisResult.

This agent does NOT calculate risks itself.
It delegates to:
  - MarketAnalysisAgent   → external market risk
  - ProjectStatusAgent    → internal project health KPIs
  - RiskScoringAgent      → per-project risk scores

Then it aggregates everything into a portfolio-level view.

Design pattern: Orchestrator / Coordinator
  - Single entry point for the entire analysis pipeline
  - Controls data flow between agents
  - Agents are loosely coupled — they don't call each other
  - Only this class knows the full sequence
"""

import time
from datetime import datetime
from typing import List, Optional
from loguru import logger

from backend.models.schemas import (
    Project,
    RiskReport,
    RiskLevel,
    SystemAnalysisResult,
    AgentOutput,
)
from backend.agents.market_analysis_agent import MarketAnalysisAgent
from backend.agents.risk_scoring_agent import RiskScoringAgent
from backend.agents.project_status_agent import ProjectStatusAgent
from backend.data.realtime_data import get_enriched_project_data
from backend.data.data_generator import load_projects, load_market_signals


class ProjectRiskManager:
    """
    Master orchestrator for the entire risk analysis pipeline.

    Usage:
        manager = ProjectRiskManager()
        result  = manager.run_full_analysis()
        # result is a SystemAnalysisResult with everything inside

    Optional RAG integration:
        rag = RiskRAGPipeline()
        rag.initialize()
        manager = ProjectRiskManager(rag_pipeline=rag)
        result  = manager.run_full_analysis()
        # This also stores results in ChromaDB for chatbot use

    Why accept rag_pipeline as optional?
    Because the system should work without RAG.
    RAG only enhances the chatbot — analysis works without it.
    This is called "optional dependency" pattern.
    """

    def __init__(self, rag_pipeline=None):
        """
        Args:
            rag_pipeline: Optional RiskRAGPipeline instance.
                          If provided, analysis results are stored
                          in ChromaDB after each run.
                          If None, analysis still works — just no
                          chatbot memory.
        """
        # Store the RAG pipeline reference (can be None)
        self.rag_pipeline = rag_pipeline

        # Initialize all sub-agents
        # They're created here and reused for every analysis run
        self.market_agent = MarketAnalysisAgent()
        self.status_agent = ProjectStatusAgent()

        self.agent_name = "Project Risk Manager"

        logger.info(
            f"🎯 {self.agent_name} initialized | "
            f"RAG: {'enabled' if rag_pipeline else 'disabled'}"
        )

    # ── Main public method ────────────────────────────────────

    def run_full_analysis(
        self,
        projects: Optional[List[Project]] = None
    ) -> SystemAnalysisResult:
        """
        Runs the complete risk analysis pipeline.

        This is the only method the frontend needs to call.
        Everything else happens automatically inside here.

        Args:
            projects: Optional list of Project objects.
                      If None, loads from data_generator.
                      Passing projects explicitly allows the
                      frontend to pass custom/filtered data.

        Returns:
            SystemAnalysisResult containing:
            - All 5 RiskReport objects
            - MarketAnalysis
            - Portfolio-level metrics
            - Agent execution logs
        """
        pipeline_start = time.time()

        logger.info("=" * 55)
        logger.info("🚀 Starting Full Portfolio Risk Analysis")
        logger.info("=" * 55)

        # Collect AgentOutput from every agent for logging
        all_agent_outputs: List[AgentOutput] = []

        # ── Step 1: Load Data ──────────────────────────────────
        logger.info("📂 Step 1/5 — Loading project and market data...")

        from backend.data.realtime_data import load_uploaded_projects

        uploaded_projects = load_uploaded_projects()

        if uploaded_projects:
            logger.info("📊 Using uploaded real projects")
            raw_projects = uploaded_projects
        elif projects is None:
            logger.info("🧪 Using synthetic dataset")
            raw_projects = load_projects()
        else:
            raw_projects = projects

        # Convert raw dicts → Project objects
        # load_projects() returns plain dicts from JSON
        # Agents need proper Pydantic Project objects
        from datetime import date
        from backend.models.schemas import (
            FinancialMetrics, TeamMember, ProjectType, ProjectStatus
        )

        projects = []
        for p in raw_projects:

            # Try to load uploaded internal data
            enriched = get_enriched_project_data(p.get("id") or p.get("project_code"))

            if enriched:
                logger.info(f"⚡ Using uploaded data for {p['id']}")
                p["_real_data"] = enriched
            project = Project(
                id=p["id"],
                name=p["name"],
                code=p["id"],
                client=p["client"],
                project_type=ProjectType(p["type"]),
                description=p["description"],
                start_date=date.fromisoformat(p["start_date"]),
                planned_end_date=date.fromisoformat(p["planned_end_date"]),
                current_progress_percent=p["actual_completion_pct"],
                schedule_delay_days=(
                    enriched["schedule_delay_days"]
                    if enriched and enriched.get("schedule_delay_days") is not None
                    else p["days_behind_schedule"]
                ),
                team=[],
                team_size_planned=(
                    enriched["team_size"]
                    if enriched and enriched.get("team_size") is not None
                    else p["team_size"]
                ),
                resignations_last_30_days=p["resignations_last_30_days"],
                financials={
                    "total_budget": p["budget_inr"],
                    "spent_to_date": p["amount_spent_inr"],
                    "projected_total": p["amount_spent_inr"] + p["projected_overrun_inr"],
                    "payment_delay_days": p["payment_overdue_days"],
                    "payment_amount_pending": p["pending_invoices_inr"],
                    "burn_rate_monthly": p["amount_spent_inr"] / 6,
                },
                tech_stack=p.get("technology_stack", []),
                external_dependencies=p.get("vendor_dependencies", []),
                status=ProjectStatus.ON_TRACK,
                client_satisfaction_score=(
                    enriched["customer_satisfaction"] / 10
                    if enriched and enriched.get("customer_satisfaction") is not None
                    else p["client_satisfaction_score"]
                ),
                last_client_communication_days=p["days_since_last_client_contact"],
                nps_score=p.get("nps_score", 0),
                sla_breaches_count=p.get("sla_breaches_count", 0),
                change_requests_pending=p.get("change_requests_pending", 0),
                key_person_dependency=p.get("key_person_dependency", False),
                contractor_count=p.get("contractor_count", 0),
            )
            if enriched:
                project._real_data = enriched
            projects.append(project)

        from backend.data.realtime_data import ExternalDataFetcher, build_market_signals_from_external

        if uploaded_projects:
            logger.info("🌍 Fetching REAL external market data")

            external_data = ExternalDataFetcher.fetch_all()
            market_signals = build_market_signals_from_external(external_data)

        else:
            logger.info("🧪 Using synthetic market signals")
            market_signals = load_market_signals()

        logger.info(
            f"  Loaded {len(projects)} projects and "
            f"{len(market_signals)} market signals"
        )

        # ── Step 2: Market Analysis ────────────────────────────
        logger.info("🌐 Step 2/5 — Running Market Analysis Agent...")

        # Fetch real external market data first (fills cache)
        from backend.data.realtime_data import ExternalDataFetcher

        try:
            ExternalDataFetcher.fetch_all()
            logger.info("🌍 Real external market data fetched")
        except Exception as e:
            logger.warning(f"External market data fetch failed: {e}")

        market_analysis, market_output = self.market_agent.analyze(
            market_signals
        )

        market_analysis, market_output = self.market_agent.analyze(
            market_signals
        )
        all_agent_outputs.append(market_output)

        logger.info(
            f"  Market Risk: {market_analysis.market_risk_score:.1f}/100 | "
            f"Sentiment: {market_analysis.overall_market_sentiment}"
        )

        # ── Step 3: Project Status Tracking ───────────────────
        logger.info("📊 Step 3/5 — Running Project Status Agent...")

        status_map, status_output = self.status_agent.track_all(projects)
        all_agent_outputs.append(status_output)

        logger.info(
            f"  Tracked {len(status_map)} projects | "
            f"Avg health: {status_output.output['avg_health_score']:.1f}/100"
        )

        # ── Step 4: Risk Scoring (one per project) ─────────────
        logger.info("🔢 Step 4/5 — Running Risk Scoring Agent...")

        # Create scoring agent with market risk score injected
        # This is dependency injection — the orchestrator controls
        # what data flows between agents
        scoring_agent = RiskScoringAgent(
            market_risk_score=market_analysis.market_risk_score
        )

        risk_reports: List[RiskReport] = []

        for project in projects:
            report, score_output = scoring_agent.analyze_project(project)
            risk_reports.append(report)
            all_agent_outputs.append(score_output)

        logger.info(
            f"  Scored {len(risk_reports)} projects successfully"
        )

        # ── Step 5: Portfolio Aggregation ─────────────────────
        logger.info("📈 Step 5/5 — Aggregating portfolio metrics...")

        portfolio_score = self._compute_portfolio_score(risk_reports)
        most_critical   = self._find_most_critical(risk_reports)
        high_risk_count = self._count_high_risk(risk_reports)

        # ── Build the final result object ──────────────────────
        total_elapsed = round(time.time() - pipeline_start, 2)

        result = SystemAnalysisResult(
            risk_reports=risk_reports,
            market_analysis=market_analysis,
            agent_outputs=all_agent_outputs,
            portfolio_risk_score=round(portfolio_score, 1),
            most_critical_project=most_critical,
            total_projects_analyzed=len(projects),
            high_risk_count=high_risk_count,
        )

        # ── Store in RAG (if pipeline is available) ────────────
        if self.rag_pipeline:
            logger.info("🧠 Storing results in ChromaDB for AI chat...")
            try:
                self.rag_pipeline.store_analysis(result)
                logger.info("  ✅ Results stored in vector database")
            except Exception as e:
                # Don't crash the whole analysis if RAG storage fails
                logger.warning(f"  ⚠️ RAG storage failed (non-fatal): {e}")

        # ── Log final summary ──────────────────────────────────
        logger.info("=" * 55)
        logger.info(f"✅ Analysis Complete in {total_elapsed}s")
        logger.info(f"   Portfolio Risk Score : {portfolio_score:.1f}/100")
        logger.info(f"   HIGH/CRITICAL Projects: {high_risk_count}/{len(projects)}")
        logger.info(f"   Most Critical        : {most_critical}")
        logger.info("=" * 55)

        return result

    # ── Private aggregation methods ───────────────────────────

    def _compute_portfolio_score(
        self,
        reports: List[RiskReport]
    ) -> float:
        """
        Computes a weighted portfolio-level risk score.

        Why weighted and not a simple average?
        A simple average hides critical emergencies.
        Example: 4 projects at score 20 + 1 at score 90
          Simple average = (80 + 90) / 5 = 34 → looks fine
          Weighted average = higher → reflects real danger

        Critical projects get 1.5× weight.
        High risk gets 1.2×.
        Medium stays at 1.0×.
        Low gets 0.8× (doesn't drag the score up).

        Args:
            reports: list of all RiskReport objects

        Returns:
            Weighted portfolio risk score (0-100)
        """
        if not reports:
            return 0.0

        # Weight multipliers per risk level
        level_weights = {
            RiskLevel.CRITICAL: 1.5,
            RiskLevel.HIGH:     1.2,
            RiskLevel.MEDIUM:   1.0,
            RiskLevel.LOW:      0.8,
        }

        # Weighted sum of scores
        weighted_sum = sum(
            report.overall_risk_score * level_weights.get(report.risk_level, 1.0)
            for report in reports
        )

        # Sum of weights (for proper normalization)
        weight_total = sum(
            level_weights.get(report.risk_level, 1.0)
            for report in reports
        )

        return weighted_sum / weight_total

    def _find_most_critical(
        self,
        reports: List[RiskReport]
    ) -> Optional[str]:
        """
        Finds the project with the highest risk score.

        Returns a human-readable string like:
        "PRJ-005 - Project Zenith (61/100 — HIGH)"

        Returns None if no reports exist.
        """
        if not reports:
            return None

        # max() with key= finds the report with highest score
        worst = max(reports, key=lambda r: r.overall_risk_score)

        return (
            f"{worst.project_code} - {worst.project_name} "
            f"({worst.overall_risk_score:.0f}/100 — {worst.risk_level.value})"
        )

    def _count_high_risk(self, reports: List[RiskReport]) -> int:
        """
        Counts projects that are HIGH or CRITICAL risk.
        Used for the dashboard KPI card "X projects need action".
        """
        return sum(
            1 for r in reports
            if r.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
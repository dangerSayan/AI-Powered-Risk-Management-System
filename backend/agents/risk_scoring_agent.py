"""
risk_scoring_agent.py — Risk Scoring Agent
==========================================
The core agent. Takes a project and produces a complete
RiskReport with a 0-100 risk score, evidence, and
mitigation strategies.

Input:  One Project object + market_risk_score (float)
Output: RiskReport object + AgentOutput metadata

Design principles:
- All SCORING is rule-based (consistent, explainable)
- All NARRATIVE is template-based (clear, professional)
- Market risk is injected from Market Analysis Agent
- Each risk category has clear evidence strings
- Mitigation strategies are actionable and specific
"""

import time
from datetime import date
from typing import List, Tuple, Dict
from loguru import logger

from backend.models.schemas import (
    Project,
    RiskFactor,
    RiskReport,
    RiskLevel,
    RiskCategory,
    MitigationStrategy,
    AgentOutput,
)
from config.llm_config import AppConfig


# ============================================================
# RISK WEIGHT MATRIX
# These weights determine how much each category contributes
# to the final overall risk score.
# Must sum to 1.0 (100%).
# ============================================================

RISK_WEIGHTS: Dict[RiskCategory, float] = {
    RiskCategory.SCHEDULE:    0.22,  # 22% — timeline is #1 concern
    RiskCategory.FINANCIAL:   0.20,  # 20% — money health is critical
    RiskCategory.RESOURCE:    0.20,  # 20% — team stability
    RiskCategory.TECHNICAL:   0.12,  # 12% — tech complexity
    RiskCategory.MARKET:      0.10,  # 10% — external conditions
    RiskCategory.OPERATIONAL: 0.10,  # 10% — client relationship
    RiskCategory.COMPLIANCE:  0.06,  # 6%  — contract/legal
}


class RiskScoringAgent:
    """
    Calculates a comprehensive risk score for one project.

    Takes the project's raw data and the market risk score
    from the Market Analysis Agent, then:
    1. Scores each of the 7 risk categories (0-100 each)
    2. Applies weights to get an overall score
    3. Generates mitigation strategies for top risks
    4. Writes an executive summary and key alerts

    market_risk_score is injected by the Risk Manager —
    the scoring agent doesn't call the market agent directly.
    This keeps agents decoupled from each other.
    """

    def __init__(self, market_risk_score: float = 50.0):
        """
        Args:
            market_risk_score: Score from Market Analysis Agent.
                               Default 50 = neutral market.
                               Passed in by Risk Manager after
                               Market Agent runs.
        """
        self.market_risk_score = market_risk_score
        self.agent_name = "Risk Scoring Agent"
        logger.info(
            f"🔢 {self.agent_name} initialized | "
            f"Market risk baseline: {market_risk_score:.1f}"
        )

    # ── Main public method ────────────────────────────────────

    def analyze_project(
        self,
        project: Project
    ) -> Tuple[RiskReport, AgentOutput]:
        """
        Full risk analysis pipeline for a single project.

        Steps:
        1. Calculate individual risk factors for each category
        2. Compute weighted category scores
        3. Compute final overall score
        4. Determine risk level (LOW/MEDIUM/HIGH/CRITICAL)
        5. Generate mitigation strategies
        6. Write executive summary + key alerts
        7. Return complete RiskReport

        Args:
            project: Project object to analyze

        Returns:
            Tuple of (RiskReport, AgentOutput)
        """
        start_time = time.time()
        logger.info(f"🔍 Scoring: {project.code} — {project.name}")

        # Step 1 — Calculate all risk factors
        risk_factors = self._calculate_all_risk_factors(project)

        # Step 2 — Build category score dict
        # Maps RiskCategory → score (0-100)
        category_scores: Dict[RiskCategory, float] = {
            factor.category: factor.impact_score
            for factor in risk_factors
        }

        # Step 3 — Apply weights to get overall score
        overall_score = self._compute_weighted_score(category_scores)

        # Step 4 — Convert score to risk level
        risk_level_str = AppConfig.get_risk_level(overall_score)
        risk_level = RiskLevel(risk_level_str)

        # Step 5 — Generate mitigation strategies
        # Only generate for top 5 highest-scoring risk categories
        mitigations = self._generate_mitigations(
            project,
            risk_factors,
            overall_score
        )

        # Step 6 — Write human-readable narrative
        executive_summary = self._write_executive_summary(
            project, overall_score, risk_level, risk_factors
        )
        detailed_analysis = self._write_detailed_analysis(
            project, risk_factors, category_scores
        )
        key_alerts = self._extract_key_alerts(
            project, risk_factors, overall_score
        )

        elapsed = round(time.time() - start_time, 2)

        # Convert category scores dict to use string keys for JSON
        # RiskCategory.FINANCIAL → "FINANCIAL"
        category_scores_str = {
            cat.value: round(score, 1)
            for cat, score in category_scores.items()
        }

        # Build the complete RiskReport
        report = RiskReport(
            project_id=project.id,
            project_name=project.name,
            project_code=project.code,
            overall_risk_score=round(overall_score, 1),
            risk_level=risk_level,
            risk_factors=risk_factors,
            category_scores=category_scores_str,
            mitigation_strategies=mitigations,
            executive_summary=executive_summary,
            detailed_analysis=detailed_analysis,
            key_alerts=key_alerts,
        )

        agent_output = AgentOutput(
            agent_name=self.agent_name,
            task_completed=f"Risk scored for {project.code}",
            output={
                "project_code":  project.code,
                "risk_score":    overall_score,
                "risk_level":    risk_level.value,
                "alerts_count":  len(key_alerts),
            },
            confidence=0.88,
            processing_time_seconds=elapsed
        )

        logger.info(
            f"  ✅ {project.code} → Score: {overall_score:.1f}/100 "
            f"({risk_level.value}) | Alerts: {len(key_alerts)} | "
            f"Time: {elapsed}s"
        )

        return report, agent_output

    # ============================================================
    # SECTION A — RISK FACTOR CALCULATIONS
    # One method per category. Each returns:
    #   (score: float, evidence: List[str])
    # Score is 0-100. Evidence explains exactly why.
    # ============================================================

    def _calculate_all_risk_factors(
        self,
        project: Project
    ) -> List[RiskFactor]:
        """
        Runs all 7 category scorers and returns a list of RiskFactors.
        """
        factors = []

        # ── 1. Schedule Risk ───────────────────────────────────
        schedule_score, schedule_evidence = self._score_schedule(project)
        factors.append(RiskFactor(
            category=RiskCategory.SCHEDULE,
            description="Schedule delay and delivery velocity analysis",
            impact_score=schedule_score,
            # probability increases as score increases
            probability=min(0.95, schedule_score / 100 + 0.25),
            weight=RISK_WEIGHTS[RiskCategory.SCHEDULE],
            evidence=schedule_evidence
        ))

        # ── 2. Financial Risk ──────────────────────────────────
        financial_score, financial_evidence = self._score_financial(project)
        factors.append(RiskFactor(
            category=RiskCategory.FINANCIAL,
            description="Budget utilization, overrun, and payment health",
            impact_score=financial_score,
            probability=min(0.95, financial_score / 100 + 0.20),
            weight=RISK_WEIGHTS[RiskCategory.FINANCIAL],
            evidence=financial_evidence
        ))

        # ── 3. Resource Risk ───────────────────────────────────
        resource_score, resource_evidence = self._score_resource(project)
        factors.append(RiskFactor(
            category=RiskCategory.RESOURCE,
            description="Team stability, attrition, and knowledge risk",
            impact_score=resource_score,
            probability=min(0.95, resource_score / 100 + 0.15),
            weight=RISK_WEIGHTS[RiskCategory.RESOURCE],
            evidence=resource_evidence
        ))

        # ── 4. Technical Risk ──────────────────────────────────
        tech_score, tech_evidence = self._score_technical(project)
        factors.append(RiskFactor(
            category=RiskCategory.TECHNICAL,
            description="Technical complexity and dependency risks",
            impact_score=tech_score,
            probability=min(0.90, tech_score / 100 + 0.15),
            weight=RISK_WEIGHTS[RiskCategory.TECHNICAL],
            evidence=tech_evidence
        ))

        # ── 5. Market Risk ─────────────────────────────────────
        # Direct injection of Market Agent score — no recalculation
        factors.append(RiskFactor(
            category=RiskCategory.MARKET,
            description="External market, economic, and industry conditions",
            impact_score=self.market_risk_score,
            probability=0.65,  # market risk is always somewhat probable
            weight=RISK_WEIGHTS[RiskCategory.MARKET],
            evidence=[
                f"Market risk score from Market Analysis Agent: "
                f"{self.market_risk_score:.0f}/100",
                "Reflects NASSCOM slowdown, BFSI budget cuts, "
                "and talent attrition trends"
            ]
        ))

        # ── 6. Operational Risk ────────────────────────────────
        ops_score, ops_evidence = self._score_operational(project)
        factors.append(RiskFactor(
            category=RiskCategory.OPERATIONAL,
            description="Client relationship and communication health",
            impact_score=ops_score,
            probability=min(0.90, ops_score / 100 + 0.10),
            weight=RISK_WEIGHTS[RiskCategory.OPERATIONAL],
            evidence=ops_evidence
        ))

        # ── 7. Compliance Risk ─────────────────────────────────
        comp_score, comp_evidence = self._score_compliance(project)
        factors.append(RiskFactor(
            category=RiskCategory.COMPLIANCE,
            description="Contractual obligations and SLA breach risk",
            impact_score=comp_score,
            probability=0.30,
            weight=RISK_WEIGHTS[RiskCategory.COMPLIANCE],
            evidence=comp_evidence
        ))

        return factors

    def _score_schedule(
        self,
        project: Project
    ) -> Tuple[float, List[str]]:
        """
        Scores schedule risk based on:
        - Days delayed beyond plan
        - Gap between time consumed and progress made
        - Emergency: very close to deadline with low completion
        """
        score = 0.0
        evidence = []
        today = date.today()

        # Calculate timeline percentages
        total_days = max(
            (project.planned_end_date - project.start_date).days, 1
        )
        elapsed_days = max((today - project.start_date).days, 0)
        time_consumed_pct = (elapsed_days / total_days) * 100
        progress_gap = time_consumed_pct - project.current_progress_percent

        # Rule 1: Direct schedule delay
        if project.schedule_delay_days > 0:
            delay_points = min(50.0, project.schedule_delay_days * 1.2)
            score += delay_points
            evidence.append(
                f"Project is {project.schedule_delay_days} days behind "
                f"schedule (+{delay_points:.0f} pts)"
            )

        # Rule 2: Progress-velocity gap
        if progress_gap > 15:
            gap_points = min(30.0, progress_gap * 0.8)
            score += gap_points
            evidence.append(
                f"{time_consumed_pct:.0f}% of timeline consumed but only "
                f"{project.current_progress_percent:.0f}% complete — "
                f"{progress_gap:.0f}% gap (+{gap_points:.0f} pts)"
            )

        # Rule 3: Emergency — deadline close, work not done
        days_remaining = (project.planned_end_date - today).days
        if days_remaining < 30 and project.current_progress_percent < 80:
            score += 25
            evidence.append(
                f"CRITICAL: {days_remaining} days remaining but only "
                f"{project.current_progress_percent:.0f}% complete (+25 pts)"
            )

        # If no delay issues, record this positively
        if score == 0:
            evidence.append(
                f"Project is on schedule — "
                f"{project.current_progress_percent:.0f}% complete"
            )

        return min(100.0, score), evidence

    def _score_financial(
        self,
        project: Project
    ) -> Tuple[float, List[str]]:
        """
        Scores financial risk based on:
        - Client payment delay
        - Budget overrun (projected vs planned)
        - Budget exhaustion ahead of completion
        """
        score = 0.0
        evidence = []
        fin = project.financials

        # Rule 1: Payment delay
        if fin.payment_delay_days > 0:
            pay_points = min(40.0, fin.payment_delay_days * 0.65)
            score += pay_points
            evidence.append(
                f"Client payment delayed by {fin.payment_delay_days} days | "
                f"₹{fin.payment_amount_pending:,.0f} pending "
                f"(+{pay_points:.0f} pts)"
            )

        # Rule 2: Budget overrun
        if fin.is_over_budget:
            overrun_pct = (
                (fin.projected_total - fin.total_budget)
                / fin.total_budget * 100
            )
            over_points = min(35.0, overrun_pct * 1.5)
            score += over_points
            evidence.append(
                f"Projected {overrun_pct:.1f}% over budget | "
                f"₹{fin.projected_total - fin.total_budget:,.0f} overrun "
                f"(+{over_points:.0f} pts)"
            )

        # Rule 3: Burning money faster than delivering
        utilization = fin.budget_utilization
        if utilization > 85 and project.current_progress_percent < 70:
            score += 20
            evidence.append(
                f"{utilization:.0f}% of budget used but only "
                f"{project.current_progress_percent:.0f}% of work complete "
                f"(+20 pts)"
            )

        if score == 0:
            evidence.append(
                f"Financial health stable — budget utilization aligned "
                f"with project progress"
            )

        return min(100.0, score), evidence

    def _score_resource(
        self,
        project: Project
    ) -> Tuple[float, List[str]]:
        """
        Scores resource risk based on:
        - Number of recent resignations
        - Seniority of resigned members (senior loss = more damage)
        - Overall team attrition risk
        """
        score = 0.0
        evidence = []

        # Rule 1: Recent resignations
        if project.resignations_last_30_days > 0:
            resign_points = min(50.0, project.resignations_last_30_days * 18)
            score += resign_points
            active_count = sum(1 for m in project.team if m.is_active)
            evidence.append(
                f"{project.resignations_last_30_days} resignation(s) in "
                f"last 30 days | {active_count}/{project.team_size_planned} "
                f"team members active (+{resign_points:.0f} pts)"
            )

        # Rule 2: Senior/Lead resignations hurt much more
        # These people carry critical knowledge
        senior_resigned = sum(
            1 for m in project.team
            if not m.is_active and m.seniority in ["Senior", "Lead"]
        )
        if senior_resigned > 0:
            senior_points = senior_resigned * 15
            score += senior_points
            evidence.append(
                f"{senior_resigned} Senior/Lead resource(s) lost — "
                f"critical knowledge transfer risk "
                f"(+{senior_points} pts)"
            )

        # Rule 3: High ongoing attrition risk across active team
        active_members = [m for m in project.team if m.is_active]
        if active_members:
            avg_resign_risk = (
                sum(m.resignation_risk for m in active_members)
                / len(active_members)
            )
            if avg_resign_risk > 0.40:
                score += 10
                evidence.append(
                    f"Active team shows elevated flight risk "
                    f"(avg {avg_resign_risk:.0%} resignation probability) "
                    f"(+10 pts)"
                )

        if score == 0:
            evidence.append(
                f"Team stable — all {project.team_size_planned} "
                f"planned resources active"
            )

        return min(100.0, score), evidence

    def _score_technical(
        self,
        project: Project
    ) -> Tuple[float, List[str]]:
        """
        Scores technical risk based on:
        - Project type complexity (Cloud/AI/ERP = harder)
        - Number of external dependencies (more = riskier)
        - Size of tech stack (more technologies = harder to manage)
        """
        # Every project has some baseline technical risk
        score = 20.0
        evidence = [
            f"Project type: {project.project_type.value} "
            f"(baseline technical complexity — 20 pts)"
        ]

        # Rule 1: High-complexity project types
        complex_types = [
            "Cloud Migration",
            "AI/ML",
            "ERP Implementation"
        ]
        if project.project_type.value in complex_types:
            score += 20
            evidence.append(
                f"High-complexity project type: {project.project_type.value} "
                f"— elevated integration and delivery risk (+20 pts)"
            )

        # Rule 2: External dependencies
        dep_count = len(project.external_dependencies)
        if dep_count >= 2:
            dep_points = dep_count * 5
            score += dep_points
            deps = ", ".join(project.external_dependencies)
            evidence.append(
                f"{dep_count} external dependencies ({deps}) — "
                f"each adds integration risk (+{dep_points} pts)"
            )

        # Rule 3: Large tech stack
        tech_count = len(project.tech_stack)
        if tech_count >= 5:
            score += 10
            evidence.append(
                f"Large tech stack ({tech_count} technologies) — "
                f"increases maintenance and skill coverage risk (+10 pts)"
            )

        return min(100.0, score), evidence

    def _score_operational(
        self,
        project: Project
    ) -> Tuple[float, List[str]]:
        """
        Scores operational risk based on:
        - Days since last client communication
        - Client satisfaction score
        """
        score = 0.0
        evidence = []

        # Rule 1: Communication gap
        if project.last_client_communication_days > 7:
            comm_points = min(40.0, project.last_client_communication_days * 2)
            score += comm_points
            evidence.append(
                f"No client communication for "
                f"{project.last_client_communication_days} days — "
                f"relationship risk (+{comm_points:.0f} pts)"
            )

        # Rule 2: Low satisfaction score
        # Threshold is 7/10 — below this is concerning
        if project.client_satisfaction_score < 7.0:
            sat_gap = 7.0 - project.client_satisfaction_score
            sat_points = sat_gap * 8
            score += sat_points
            evidence.append(
                f"Client satisfaction score: "
                f"{project.client_satisfaction_score}/10 — "
                f"below acceptable threshold of 7.0 "
                f"(+{sat_points:.0f} pts)"
            )

        if score == 0:
            evidence.append(
                f"Client relationship healthy — "
                f"satisfaction {project.client_satisfaction_score}/10, "
                f"recent communication maintained"
            )

        return min(100.0, score), evidence

    def _score_compliance(
        self,
        project: Project
    ) -> Tuple[float, List[str]]:
        """
        Scores compliance risk based on:
        - Payment delay breaching SLA thresholds
        - Schedule delay potentially triggering penalty clauses
        """
        # Baseline: every contract has some compliance exposure
        score = 15.0
        evidence = ["Baseline contractual compliance risk (15 pts)"]

        # Rule 1: Prolonged payment delay may breach SLA
        if project.financials.payment_delay_days > 60:
            score += 20
            evidence.append(
                f"Payment delay of {project.financials.payment_delay_days} "
                f"days may breach contractual SLA thresholds (+20 pts)"
            )

        # Rule 2: Major schedule overrun may trigger penalty clauses
        if project.schedule_delay_days > 45:
            score += 15
            evidence.append(
                f"Schedule overrun of {project.schedule_delay_days} days "
                f"may trigger contract penalty clauses (+15 pts)"
            )

        return min(100.0, score), evidence

    # ============================================================
    # SECTION B — SCORE AGGREGATION
    # ============================================================

    def _compute_weighted_score(
        self,
        category_scores: Dict[RiskCategory, float]
    ) -> float:
        """
        Applies weights to category scores to produce one final score.

        Formula:
          overall = Σ (category_score × category_weight)

        Example:
          Schedule  80 × 0.22 = 17.6
          Financial 70 × 0.20 = 14.0
          Resource  60 × 0.20 = 12.0
          Technical 50 × 0.12 =  6.0
          Market    95 × 0.10 =  9.5
          Operational 40 × 0.10 = 4.0
          Compliance 35 × 0.06 = 2.1
                                ─────
          Overall score        = 65.2 → HIGH risk
        """
        total = 0.0
        for category, score in category_scores.items():
            weight = RISK_WEIGHTS.get(category, 0.0)
            total += score * weight
        return min(100.0, total)

    # ============================================================
    # SECTION C — MITIGATION STRATEGIES
    # ============================================================

    def _generate_mitigations(
        self,
        project: Project,
        risk_factors: List[RiskFactor],
        overall_score: float
    ) -> List[MitigationStrategy]:
        """
        Generates one mitigation strategy per top-risk category.

        We sort risk factors by score (highest first) and generate
        mitigations for the top 5. This ensures the most urgent
        risks always get an action plan.
        """
        # Sort by impact score, highest first
        sorted_factors = sorted(
            risk_factors,
            key=lambda f: f.impact_score,
            reverse=True
        )

        strategies = []
        for priority, factor in enumerate(sorted_factors[:5], start=1):
            mitigation = self._get_mitigation(
                factor.category, project, priority
            )
            if mitigation:
                strategies.append(mitigation)

        return strategies

    def _get_mitigation(
        self,
        category: RiskCategory,
        project: Project,
        priority: int
    ) -> MitigationStrategy:
        """
        Returns a specific mitigation strategy for a risk category.

        Each strategy has:
        - A specific, actionable description
        - A named owner (by role, not person)
        - A clear timeline
        - An estimated risk reduction in score points
        """
        fin = project.financials

        mitigations = {
            RiskCategory.SCHEDULE: MitigationStrategy(
                priority=priority,
                action=(
                    f"Initiate schedule recovery plan immediately — "
                    f"reduce sprint scope by 20%, add parallel workstreams, "
                    f"and re-baseline project timeline with stakeholder sign-off"
                ),
                owner="Project Manager",
                timeline="Immediate — within 48 hours",
                estimated_risk_reduction=15.0,
                effort="High"
            ),
            RiskCategory.FINANCIAL: MitigationStrategy(
                priority=priority,
                action=(
                    f"Escalate payment delay to leadership — send formal "
                    f"payment notice for ₹{fin.payment_amount_pending:,.0f} "
                    f"pending amount and negotiate partial release within 7 days"
                ),
                owner="Finance Lead + Account Manager",
                timeline="Within 1 week",
                estimated_risk_reduction=18.0,
                effort="Medium"
            ),
            RiskCategory.RESOURCE: MitigationStrategy(
                priority=priority,
                action=(
                    f"Mobilize {project.resignations_last_30_days} replacement "
                    f"resource(s) from bench or contract pool immediately — "
                    f"initiate knowledge transfer sessions within 5 business days"
                ),
                owner="Resource Manager + HR",
                timeline="Immediate — within 72 hours",
                estimated_risk_reduction=20.0,
                effort="High"
            ),
            RiskCategory.TECHNICAL: MitigationStrategy(
                priority=priority,
                action=(
                    "Conduct technical risk workshop with solution architect — "
                    "identify top 3 integration points, create proof-of-concept "
                    "for highest-risk components, document fallback approaches"
                ),
                owner="Tech Lead + Solution Architect",
                timeline="Within 1 week",
                estimated_risk_reduction=10.0,
                effort="Medium"
            ),
            RiskCategory.MARKET: MitigationStrategy(
                priority=priority,
                action=(
                    "Brief client on current market conditions — present "
                    "contingency options including 10-15% scope reduction levers "
                    "and phased delivery model if client budget freeze occurs"
                ),
                owner="Account Manager + Delivery Head",
                timeline="Within 2 weeks",
                estimated_risk_reduction=8.0,
                effort="Low"
            ),
            RiskCategory.OPERATIONAL: MitigationStrategy(
                priority=priority,
                action=(
                    f"Schedule executive-level check-in with client within 48 hours — "
                    f"present live project dashboard, address satisfaction gap, "
                    f"and establish weekly steering committee cadence"
                ),
                owner="Delivery Manager + Account Manager",
                timeline="Within 48 hours",
                estimated_risk_reduction=12.0,
                effort="Low"
            ),
            RiskCategory.COMPLIANCE: MitigationStrategy(
                priority=priority,
                action=(
                    "Legal team to review contract SLA clauses — "
                    "prepare variance request documentation for schedule overrun, "
                    "and check force majeure applicability for payment delays"
                ),
                owner="Legal Team + PMO",
                timeline="Within 1 week",
                estimated_risk_reduction=5.0,
                effort="Medium"
            ),
        }

        return mitigations.get(category)

    # ============================================================
    # SECTION D — NARRATIVE GENERATION
    # Rule-based templates for consistent, professional text.
    # In production with HuggingFace token, these would be
    # enhanced by Mistral-7B for more natural language.
    # ============================================================

    def _write_executive_summary(
        self,
        project: Project,
        score: float,
        level: RiskLevel,
        risk_factors: List[RiskFactor]
    ) -> str:
        """
        Writes a 2-3 sentence executive summary for the report.
        Identifies top 3 risk drivers by name.
        """
        # Get top 3 risk categories by score
        top_3 = sorted(risk_factors, key=lambda f: f.impact_score, reverse=True)[:3]
        top_categories = ", ".join(
            f.category.value.lower() for f in top_3
        )

        level_phrases = {
            RiskLevel.LOW:      "within acceptable parameters and requires standard monitoring",
            RiskLevel.MEDIUM:   "showing moderate risk requiring proactive management attention",
            RiskLevel.HIGH:     "at HIGH risk and requires immediate management intervention",
            RiskLevel.CRITICAL: "in CRITICAL state and requires emergency executive action",
        }

        return (
            f"{project.name} ({project.code}) is currently "
            f"{level_phrases[level]}, with an overall risk score of "
            f"{score:.0f}/100 ({level.value}). "
            f"Primary risk drivers are {top_categories}. "
            f"The project is {project.current_progress_percent:.0f}% complete "
            f"against a planned end date of "
            f"{project.planned_end_date.strftime('%d %b %Y')}. "
            f"{'Immediate executive escalation is recommended.' if score >= 75 else 'Continued monitoring with the mitigation actions below is advised.'}"
        )

    def _write_detailed_analysis(
        self,
        project: Project,
        risk_factors: List[RiskFactor],
        category_scores: Dict[RiskCategory, float]
    ) -> str:
        """
        Writes a detailed markdown analysis for the Reports page.
        Lists each risk category with its evidence points.
        """
        lines = [f"## Detailed Risk Analysis — {project.name}\n"]

        # Sort by score highest first for readability
        sorted_factors = sorted(
            risk_factors,
            key=lambda f: f.impact_score,
            reverse=True
        )

        for factor in sorted_factors:
            lines.append(
                f"### {factor.category.value} Risk "
                f"({factor.impact_score:.0f}/100)"
            )
            for ev in factor.evidence:
                lines.append(f"- {ev}")
            lines.append("")  # blank line between sections

        return "\n".join(lines)

    def _extract_key_alerts(
        self,
        project: Project,
        risk_factors: List[RiskFactor],
        overall_score: float
    ) -> List[str]:
        """
        Extracts urgent, specific alert messages.
        These appear in the dashboard alert panel and
        are the first thing a manager sees.
        """
        alerts = []

        # Overall score alert
        if overall_score >= 75:
            alerts.append(
                f"🚨 CRITICAL: {project.name} has exceeded critical "
                f"risk threshold with score {overall_score:.0f}/100"
            )
        elif overall_score >= 55:
            alerts.append(
                f"⚠️ HIGH RISK: {project.name} requires immediate "
                f"management attention (score: {overall_score:.0f}/100)"
            )

        # Specific condition alerts
        if project.resignations_last_30_days >= 2:
            alerts.append(
                f"👥 {project.resignations_last_30_days} team member(s) "
                f"resigned in the last 30 days — knowledge loss risk"
            )

        if project.financials.payment_delay_days > 45:
            alerts.append(
                f"💰 Client payment {project.financials.payment_delay_days} "
                f"days overdue — ₹{project.financials.payment_amount_pending:,.0f} "
                f"pending — escalation required"
            )

        if project.schedule_delay_days > 30:
            alerts.append(
                f"📅 Project {project.schedule_delay_days} days behind "
                f"schedule — timeline re-baseline needed"
            )

        if project.client_satisfaction_score < 6.0:
            alerts.append(
                f"😟 Client satisfaction critically low at "
                f"{project.client_satisfaction_score}/10 — "
                f"immediate relationship intervention needed"
            )

        if project.last_client_communication_days > 14:
            alerts.append(
                f"📵 No client contact for "
                f"{project.last_client_communication_days} days — "
                f"relationship at risk"
            )

        if project.financials.is_over_budget:
            overrun = (
                project.financials.projected_total
                - project.financials.total_budget
            )
            alerts.append(
                f"💸 Budget overrun projected: "
                f"₹{overrun:,.0f} above approved budget"
            )

        return alerts
"""
project_status_agent.py — Project Status Tracking Agent
========================================================
Monitors internal health of each project across 4 dimensions:
  1. Schedule Health  — is progress matching timeline?
  2. Budget Health    — is spending matching delivery?
  3. Resource Health  — is the team stable?
  4. Client Health    — is the client relationship healthy?

Input:  List of Project objects
Output: Dict mapping project code → health KPIs + AgentOutput

Key distinction from Risk Scoring Agent:
  This agent MEASURES (what is happening?)
  Risk Scoring Agent JUDGES (how bad is it?)
"""

import time
from datetime import date
from typing import List, Tuple, Dict
from loguru import logger

from backend.models.schemas import Project, AgentOutput


# ============================================================
# HEALTH SCORE WEIGHTS
# How much each dimension contributes to overall health score.
# Schedule and resources matter most in IT project delivery.
# ============================================================

HEALTH_WEIGHTS = {
    "schedule":  0.30,   # 30% — timeline is the #1 concern
    "budget":    0.25,   # 25% — money health is critical
    "resource":  0.25,   # 25% — team stability drives everything
    "client":    0.20,   # 20% — relationship health matters
}


class ProjectStatusAgent:
    """
    Tracks the internal health of all projects.

    For each project, computes:
    - A health score for each of the 4 dimensions
    - An overall health score (0-100, higher = healthier)
    - Key KPI values that the Risk Scoring Agent uses

    Note: Health score and Risk score move in OPPOSITE directions.
    Health 80 = project is doing well
    Risk   80 = project is in serious danger
    """

    def __init__(self):
        self.agent_name = "Project Status Tracking Agent"
        logger.info(f"📊 {self.agent_name} initialized")

    # ── Main public method ────────────────────────────────────

    def track_all(
        self,
        projects: List[Project]
    ) -> Tuple[Dict[str, dict], AgentOutput]:
        """
        Tracks status for all projects at once.

        Why process all at once instead of one at a time?
        Because the Risk Manager calls this once to get a
        complete picture. It also lets us compute portfolio-level
        comparisons in the future (e.g. "which project is most
        behind relative to others?")

        Args:
            projects: list of Project objects

        Returns:
            Tuple of:
              - Dict mapping "PRJ-001" → {kpi dict}
              - AgentOutput with run metadata
        """
        start_time = time.time()
        logger.info(f"📋 Tracking status for {len(projects)} projects...")

        status_map = {}   # will hold KPIs for each project
        critical_projects = []  # projects with health score < 50

        for project in projects:
            # Compute KPIs for this project
            kpis = self._compute_kpis(project)
            # Store under the project code as key
            status_map[project.code] = kpis

            # Flag critically unhealthy projects
            if kpis["overall_health_score"] < 50:
                critical_projects.append(
                    f"{project.code} (health: {kpis['overall_health_score']:.0f}/100)"
                )

            logger.info(
                f"  {project.code} | Health: {kpis['overall_health_score']:.0f}/100 | "
                f"Schedule: {kpis['schedule_health']:.0f} | "
                f"Budget: {kpis['budget_health']:.0f} | "
                f"Resource: {kpis['resource_health']:.0f} | "
                f"Client: {kpis['client_health']:.0f}"
            )

        elapsed = round(time.time() - start_time, 2)

        agent_output = AgentOutput(
            agent_name=self.agent_name,
            task_completed=f"Tracked status for {len(projects)} projects",
            output={
                "projects_tracked": len(projects),
                "critical_projects": critical_projects,
                "avg_health_score": round(
                    sum(v["overall_health_score"] for v in status_map.values())
                    / len(status_map), 1
                ) if status_map else 0,
            },
            confidence=0.95,   # rule-based = high confidence
            processing_time_seconds=elapsed
        )

        logger.info(
            f"✅ Status tracking complete | "
            f"{len(critical_projects)} critical projects | "
            f"Time: {elapsed}s"
        )

        return status_map, agent_output

    # ── Private KPI calculation methods ──────────────────────

    def _compute_kpis(self, project: Project) -> dict:
        """
        Computes all health KPIs for one project.

        Returns a plain dict (not a Pydantic object) because
        these KPIs are intermediate data — used by the Risk
        Scoring Agent but not directly stored in the database
        or shown in the UI as structured objects.

        Args:
            project: Project object

        Returns:
            Dict with all KPI values
        """
        today = date.today()

        # ── Timeline calculations ──────────────────────────────

        # Total project duration in days
        total_days = max(
            (project.planned_end_date - project.start_date).days,
            1  # avoid division by zero
        )

        # How many days have passed since project started
        # max(..., 0) ensures we don't get negative days
        elapsed_days = max(
            (today - project.start_date).days,
            0
        )

        # How many days until planned end date
        # Can be negative if project is past its deadline
        remaining_days = (project.planned_end_date - today).days

        # What percentage of the timeline has been consumed
        time_consumed_pct = (elapsed_days / total_days) * 100

        # ── 1. Schedule Health ─────────────────────────────────
        schedule_health, velocity = self._compute_schedule_health(
            project.current_progress_percent,
            time_consumed_pct
        )

        # ── 2. Budget Health ───────────────────────────────────
        budget_health = self._compute_budget_health(
            project.financials.budget_utilization,
            project.current_progress_percent
        )

        # ── 3. Resource Health ─────────────────────────────────
        resource_health = self._compute_resource_health(project)

        # ── 4. Client Health ───────────────────────────────────
        client_health = self._compute_client_health(
            project.last_client_communication_days,
            project.client_satisfaction_score
        )

        # ── Overall Health Score ───────────────────────────────
        overall_health = (
            schedule_health  * HEALTH_WEIGHTS["schedule"] +
            budget_health    * HEALTH_WEIGHTS["budget"] +
            resource_health  * HEALTH_WEIGHTS["resource"] +
            client_health    * HEALTH_WEIGHTS["client"]
        )

        # Return all KPIs as a dictionary
        # These values are used by:
        # 1. Risk Scoring Agent (for scoring input)
        # 2. Frontend Projects page (for KPI display)
        return {
            # Identity
            "project_code":  project.code,
            "project_name":  project.name,
            "project_status": project.status.value,

            # Overall
            "overall_health_score": round(overall_health, 1),

            # Schedule dimension
            "schedule_health":    round(schedule_health, 1),
            "schedule_velocity":  round(velocity, 2),
            "time_consumed_pct":  round(time_consumed_pct, 1),
            "progress_pct":       round(project.current_progress_percent, 1),
            "remaining_days":     remaining_days,
            "schedule_delay_days": project.schedule_delay_days,

            # Budget dimension
            "budget_health":      round(budget_health, 1),
            "budget_utilization": round(project.financials.budget_utilization, 1),
            "total_budget":       project.financials.total_budget,
            "spent_to_date":      project.financials.spent_to_date,
            "projected_total":    project.financials.projected_total,
            "is_over_budget":     project.financials.is_over_budget,

            # Resource dimension
            "resource_health":    round(resource_health, 1),
            "active_team_count":  sum(1 for m in project.team if m.is_active),
            "planned_team_size":  project.team_size_planned,
            "resignations_30d":   project.resignations_last_30_days,

            # Client dimension
            "client_health":             round(client_health, 1),
            "client_satisfaction_score": project.client_satisfaction_score,
            "days_since_client_contact": project.last_client_communication_days,

            # Payment
            "payment_delay_days":        project.financials.payment_delay_days,
            "payment_amount_pending":    project.financials.payment_amount_pending,
        }

    def _compute_schedule_health(
        self,
        progress_pct: float,
        time_consumed_pct: float
    ) -> Tuple[float, float]:
        """
        Measures if project progress matches timeline consumption.

        Velocity concept:
          velocity = progress / time_consumed
          1.0 = perfect (on track)
          0.7 = only doing 70% of expected work (behind)
          1.2 = doing 120% of expected work (ahead!)

        Args:
            progress_pct:      how complete the project is (0-100)
            time_consumed_pct: how much of the timeline is used (0-100)

        Returns:
            Tuple of (schedule_health 0-100, velocity float)
        """
        if time_consumed_pct <= 0:
            # Project just started — full health
            return 100.0, 1.0

        # Velocity: how efficiently are we progressing vs time?
        velocity = progress_pct / time_consumed_pct

        # Convert velocity to health score (capped at 100)
        # velocity 1.0 → health 100 (on track)
        # velocity 0.5 → health 50  (50% as fast as needed)
        # velocity 1.5 → health 100 (ahead, but capped at 100)
        schedule_health = min(100.0, velocity * 100)

        return schedule_health, velocity

    def _compute_budget_health(
        self,
        budget_utilization: float,
        progress_pct: float
    ) -> float:
        """
        Measures if spending aligns with delivery progress.

        Key insight: if you've spent 80% of budget but only
        done 50% of work, you're going to run out of money
        before finishing. That's a serious risk.

        Formula:
          gap = budget_utilization - progress_pct
          budget_health = 100 - max(0, gap)

          gap = 0  → perfect alignment → health = 100
          gap = 30 → spending 30% ahead of progress → health = 70
          gap < 0  → progress ahead of spending → health = 100

        Args:
            budget_utilization: % of budget spent (0-100)
            progress_pct:       % of work completed (0-100)

        Returns:
            budget_health score 0-100
        """
        # How much ahead of progress is the spending?
        spending_gap = budget_utilization - progress_pct

        # max(0, gap) means we only penalize overspending,
        # not under-spending (being under budget is fine)
        budget_health = 100.0 - max(0.0, spending_gap)

        # Clamp to valid range
        return max(0.0, min(100.0, budget_health))

    def _compute_resource_health(self, project: Project) -> float:
        """
        Measures team stability and completeness.

        Formula:
          active_members = count of team where is_active = True
          resource_health = (active_members / planned_size) × 100

        Example:
          10 planned, 2 resigned → 8 active
          resource_health = (8/10) × 100 = 80%

        Also applies a penalty for very recent resignations
        (resignations in last 30 days = knowledge loss risk)

        Args:
            project: Project object (needs team and team_size_planned)

        Returns:
            resource_health score 0-100
        """
        if project.team_size_planned <= 0:
            return 100.0

        # Count currently active members
        active_count = sum(1 for m in project.team if m.is_active)

        # Base health from team completeness
        base_health = (active_count / project.team_size_planned) * 100

        # Additional penalty for recent resignations
        # Each recent resignation = extra 5 point penalty
        # (beyond the base headcount reduction)
        # Why? Because recent resignations mean knowledge transfer
        # hasn't happened yet — the impact is worse than just headcount
        recent_penalty = project.resignations_last_30_days * 5

        resource_health = base_health - recent_penalty

        # Clamp to valid range
        return max(0.0, min(100.0, resource_health))

    def _compute_client_health(
        self,
        days_since_contact: int,
        satisfaction_score: float
    ) -> float:
        """
        Measures the health of the client relationship.

        Two inputs:
        1. Communication recency:
           0 days = talked today → full score
           20 days = 3 weeks no contact → 0 score (5 points per day)

        2. Satisfaction score:
           10/10 → 100 points
           5/10  → 50 points
           (just multiply by 10)

        Final client health = average of both.

        Args:
            days_since_contact: how many days since last client contact
            satisfaction_score: 0-10 client satisfaction rating

        Returns:
            client_health score 0-100
        """
        # Communication health: lose 5 points per day of silence
        # After 20 days with no contact → score hits 0
        comm_health = max(0.0, 100.0 - (days_since_contact * 5))

        # Satisfaction health: direct conversion from 0-10 to 0-100
        satisfaction_health = satisfaction_score * 10

        # Average the two for overall client health
        client_health = (comm_health + satisfaction_health) / 2

        return round(client_health, 1)


# ============================================================
# QUICK TEST
# python -c "..."
# ============================================================

if __name__ == "__main__":
    from backend.data.data_generator import load_projects

    print("\n🚀 Testing Project Status Agent...\n")

    agent = ProjectStatusAgent()
    projects = load_projects()
    status_map, output = agent.track_all(projects)

    print("\n📊 Project Health Scores:")
    print("-" * 70)
    for code, kpis in status_map.items():
        health = kpis["overall_health_score"]
        icon = "🔴" if health < 40 else "🟡" if health < 65 else "🟢"
        print(
            f"  {icon} {code} | Health: {health:>5.1f}/100 | "
            f"Schedule: {kpis['schedule_health']:>5.1f} | "
            f"Budget: {kpis['budget_health']:>5.1f} | "
            f"Resource: {kpis['resource_health']:>5.1f} | "
            f"Client: {kpis['client_health']:>5.1f}"
        )

    print(f"\n✅ Agent ran in {output.processing_time_seconds}s")
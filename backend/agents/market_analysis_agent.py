"""
market_analysis_agent.py — Market Analysis Agent
=================================================
Analyzes external market signals and produces a
MarketAnalysis object with an overall risk score.

Input:  List of raw market signal dicts
Output: MarketAnalysis object + AgentOutput metadata

This agent answers the question:
"How is the outside world affecting our IT projects?"
"""

import time
from datetime import datetime
from typing import List, Tuple
from loguru import logger

# Import the schemas we defined in Step 3
from backend.models.schemas import (
    MarketSignal,
    MarketAnalysis,
    AgentOutput
)
from backend.data.realtime_data import get_external_market_context


# ============================================================
# SCORING WEIGHTS
# Defined at module level (outside the class) because they're
# constants — they never change at runtime.
# ============================================================

# How much each sentiment type contributes to risk score
# Negative news increases risk, positive news reduces it slightly
SENTIMENT_WEIGHTS = {
    "negative": 1.0,   # bad news = full risk contribution
    "neutral":  0.0,   # neutral news = no risk contribution
    "positive": -0.5,  # good news = slight risk reduction
}

# Economic indicators (RBI, GDP) affect projects more than general news
# So we multiply their scores by a higher number
SIGNAL_TYPE_MULTIPLIERS = {
    "economic_indicator": 1.3,  # RBI decisions, GDP data — high impact
    "industry_trend":     1.2,  # NASSCOM reports — significant
    "news":               1.0,  # Regular news articles — base impact
}


# ============================================================
# MARKET ANALYSIS AGENT CLASS
# ============================================================

class MarketAnalysisAgent:
    """
    Analyzes market signals and computes market risk score.

    Design decisions:
    - Scoring is rule-based (consistent, explainable)
    - Sentiment classification is in the data (not AI-driven)
    - In production: signals come from NewsAPI, Alpha Vantage
    - For demo: signals come from data_generator.py
    """

    def __init__(self):
        self.agent_name = "Market Analysis Agent"
        logger.info(f"📈 {self.agent_name} initialized")

    # ── Main public method ────────────────────────────────────

    def analyze(self, raw_signals: list) -> Tuple[MarketAnalysis, AgentOutput]:
        """
        Main entry point. Runs the full analysis pipeline.

        Tuple[MarketAnalysis, AgentOutput] means this function
        returns TWO things at once — the analysis result AND
        metadata about how the agent ran.

        Why return AgentOutput too?
        The Risk Manager collects AgentOutputs from all agents
        and stores them in SystemAnalysisResult. This lets the
        UI show "how did each agent perform?" — useful for
        debugging and for impressing in presentations.

        Args:
            raw_signals: list of dicts from data_generator.py

        Returns:
            Tuple of (MarketAnalysis, AgentOutput)
        """
        # Record start time for performance tracking
        start_time = time.time()
        logger.info(f"🌐 Analyzing {len(raw_signals)} market signals...")

        # ── Step 1: Parse raw dicts into MarketSignal objects ──
        # raw_signals are plain Python dicts from JSON
        # We convert them to proper Pydantic objects for type safety
        signals = [self._parse_signal(s) for s in raw_signals]

        # ── Step 2: Score each signal individually ─────────────
        signal_scores = [self._score_signal(s) for s in signals]

        # ── Step 3: Compute overall market risk score ──────────
        market_risk_score = self._compute_market_risk(signals, signal_scores)
        # ── Inject real external market context ─────────────────────
        try:
            ctx = get_external_market_context()

            # GDP impact
            gdp = ctx.get("gdp_growth")
            if gdp:
                if gdp < 5:
                    market_risk_score += 10
                elif gdp > 7:
                    market_risk_score -= 5

            # Inflation impact
            inflation = ctx.get("inflation")
            if inflation and inflation > 6:
                market_risk_score += 8

            # USD/INR impact
            usd_inr = ctx.get("usd_inr")
            if usd_inr and usd_inr > 86:
                market_risk_score += 6

            # News sentiment impact
            neg_pct = ctx.get("news_negative_pct")
            if neg_pct:
                if neg_pct > 40:
                    market_risk_score += 10
                elif neg_pct < 20:
                    market_risk_score -= 5

            # Clamp score again
            market_risk_score = min(100, max(10, market_risk_score))

            logger.info(f"🌍 External market context applied: {ctx}")

        except Exception as e:
            logger.warning(f"External market context unavailable: {e}")

        # ── Step 4: Determine overall sentiment ────────────────
        negative_count = sum(1 for s in signals if s.sentiment == "negative")
        positive_count = sum(1 for s in signals if s.sentiment == "positive")
        overall_sentiment = self._determine_sentiment(
            negative_count, positive_count, len(signals)
        )

        # ── Step 5: Extract key trend statements ───────────────
        key_trends = self._extract_trends(signals)

        # ── Step 6: Write IT sector outlook paragraph ──────────
        it_outlook = self._build_it_outlook(market_risk_score, signals)

        # Calculate how long this agent took
        elapsed = round(time.time() - start_time, 2)

        # ── Build the MarketAnalysis output object ─────────────
        analysis = MarketAnalysis(
            overall_market_sentiment=overall_sentiment,
            market_risk_score=round(market_risk_score, 1),
            signals=signals,
            key_trends=key_trends,
            it_sector_outlook=it_outlook,
        )

        # ── Build the AgentOutput metadata object ──────────────
        agent_output = AgentOutput(
            agent_name=self.agent_name,
            task_completed=f"Analyzed {len(signals)} market signals",
            output={
                "market_risk_score":  market_risk_score,
                "sentiment":          overall_sentiment,
                "signals_analyzed":   len(signals),
                "negative_signals":   negative_count,
                "positive_signals":   positive_count,
            },
            confidence=0.82,
            processing_time_seconds=elapsed
        )

        logger.info(
            f"✅ Market analysis complete | "
            f"Score: {market_risk_score:.1f}/100 | "
            f"Sentiment: {overall_sentiment} | "
            f"Time: {elapsed}s"
        )

        # Return both objects as a tuple
        # Caller unpacks like: analysis, output = agent.analyze(signals)
        return analysis, agent_output

    # ── Private helper methods ────────────────────────────────
    # These are the internal steps of the analysis pipeline.
    # Each does one thing. Small, focused, testable.

    def _parse_signal(self, raw) -> MarketSignal:
        """
        Converts raw input into a MarketSignal object.

        Handles BOTH:
        - dict signals (synthetic mode)
        - MarketSignal objects (real-time mode)
        """

        # If it's already a MarketSignal, just return it
        if isinstance(raw, MarketSignal):
            return raw

        # Otherwise treat it as dict (synthetic signals)
        severity_to_relevance = {
            "high": 0.90,
            "medium": 0.65,
            "low": 0.40,
        }

        severity = raw.get("severity", "medium")
        relevance = severity_to_relevance.get(severity, 0.65)

        return MarketSignal(
            signal_type=raw.get("signal_type", "news"),
            source=raw.get("source", "Unknown Source"),
            headline=raw.get("headline", ""),
            summary=raw.get("summary", raw.get("description", "")),
            sentiment=raw.get("sentiment", "neutral"),
            relevance_score=raw.get("relevance_score", relevance),
            impact_on_it=raw.get("impact_on_it", ""),
            severity=severity,
            affected_sectors=raw.get("affected_sectors", []),
            description=raw.get("description", ""),
            date=raw.get("date", ""),
        )

    
    
    def _score_signal(self, signal: MarketSignal) -> float:
        """
        Calculates the risk contribution of one market signal.

        Formula:
            score = relevance × 100 × sentiment_weight × type_multiplier

        Example — NASSCOM report (negative, industry_trend, relevance=0.90):
            score = 0.90 × 100 × 1.0 × 1.2 = 108 → capped at 100

        Example — Rupee stability news (positive, economic, relevance=0.60):
            score = 0.60 × 100 × (-0.5) × 1.3 = -39
            (negative score = reduces overall risk)

        Args:
            signal: MarketSignal object

        Returns:
            float risk contribution (can be negative for positive news)
        """
        # Base score from relevance (0-100 scale)
        base_score = signal.relevance_score * 100

        # Apply sentiment weight
        sentiment_weight = SENTIMENT_WEIGHTS.get(signal.sentiment, 0.0)

        # Apply signal type multiplier
        type_multiplier = SIGNAL_TYPE_MULTIPLIERS.get(signal.signal_type, 1.0)

        return base_score * sentiment_weight * type_multiplier

    def _compute_market_risk(
        self,
        signals: List[MarketSignal],
        scores: List[float]
    ) -> float:
        """
        Combines individual signal scores into one market risk score.

        Method: weighted average of positive scores
        Weights: each signal's relevance_score
        So high-relevance signals affect the final score more.

        Why only positive scores?
        Positive signals already reduced individual scores.
        We don't want to double-count the good news reduction.
        The positive impact is captured in the lower raw scores.

        Returns:
            float between 10 and 100
        """
        if not scores:
            return 30.0  # default neutral baseline if no signals

        # Only use scores where the signal contributed positively to risk
        positive_contributions = [
            (score, signal.relevance_score)
            for score, signal in zip(scores, signals)
            if score > 0
        ]

        if not positive_contributions:
            return 20.0  # all signals were positive news — low market risk

        # Weighted sum: multiply each score by its relevance weight
        weighted_sum = sum(score * weight for score, weight in positive_contributions)

        # Sum of all weights (for normalization)
        weight_total = sum(weight for _, weight in positive_contributions)

        # Weighted average
        raw_score = weighted_sum / weight_total if weight_total > 0 else 30.0

        # Clamp between 10 and 100
        # min(100, max(10, x)) ensures the score stays in valid range
        return min(100.0, max(10.0, raw_score))

    def _determine_sentiment(
        self,
        negative_count: int,
        positive_count: int,
        total: int
    ) -> str:
        """
        Determines the overall market mood based on signal breakdown.

        Logic:
        >60% negative signals → BEARISH  (market is pessimistic)
        >40% negative signals → CAUTIOUS (mixed but leaning negative)
        >50% positive signals → BULLISH  (market is optimistic)
        Otherwise             → NEUTRAL  (mixed signals)

        Args:
            negative_count: number of negative signals
            positive_count: number of positive signals
            total:          total number of signals

        Returns:
            "BEARISH", "CAUTIOUS", "NEUTRAL", or "BULLISH"
        """
        if total == 0:
            return "NEUTRAL"

        neg_ratio = negative_count / total
        pos_ratio = positive_count / total

        if neg_ratio > 0.50:
            return "BEARISH"
        elif neg_ratio > 0.30:
            return "CAUTIOUS"
        elif pos_ratio > 0.50:
            return "BULLISH"
        else:
            return "NEUTRAL"

    def _extract_trends(self, signals: List[MarketSignal]) -> List[str]:
        """
        Extracts key trend statements from the signals.

        These are human-readable bullet points shown in the
        Market Intelligence panel of the dashboard.

        Logic: scans signal headlines for known keywords
        and generates relevant trend statements.

        Returns:
            List of up to 5 trend strings
        """
        trends = []

        # Separate signals by sentiment for pattern matching
        negative = [s for s in signals if s.sentiment == "negative"]
        positive = [s for s in signals if s.sentiment == "positive"]

        # Check for talent/attrition signals
        if any(
            "attrition" in s.headline.lower() or "talent" in s.headline.lower()
            for s in signals
        ):
            trends.append(
                "Tech talent attrition at 18-month high — "
                "resource risk elevated across all active projects"
            )

        # Check for overall negative signal count
        if len(negative) >= 3:
            trends.append(
                f"{len(negative)} negative economic indicators detected — "
                "market risk elevated for IT delivery"
            )

        # Check for AI/GenAI positive signals
        if any(
            "ai" in s.headline.lower() or "ml" in s.headline.lower()
            for s in positive
        ):
            trends.append(
                "AI/ML investment momentum strong — "
                "positive tailwind for data and AI-focused projects"
            )

        # Check for banking sector signals
        if any(
            "bfsi" in s.headline.lower() or "banking" in s.headline.lower()
            for s in negative
        ):
            trends.append(
                "BFSI sector IT budgets under pressure — "
                "payment delays likely for banking clients"
            )

        # Check for macro/RBI signals
        if any(
            "rbi" in s.headline.lower() or "rate" in s.headline.lower()
            for s in signals
        ):
            trends.append(
                "Macro environment cautious — "
                "monitor client budget health and payment timelines"
            )

        # Return max 5 trends
        return trends[:5]

    def _build_it_outlook(
        self,
        market_risk_score: float,
        signals: List[MarketSignal]
    ) -> str:
        """
        Generates the IT sector outlook paragraph.

        This is a rule-based template approach.
        In the AI-enhanced version (with HuggingFace token),
        this would be generated by Mistral-7B.
        For now, templates give consistent, professional output.

        Args:
            market_risk_score: computed 0-100 score
            signals:           all analyzed signals

        Returns:
            2-3 sentence IT sector outlook string
        """
        negative_count = sum(1 for s in signals if s.sentiment == "negative")

        if market_risk_score >= 70:
            return (
                f"The IT sector is facing significant headwinds with "
                f"{negative_count} out of {len(signals)} market indicators "
                f"turning negative. Clients are expected to defer discretionary "
                f"IT spending, creating elevated risk of budget freezes, "
                f"scope reductions, and payment delays in the coming quarter. "
                f"Proactive client engagement and contract review are strongly advised."
            )

        elif market_risk_score >= 50:
            return (
                f"The IT sector outlook is mixed with cautious optimism. "
                f"While core transformation projects continue, discretionary "
                f"initiatives are facing budget scrutiny. Teams with strong "
                f"AI/ML capabilities remain well-positioned, but traditional "
                f"IT services face margin pressure. Client engagement and "
                f"SLA adherence are critical differentiators right now."
            )

        else:
            return (
                f"The IT sector outlook is stable with positive signals "
                f"outweighing concerns. Continued demand for digital "
                f"transformation, cloud migration, and AI projects supports "
                f"healthy delivery pipelines. Market conditions are supportive "
                f"of project execution with no immediate external risk triggers."
            )
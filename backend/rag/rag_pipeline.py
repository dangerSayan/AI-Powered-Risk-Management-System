"""
rag_pipeline.py — RAG Pipeline (Memory System)
===============================================
Stores risk analysis results in ChromaDB and retrieves
relevant context to power the AI chatbot.

FLOW:
  1. User asks question
  2. ChromaDB retrieves top 5 relevant chunks (RAG)
  3. LLM generates answer from those chunks
  4. If LLM fails → rule-based answer from memory
  5. If off-topic → polite redirect
"""

from pathlib import Path
from typing import List, Optional
from loguru import logger

from backend.models.schemas import SystemAnalysisResult, RiskReport, ChatMessage


class RiskRAGPipeline:
    """
    ChromaDB + LangChain RAG pipeline for risk intelligence.

    Lifecycle:
      1. Create:      pipeline = RiskRAGPipeline()
      2. Initialize:  pipeline.initialize()
      3. Store:       pipeline.store_analysis(result)
      4. Query:       pipeline.answer_question("your question")
    """

    def __init__(self):
        self.chroma_client  = None
        self.collection     = None
        self.embeddings     = None
        self.llm            = None
        self._initialized   = False
        self._last_analysis = None
        logger.info("🧠 RAG Pipeline created (models not yet loaded)")

    # ── Initialization ────────────────────────────────────────

    def initialize(self):
        """Loads all heavy models and connects to ChromaDB."""
        if self._initialized:
            return

        try:
            import chromadb
            from chromadb.config import Settings
            from config.llm_config import AppConfig, LLMConfig

            persist_dir = AppConfig.CHROMA_PERSIST_DIR
            Path(persist_dir).mkdir(parents=True, exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )

            self.collection = self.chroma_client.get_or_create_collection(
                name=AppConfig.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(
                f"✅ ChromaDB connected | "
                f"Collection: '{AppConfig.CHROMA_COLLECTION_NAME}' | "
                f"Existing docs: {self.collection.count()}"
            )

            logger.info("⏳ Loading embedding model...")
            self.embeddings = LLMConfig.get_embeddings()
            if not self.embeddings:
                raise RuntimeError("Embedding model failed to load")
            logger.info("✅ Embedding model ready")

            logger.info("⏳ Loading LLM...")
            self.llm = LLMConfig.get_llm(temperature=0.2, max_tokens=1024)
            if self.llm:
                logger.info("✅ LLM ready — AI-powered chat enabled")
            else:
                logger.warning("⚠️ LLM not available — chat will use rule-based answers.")

            self._initialized = True
            logger.info("🚀 RAG Pipeline fully initialized")

        except Exception as e:
            logger.error(f"❌ RAG Pipeline initialization failed: {e}")
            self._initialized = False
            raise

    # ── Store Analysis Results ────────────────────────────────

    def store_analysis(self, analysis: SystemAnalysisResult):
        """
        Stores all risk reports in ChromaDB + keeps in memory.
        Memory copy = instant rule-based fallback if LLM fails.
        """
        self._last_analysis = analysis

        if not self._initialized:
            logger.warning("RAG not initialized — skipping ChromaDB storage")
            return

        documents = []
        metadatas = []
        ids       = []

        for report in analysis.risk_reports:
            chunks = self._chunk_report(report)
            for i, chunk in enumerate(chunks):
                doc_id = f"{report.project_code}_{report.id}_{i}"
                documents.append(chunk["text"])
                ids.append(doc_id)
                metadatas.append({
                    "project_code": report.project_code,
                    "project_name": report.project_name,
                    "risk_score":   float(report.overall_risk_score),
                    "risk_level":   report.risk_level.value,
                    "chunk_type":   chunk["type"],
                    "generated_at": report.generated_at.isoformat(),
                    "analysis_id":  analysis.analysis_id,
                })

        market_text = self._format_market_analysis(analysis)
        documents.append(market_text)
        ids.append(f"market_{analysis.analysis_id}")
        metadatas.append({
            "project_code": "MARKET",
            "project_name": "Market Analysis",
            "risk_score":   float(analysis.market_analysis.market_risk_score),
            "risk_level":   "MARKET",
            "chunk_type":   "market_analysis",
            "generated_at": analysis.analyzed_at.isoformat(),
            "analysis_id":  analysis.analysis_id,
        })

        try:
            logger.info(f"⏳ Embedding {len(documents)} chunks...")
            embeddings_list = self.embeddings.embed_documents(documents)
            self.collection.upsert(
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(
                f"✅ Stored {len(documents)} chunks in ChromaDB | "
                f"Total: {self.collection.count()}"
            )
        except Exception as e:
            logger.error(f"❌ ChromaDB storage error: {e}")

    # ── Answer Questions ──────────────────────────────────────

    def answer_question(
        self,
        question: str,
        chat_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """
        FLOW:
          Step 1 → Check if off-topic (instant block, no LLM wasted)
          Step 2 → RAG: retrieve relevant chunks from ChromaDB
          Step 3 → LLM: generate answer from retrieved chunks
          Step 4 → If LLM fails: rule-based answer from memory
          Step 5 → If no data: ask user to run analysis
        """
        if not self._initialized:
            return "The AI system is still initializing. Please wait."

        # ── Step 1: Off-topic check (instant, saves LLM calls) ─────
        # Check BEFORE doing any expensive RAG/LLM work
        if not self._is_risk_related(question):
            return (
                "I'm RiskPulse AI — I can only answer questions about your "
                "IT project portfolio. Try asking:\n\n"
                "• *Which project has the highest risk?*\n"
                "• *Tell me all projects in detail*\n"
                "• *What should I do about PRJ-005?*\n"
                "• *What is the market situation?*\n"
                "• *Give me a portfolio summary*"
            )

        if not self._last_analysis:
            return (
                "No risk analysis data found yet. "
                "Please go to the **⚙️ Run Analysis** tab and click "
                "**▶ Run Full Analysis** first."
            )

        # ── Step 2 + 3: RAG retrieval → LLM answer ─────────────────
        # This is the PRIMARY path — LLM gives best quality answers
        if self.llm and self.collection.count() > 0:
            chunks = self._retrieve_chunks(question, n_results=5)
            if chunks:
                # Always build full portfolio context so LLM knows ALL projects
                # RAG chunks give focused relevance, full context prevents "no data" errors
                context = self._build_full_context() 
                llm_answer = self._generate_llm_answer(
                    question, context, chat_history
                )
                # Only use LLM answer if it's meaningful
                # (not empty, not an error, not too short)
                if llm_answer and len(llm_answer.strip()) > 20:
                    return llm_answer

        # ── Step 4: Rule-based fallback ─────────────────────────────
        # Reaches here only if LLM failed or returned empty response
        logger.info("📋 Using rule-based fallback answer")
        return self._answer_from_memory(question)
    
    # ── Helper Methods ─────────────────────────────────────────

    def _build_full_context(self) -> str:
        """
        Builds complete context from ALL projects in memory.
        This ensures the LLM always has data for every project,
        not just the top RAG-retrieved chunks.
        
        Why this is needed:
        RAG retrieval returns the most SIMILAR chunks to the question.
        If you ask about PRJ-005, it might return PRJ-001 chunks if
        PRJ-001's text happens to match better by embedding similarity.
        By including ALL project data, the LLM always has the full picture.
        """
        if not self._last_analysis:
            return ""

        analysis = self._last_analysis
        parts = []

        # Add all project reports
        for report in analysis.risk_reports:
            alerts_text = "\n".join(
                f"  - {a}" for a in report.key_alerts
            ) if report.key_alerts else "  - No active alerts"

            mits_text = "\n".join(
                f"  - Priority {m.priority}: {m.action} "
                f"(Owner: {m.owner}, Timeline: {m.timeline}, "
                f"Risk reduction: -{m.estimated_risk_reduction:.0f} pts)"
                for m in report.mitigation_strategies
            ) if report.mitigation_strategies else "  - No mitigation strategies"

            cats_text = "\n".join(
                f"  - {cat}: {score:.0f}/100"
                for cat, score in sorted(
                    report.category_scores.items(),
                    key=lambda x: x[1], reverse=True
                )
            )

            parts.append(f"""
    PROJECT: {report.project_name}
    CODE: {report.project_code}
    RISK SCORE: {report.overall_risk_score:.0f}/100
    RISK LEVEL: {report.risk_level.value}
    SUMMARY: {report.executive_summary}

    RISK CATEGORY SCORES:
    {cats_text}

    ACTIVE ALERTS:
    {alerts_text}

    MITIGATION STRATEGIES:
    {mits_text}
    """)

        # Add market analysis
        ma = analysis.market_analysis
        trends = "\n".join(f"  - {t}" for t in ma.key_trends)
        parts.append(f"""
    MARKET ANALYSIS:
    Market Risk Score: {ma.market_risk_score:.0f}/100
    Sentiment: {ma.overall_market_sentiment}
    Outlook: {ma.it_sector_outlook}
    Key Trends:
    {trends}
    """)

        parts.append(
            f"\nPORTFOLIO SUMMARY:\n"
            f"Portfolio Risk Score: {analysis.portfolio_risk_score:.0f}/100\n"
            f"HIGH/CRITICAL Projects: {analysis.high_risk_count}/{analysis.total_projects_analyzed}\n"
            f"Most Critical: {analysis.most_critical_project}\n"
        )

        return "\n===========================\n".join(parts)

    # ── Off-topic detection ───────────────────────────────────

    def _is_risk_related(self, question: str) -> bool:
        """
        Returns True if question is about IT project risk.
        Returns False for greetings, small talk, unrelated topics.
        Checked BEFORE doing any expensive operations.
        """
        q = question.lower().strip()

        # Very short inputs (hi, hey, ok, thanks)
        if len(q) < 6:
            return False

        # Common off-topic patterns
        off_topic = [
            "how are you", "what are you", "who are you",
            "good morning", "good evening", "good night",
            "hello", "hey there", "what's up", "sup",
            "tell me a joke", "weather", "news today",
            "thank you", "thanks", "bye", "goodbye",
            "what time", "what date", "calculate",
        ]
        if any(phrase in q for phrase in off_topic):
            return False

        # Must contain at least one risk-related keyword
        risk_keywords = [
            "project", "risk", "score", "alert", "prj", "team", "budget",
            "payment", "schedule", "delay", "market", "portfolio", "analysis",
            "report", "mitigation", "client", "resource", "financial", "atlas",
            "helix", "nova", "orion", "zenith", "status", "health", "issue",
            "detail", "summary", "tell", "show", "give", "what", "which",
            "how", "why", "compare", "worst", "best", "highest", "lowest",
            "action", "fix", "help", "improve", "strategy", "plan",
        ]
        return any(kw in q for kw in risk_keywords)

    # ── Rule-based answer from memory ────────────────────────

    def _answer_from_memory(self, question: str) -> str:
        """
        Pattern-based answers using in-memory analysis data.
        Called as FALLBACK when LLM fails.
        Covers all common question types with accurate, data-backed answers.
        """
        analysis = self._last_analysis
        reports  = analysis.risk_reports
        q        = question.lower()

        sorted_reports = sorted(
            reports,
            key=lambda r: r.overall_risk_score,
            reverse=True
        )

        # ── All projects in detail ─────────────────────────────────
        if any(p in q for p in [
            "all project", "every project", "each project",
            "tell all", "detail", "full detail", "complete detail",
            "all in detail", "describe all", "explain all"
        ]):
            lines = [f"**Complete Portfolio Report — All {len(reports)} Projects**\n"]
            lines.append("=" * 50 + "\n")
            for r in sorted_reports:
                icon = ("🔴" if r.risk_level.value == "CRITICAL" else
                        "🟡" if r.risk_level.value == "HIGH" else
                        "🔵" if r.risk_level.value == "MEDIUM" else "🟢")
                alerts_text = "\n".join(f"  • {a}" for a in r.key_alerts[:3])
                top_cats = sorted(r.category_scores.items(),
                                  key=lambda x: x[1], reverse=True)[:3]
                cat_text = ", ".join(f"{c}: {s:.0f}" for c, s in top_cats)
                mits = r.mitigation_strategies[:2]
                mit_text = "\n".join(
                    f"  • P{m.priority}: {m.action[:70]}... ({m.timeline})"
                    for m in mits
                ) if mits else "  • No actions generated"
                lines.append(
                    f"{icon} **{r.project_name} ({r.project_code})**\n"
                    f"Risk Score: **{r.overall_risk_score:.0f}/100** — {r.risk_level.value}\n"
                    f"Summary: {r.executive_summary}\n"
                    f"Top Risk Areas: {cat_text}\n"
                    f"Active Alerts:\n{alerts_text}\n"
                    f"Top Actions:\n{mit_text}\n"
                    f"{'─' * 40}\n"
                )
            lines.append(
                f"**Portfolio Score: {analysis.portfolio_risk_score:.0f}/100 "
                f"| {analysis.high_risk_count} projects need attention**"
            )
            return "\n".join(lines)

        # ── Highest / most risky ───────────────────────────────────
        if any(p in q for p in [
            "highest", "most risky", "worst", "dangerous",
            "critical", "top risk", "most at risk", "biggest risk"
        ]):
            top = sorted_reports[0]
            alerts_text = "\n".join(f"• {a}" for a in top.key_alerts[:3])
            mits = top.mitigation_strategies[:3]
            mit_text = "\n".join(
                f"• P{m.priority}: {m.action[:80]}... ({m.timeline})"
                for m in mits
            )
            return (
                f"**{top.project_name} ({top.project_code})** has the highest "
                f"risk score of **{top.overall_risk_score:.0f}/100** "
                f"({top.risk_level.value} risk).\n\n"
                f"**Summary:** {top.executive_summary}\n\n"
                f"**Active Alerts:**\n{alerts_text}\n\n"
                f"**Recommended Actions:**\n{mit_text}"
            )

        # ── Lowest / safest ────────────────────────────────────────
        if any(p in q for p in [
            "lowest", "safest", "best", "least risky", "healthiest"
        ]):
            bottom = sorted_reports[-1]
            return (
                f"**{bottom.project_name} ({bottom.project_code})** is the "
                f"safest project with a score of "
                f"**{bottom.overall_risk_score:.0f}/100** "
                f"({bottom.risk_level.value} risk).\n\n"
                f"{bottom.executive_summary}"
            )

        # ── Specific project code or name ──────────────────────────
        for report in reports:
            if report.project_code.lower() in q or \
               report.project_name.lower() in q:
                alerts_text = "\n".join(
                    f"• {a}" for a in report.key_alerts[:5]
                ) if report.key_alerts else "• No active alerts"
                mits = report.mitigation_strategies[:4]
                mit_text = "\n".join(
                    f"• **Priority {m.priority}:** {m.action}\n"
                    f"  Owner: {m.owner} | Timeline: {m.timeline} | "
                    f"Risk reduction: -{m.estimated_risk_reduction:.0f} pts"
                    for m in mits
                ) if mits else "• No mitigation strategies generated"
                cats = sorted(report.category_scores.items(),
                              key=lambda x: x[1], reverse=True)
                cat_text = "\n".join(f"• {c}: {s:.0f}/100" for c, s in cats)
                return (
                    f"**{report.project_name} ({report.project_code})**\n\n"
                    f"Risk Score: **{report.overall_risk_score:.0f}/100** "
                    f"({report.risk_level.value})\n\n"
                    f"**Summary:** {report.executive_summary}\n\n"
                    f"**Risk Category Scores:**\n{cat_text}\n\n"
                    f"**Active Alerts:**\n{alerts_text}\n\n"
                    f"**Action Plan:**\n{mit_text}"
                )

        # ── Mitigation / what to do ────────────────────────────────
        if any(p in q for p in [
            "mitigation", "what should", "what to do", "how to fix",
            "recommend", "action", "fix", "address", "solve", "help",
            "improve", "reduce risk", "next step", "migration"
        ]):
            lines = ["**Top Priority Actions Across All Projects:**\n"]
            for r in sorted_reports[:3]:
                mits = r.mitigation_strategies[:2]
                for m in mits:
                    lines.append(
                        f"• **[{r.project_code} P{m.priority}]** {m.action}\n"
                        f"  Owner: {m.owner} | Timeline: {m.timeline}"
                    )
            return "\n".join(lines)

        # ── Payment / financial ────────────────────────────────────
        if any(p in q for p in [
            "payment", "invoice", "financial", "budget",
            "money", "overrun", "cost", "billing"
        ]):
            lines = ["**Financial Risk Summary:**\n"]
            for r in sorted_reports:
                fin = r.category_scores.get("FINANCIAL", 0)
                c = ("🔴" if fin >= 75 else "🟡" if fin >= 55
                     else "🔵" if fin >= 30 else "🟢")
                lines.append(f"{c} **{r.project_code}** — Financial Risk: {fin:.0f}/100")
                for alert in r.key_alerts:
                    if any(w in alert.lower() for w in
                           ["payment", "invoice", "budget", "financial", "₹"]):
                        lines.append(f"  ⚠️ {alert}")
            return "\n".join(lines)

        # ── Schedule / delay ───────────────────────────────────────
        if any(p in q for p in [
            "schedule", "delay", "late", "deadline",
            "timeline", "behind", "overdue", "days"
        ]):
            lines = ["**Schedule Risk Summary:**\n"]
            for r in sorted_reports:
                sched = r.category_scores.get("SCHEDULE", 0)
                c = ("🔴" if sched >= 75 else "🟡" if sched >= 55
                     else "🔵" if sched >= 30 else "🟢")
                lines.append(f"{c} **{r.project_code}** — Schedule Risk: {sched:.0f}/100")
                for alert in r.key_alerts:
                    if any(w in alert.lower() for w in
                           ["delay", "behind", "schedule", "days"]):
                        lines.append(f"  ⚠️ {alert}")
            return "\n".join(lines)

        # ── Team / resource ────────────────────────────────────────
        if any(p in q for p in [
            "team", "resource", "resign", "staff",
            "people", "attrition", "headcount", "member"
        ]):
            lines = ["**Resource Risk Summary:**\n"]
            for r in sorted_reports:
                res = r.category_scores.get("RESOURCE", 0)
                c = ("🔴" if res >= 75 else "🟡" if res >= 55
                     else "🔵" if res >= 30 else "🟢")
                lines.append(f"{c} **{r.project_code}** — Resource Risk: {res:.0f}/100")
                for alert in r.key_alerts:
                    if any(w in alert.lower() for w in
                           ["resign", "team", "resource", "staff", "member"]):
                        lines.append(f"  ⚠️ {alert}")
            return "\n".join(lines)

        # ── Market / external ──────────────────────────────────────
        if any(p in q for p in [
            "market", "external", "economy", "industry",
            "nasscom", "rbi", "bfsi", "sector", "trend"
        ]):
            ma = analysis.market_analysis
            trends = "\n".join(f"• {t}" for t in ma.key_trends)
            signals_text = "\n".join(
                f"• [{s.sentiment.upper()}] {s.source}: {s.headline}"
                for s in ma.signals
            )
            return (
                f"**Market Intelligence Report**\n\n"
                f"Market Risk Score: **{ma.market_risk_score:.0f}/100** "
                f"({ma.overall_market_sentiment})\n\n"
                f"**Sector Outlook:**\n{ma.it_sector_outlook}\n\n"
                f"**Key Trends:**\n{trends}\n\n"
                f"**All Market Signals:**\n{signals_text}"
            )

        # ── Alerts / warnings ──────────────────────────────────────
        if any(p in q for p in [
            "alert", "warning", "urgent", "immediate", "critical issue"
        ]):
            lines = ["**All Active Risk Alerts:**\n"]
            for r in sorted_reports:
                if r.key_alerts:
                    lines.append(f"\n**{r.project_code} — {r.project_name}:**")
                    for alert in r.key_alerts:
                        lines.append(f"• {alert}")
            return "\n".join(lines)

        # ── Overview / portfolio / summary ─────────────────────────
        if any(p in q for p in [
            "overview", "summary", "all", "portfolio", "status",
            "list", "show", "give me", "tell me"
        ]):
            lines = ["**Portfolio Risk Summary:**\n"]
            for r in sorted_reports:
                icon = ("🔴" if r.risk_level.value == "CRITICAL" else
                        "🟡" if r.risk_level.value == "HIGH" else
                        "🔵" if r.risk_level.value == "MEDIUM" else "🟢")
                lines.append(
                    f"{icon} **{r.project_code}** — {r.project_name}: "
                    f"**{r.overall_risk_score:.0f}/100** ({r.risk_level.value})\n"
                    f"   {r.executive_summary[:120]}..."
                )
            lines.append(
                f"\n**Portfolio Score: {analysis.portfolio_risk_score:.0f}/100 "
                f"| {analysis.high_risk_count} projects need attention**"
            )
            return "\n".join(lines)

        # ── Default: general portfolio overview ────────────────────
        top = sorted_reports[0]
        return (
            f"Based on the latest analysis of {len(reports)} projects:\n\n"
            f"🔴 Highest risk: **{top.project_name}** "
            f"({top.overall_risk_score:.0f}/100 — {top.risk_level.value})\n"
            f"📊 Portfolio score: **{analysis.portfolio_risk_score:.0f}/100**\n"
            f"⚠️ Projects needing attention: **{analysis.high_risk_count}**\n\n"
            f"Try asking:\n"
            f"• *Tell me all projects in detail*\n"
            f"• *Tell me about PRJ-005*\n"
            f"• *What are the mitigation strategies?*"
        )

    # ── RAG Retrieval ─────────────────────────────────────────

    def _retrieve_chunks(self, question: str, n_results: int = 5) -> List[dict]:
        """Embeds the question and searches ChromaDB for similar chunks."""
        try:
            query_vector = self.embeddings.embed_query(question)
            count = self.collection.count()
            if count == 0:
                return []

            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=min(n_results, count),
                include=["documents", "metadatas", "distances"]
            )

            chunks = []
            if results["documents"] and results["documents"][0]:
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                ):
                    chunks.append({
                        "text":      doc,
                        "metadata":  meta,
                        "relevance": round(1 - dist, 3)
                    })

            logger.debug(f"RAG retrieved {len(chunks)} chunks for: '{question}'")
            return chunks

        except Exception as e:
            logger.error(f"ChromaDB retrieval error: {e}")
            return []

    # ── LLM Answer Generation ─────────────────────────────────

    def _generate_llm_answer(
        self,
        question: str,
        context: str,
        chat_history: Optional[List[ChatMessage]]
    ) -> str:

        history_text = ""

        if chat_history and len(chat_history) > 1:
            recent = chat_history[-4:]
            history_text = "\nRECENT CONVERSATION:\n"
            history_text += "\n".join(
                f"{m.role.upper()}: {m.content[:150]}"
                for m in recent
            )

        prompt = f"""
    You are RiskPulse AI, an expert IT Project Risk Management Assistant.

    Answer the question using ONLY the risk data below.

    Be concise, professional, and cite project codes.

    RISK DATA:
    {context}

    {history_text}

    QUESTION:
    {question}
    """

        try:

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert IT project risk management analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = self.llm.invoke(messages)

            if hasattr(response, "content"):
                text = response.content
            else:
                text = str(response)

            text = text.strip()

            if len(text) < 20:
                logger.warning("LLM returned short answer, using fallback")
                return ""

            logger.info("✅ LLM generated answer successfully")
            return text

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return ""




    # ── Helper Methods ────────────────────────────────────────

    def _chunk_report(self, report: RiskReport) -> List[dict]:
        """Splits a RiskReport into 4 focused semantic chunks."""
        chunks = []

        chunks.append({
            "type": "executive_summary",
            "text": (
                f"PROJECT RISK SUMMARY — "
                f"{report.project_name} ({report.project_code})\n"
                f"Risk Score: {report.overall_risk_score:.0f}/100 | "
                f"Risk Level: {report.risk_level.value}\n\n"
                f"{report.executive_summary}"
            )
        })

        if report.key_alerts:
            chunks.append({
                "type": "alerts",
                "text": (
                    f"ACTIVE ALERTS — {report.project_code}\n"
                    + "\n".join(report.key_alerts)
                )
            })

        if report.risk_factors:
            factors_text = f"RISK FACTORS — {report.project_code}\n"
            for factor in report.risk_factors:
                factors_text += (
                    f"\n{factor.category.value}: {factor.impact_score:.0f}/100\n"
                )
                for ev in factor.evidence:
                    factors_text += f"  - {ev}\n"
            chunks.append({"type": "risk_factors", "text": factors_text})

        if report.mitigation_strategies:
            mit_text = f"MITIGATION STRATEGIES — {report.project_code}\n"
            for m in report.mitigation_strategies:
                mit_text += (
                    f"\nPriority {m.priority}: {m.action}\n"
                    f"  Owner: {m.owner} | Timeline: {m.timeline}\n"
                )
            chunks.append({"type": "mitigations", "text": mit_text})

        return chunks

    def _format_market_analysis(self, analysis: SystemAnalysisResult) -> str:
        ma = analysis.market_analysis
        lines = [
            "MARKET ANALYSIS",
            f"Market Risk Score: {ma.market_risk_score:.0f}/100",
            f"Sentiment: {ma.overall_market_sentiment}",
            f"Outlook: {ma.it_sector_outlook}",
            "\nKey Trends:"
        ]
        for trend in ma.key_trends:
            lines.append(f"  - {trend}")
        for signal in ma.signals:
            lines.append(
                f"  [{signal.sentiment.upper()}] {signal.source}: {signal.headline}"
            )
        return "\n".join(lines)

    def _build_context_string(self, chunks: List[dict]) -> str:

        parts = []

        for chunk in chunks[:5]:

            meta = chunk["metadata"]

            part = f"""
    PROJECT: {meta['project_name']}
    CODE: {meta['project_code']}
    RISK SCORE: {meta['risk_score']}
    RISK LEVEL: {meta['risk_level']}

    CONTENT:
    {chunk['text']}
    """

            parts.append(part.strip())

        return "\n\n---------------------------\n\n".join(parts)

    def get_stats(self) -> dict:
        if not self._initialized:
            return {"initialized": False, "document_count": 0, "llm_available": False}
        return {
            "initialized":      True,
            "document_count":   self.collection.count(),
            "collection_name":  self.collection.name,
            "llm_available":    self.llm is not None,
            "memory_available": self._last_analysis is not None,
        }
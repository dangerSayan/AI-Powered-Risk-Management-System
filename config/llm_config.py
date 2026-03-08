"""
llm_config.py — AI Model Configuration
=======================================
Central place for all LLM and embedding model setup.

Current provider:  HuggingFace (Mistral-7B-Instruct)
Future provider:   AWS Bedrock (Claude 3 Sonnet)

To switch providers, change one line in .env:
    LLM_PROVIDER=huggingface   ← change to "bedrock"

Nothing else in the codebase needs to change.
"""

import os
from pathlib import Path
from loguru import logger

# python-dotenv reads your .env file and loads all
# the key=value pairs as environment variables.
# After this call, os.getenv("HUGGINGFACEHUB_API_TOKEN")
# will return whatever you put in your .env file.
from dotenv import load_dotenv
load_dotenv()


# ============================================================
# LLMConfig — Everything related to the AI language model
# ============================================================

class LLMConfig:
    """
    Manages LLM provider selection and initialization.

    Reads configuration from environment variables (.env file).
    Supports HuggingFace now, AWS Bedrock later.

    Usage (in any agent file):
        from config.llm_config import LLMConfig
        llm = LLMConfig.get_llm()
        response = llm.invoke("your prompt here")
    """

    # ── Read settings from .env ───────────────────────────────

    # Which provider to use: "huggingface", "bedrock", or "openai"
    PROVIDER = os.getenv("LLM_PROVIDER", "huggingface")

    # HuggingFace settings
    HF_TOKEN    = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    HF_MODEL_ID = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")
    HF_EMBEDDING_MODEL = os.getenv(
        "HF_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # AWS Bedrock settings (used in Phase 2 — AWS deployment)
    AWS_REGION       = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID = os.getenv(
        "BEDROCK_MODEL_ID",
        "anthropic.claude-3-sonnet-20240229-v1:0"
    )

    # ── Public methods ────────────────────────────────────────

    @classmethod
    def get_llm(cls, temperature: float = 0.1, max_tokens: int = 512):
        """
        Returns the configured LLM instance.

        @classmethod means you call this on the class itself,
        not on an instance:
            llm = LLMConfig.get_llm()    ← correct
            llm = LLMConfig().get_llm()  ← unnecessary

        Args:
            temperature: 0.0 = very focused/deterministic
                         1.0 = very creative/random
                         We use 0.1 for risk analysis (we want
                         consistent, factual answers)

            max_tokens:  Maximum length of the response.
                         512 tokens ≈ 350-400 words

        Returns:
            LLM object with an .invoke(prompt) method
            Returns None if no provider is available
        """
        logger.info(f"🤖 Loading LLM — Provider: {cls.PROVIDER}")

        if cls.PROVIDER == "groq":
            return cls._get_groq_llm(temperature, max_tokens)
        elif cls.PROVIDER == "huggingface":
            return cls._get_huggingface_llm(temperature, max_tokens)

        elif cls.PROVIDER == "bedrock":
            return cls._get_bedrock_llm(temperature, max_tokens)

        elif cls.PROVIDER == "openai":
            return cls._get_openai_llm(temperature, max_tokens)

        else:
            logger.warning(
                f"⚠️ Unknown LLM provider: '{cls.PROVIDER}'. "
                f"Falling back to HuggingFace."
            )
            return cls._get_huggingface_llm(temperature, max_tokens)

    @classmethod
    def get_embeddings(cls):
        """
        Returns the embedding model.

        Embeddings convert text → numbers for ChromaDB.
        We always use HuggingFace sentence-transformers for this
        regardless of which LLM provider is selected.

        Why? Because:
        1. sentence-transformers runs locally (no API cost)
        2. It's very fast for embedding
        3. all-MiniLM-L6-v2 is proven for semantic search tasks

        First call: downloads the model (~90MB) to your machine
        Subsequent calls: loads from local cache (fast)

        Returns:
            HuggingFaceEmbeddings object
        """
        logger.info(f"📐 Loading embedding model: {cls.HF_EMBEDDING_MODEL}")

        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(
                model_name=cls.HF_EMBEDDING_MODEL,

                # device="cpu" means run on your processor
                # device="cuda" would use GPU if available
                model_kwargs={"device": "cpu"},

                # normalize_embeddings=True means all vectors
                # have length 1 — makes similarity search more accurate
                encode_kwargs={"normalize_embeddings": True}
            )

            logger.info("✅ Embedding model loaded successfully")
            return embeddings

        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            return None

    # ── Private methods (internal use only) ───────────────────
    # Methods starting with _ are private by convention.
    # They're called by get_llm() — not from outside this class.

    @classmethod
    def _get_huggingface_llm(cls, temperature: float, max_tokens: int):

        try:
            from langchain_huggingface import HuggingFaceEndpoint
            from langchain_huggingface import ChatHuggingFace

            if not cls.HF_TOKEN:
                logger.warning(
                    "⚠️ No HuggingFace token found in .env. "
                    "Chat will use rule-based fallback answers."
                )
                return None

            endpoint = HuggingFaceEndpoint(
                repo_id=cls.HF_MODEL_ID,
                huggingfacehub_api_token=cls.HF_TOKEN,
                temperature=temperature,
                max_new_tokens=max_tokens
            )

            llm = ChatHuggingFace(llm=endpoint)

            logger.info(f"✅ HuggingFace Chat LLM ready: {cls.HF_MODEL_ID}")
            return llm

        except Exception as e:
            logger.error(f"❌ HuggingFace LLM failed: {e}")
            logger.info("💡 App will continue with rule-based answers")
            return None
        
    @classmethod
    def _get_groq_llm(cls, temperature: float, max_tokens: int):
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY", ""),
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info("✅ Groq LLM ready: llama-3.3-70b-versatile")
            return llm
        except Exception as e:
            logger.error(f"❌ Groq failed: {e}")
            return None

    @classmethod
    def _get_bedrock_llm(cls, temperature: float, max_tokens: int):
        """
        Sets up AWS Bedrock LLM.

        This will be activated in Phase 2 (AWS deployment).
        Uses Claude 3 Sonnet by default — enterprise-grade model.

        Requires:
        - AWS_ACCESS_KEY_ID in .env
        - AWS_SECRET_ACCESS_KEY in .env
        - AWS_REGION in .env
        - Bedrock access enabled in your AWS account
        """
        try:
            import boto3
            from langchain_community.llms import Bedrock

            logger.info(f"☁️ Connecting to AWS Bedrock in {cls.AWS_REGION}...")

            # Create AWS client
            bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=cls.AWS_REGION
            )

            llm = Bedrock(
                client=bedrock_client,
                model_id=cls.BEDROCK_MODEL_ID,
                model_kwargs={
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )

            logger.info(f"✅ AWS Bedrock LLM ready: {cls.BEDROCK_MODEL_ID}")
            return llm

        except Exception as e:
            logger.error(f"❌ AWS Bedrock failed: {e}")
            logger.info("💡 Falling back to HuggingFace...")
            # Graceful fallback — try HuggingFace if Bedrock fails
            return cls._get_huggingface_llm(temperature, max_tokens)

    @classmethod
    def _get_openai_llm(cls, temperature: float, max_tokens: int):
        """
        OpenAI fallback — in case neither HF nor Bedrock works.
        Requires OPENAI_API_KEY in .env.
        """
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model="gpt-4o-mini",
                temperature=temperature,
                max_tokens=max_tokens
            )

            logger.info("✅ OpenAI LLM ready: gpt-4o-mini")
            return llm

        except Exception as e:
            logger.error(f"❌ OpenAI LLM failed: {e}")
            return None


# ============================================================
# AppConfig — Application-level settings
# Not LLM-specific. These are used across the whole app.
# ============================================================

class AppConfig:
    """
    Application configuration — constants and settings
    used across frontend and backend.

    Why a class instead of plain variables?
    Because we can add logic (like get_risk_level) and
    everything is namespaced under AppConfig — no conflicts
    with other variable names in your code.
    """

    # Basic app info
    APP_NAME    = os.getenv("APP_NAME", "RiskPulse AI")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    LOG_LEVEL   = os.getenv("LOG_LEVEL", "INFO")

    # ChromaDB settings
    # This is the folder where ChromaDB saves its data on disk
    _BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CHROMA_PERSIST_DIR = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(_BASE_DIR / "data" / "chromadb")
    )
    CHROMA_COLLECTION_NAME  = os.getenv("CHROMA_COLLECTION_NAME", "risk_reports")

    # How often to auto-refresh risk analysis (Phase 4 feature)
    RISK_REFRESH_INTERVAL = int(
        os.getenv("RISK_REFRESH_INTERVAL_MINUTES", "30")
    )

    # ── Risk Score Thresholds ─────────────────────────────────
    # These define the boundaries between risk levels.
    # Based on standard IT project risk management frameworks.
    #
    # Score  0-29  → LOW      (green)
    # Score 30-54  → MEDIUM   (blue)
    # Score 55-74  → HIGH     (amber)
    # Score 75-100 → CRITICAL (red)

    RISK_THRESHOLD_LOW      = 30
    RISK_THRESHOLD_MEDIUM   = 55
    RISK_THRESHOLD_HIGH     = 75

    @classmethod
    def get_risk_level(cls, score: float) -> str:
        """
        Converts a numeric score into a risk level label.

        Used by Risk Scoring Agent after computing the score.
        Also used by frontend for color-coding.

        Args:
            score: float between 0 and 100

        Returns:
            "LOW", "MEDIUM", "HIGH", or "CRITICAL"

        Example:
            AppConfig.get_risk_level(72.5)  →  "HIGH"
            AppConfig.get_risk_level(28.0)  →  "LOW"
            AppConfig.get_risk_level(80.0)  →  "CRITICAL"
        """
        if score < cls.RISK_THRESHOLD_LOW:
            return "LOW"
        elif score < cls.RISK_THRESHOLD_MEDIUM:
            return "MEDIUM"
        elif score < cls.RISK_THRESHOLD_HIGH:
            return "HIGH"
        else:
            return "CRITICAL"

    @classmethod
    def get_risk_color(cls, risk_level: str) -> str:
        """
        Returns the hex color code for a risk level.
        Used by the Streamlit frontend for consistent coloring.

        Args:
            risk_level: "LOW", "MEDIUM", "HIGH", or "CRITICAL"

        Returns:
            Hex color string like "#e84545"
        """
        colors = {
            "LOW":      "#10b981",  # green
            "MEDIUM":   "#3b82f6",  # blue
            "HIGH":     "#f59e0b",  # amber
            "CRITICAL": "#e84545",  # red
        }
        # .get(key, default) returns default if key not found
        return colors.get(risk_level, "#8b96aa")  # grey as fallback


# ============================================================
# QUICK TEST
# Run this file directly to verify LLM setup:
# python -m config.llm_config
# ============================================================

if __name__ == "__main__":
    print("\n🔧 Testing RiskPulse AI Configuration\n")

    # Test AppConfig
    print("📋 App Settings:")
    print(f"   App Name:    {AppConfig.APP_NAME}")
    print(f"   Version:     {AppConfig.APP_VERSION}")
    print(f"   LLM Provider: {LLMConfig.PROVIDER}")
    print(f"   ChromaDB:    {AppConfig.CHROMA_PERSIST_DIR}")

    # Test risk level logic
    print("\n🎯 Risk Level Thresholds:")
    test_scores = [15, 42, 68, 82]
    for score in test_scores:
        level = AppConfig.get_risk_level(score)
        color = AppConfig.get_risk_color(level)
        print(f"   Score {score:>3} → {level:<8} ({color})")

    # Test embeddings (this may download the model first time)
    print("\n📐 Testing Embedding Model...")
    embeddings = LLMConfig.get_embeddings()
    if embeddings:
        test_text = "project payment delayed"
        result = embeddings.embed_query(test_text)
        print(f"   ✅ Embedded '{test_text}'")
        print(f"   Vector dimensions: {len(result)}")
        print(f"   First 5 values: {[round(x, 4) for x in result[:5]]}")
    else:
        print("   ❌ Embeddings failed — check your setup")

    # Test LLM connection
    print(f"\n🤖 Testing LLM ({LLMConfig.PROVIDER})...")
    llm = LLMConfig.get_llm()
    if llm:
        print("   ✅ LLM loaded successfully")
        print("   💡 Tip: call llm.invoke('your prompt') to generate text")
    else:
        print("   ⚠️ LLM not available — add token to .env for AI chat")
        print("   💡 App still works fully — chat uses smart fallback answers")

    print("\n✅ Configuration test complete!\n")
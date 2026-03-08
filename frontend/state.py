"""
state.py — Streamlit Session State Manager
==========================================
Centralizes all st.session_state access.

Why centralize state?
Without this, every page would directly read/write
st.session_state["analysis_result"] etc.
If the key name ever changes, you'd update 4 files.
With this, you update one place.

Also documents exactly what state exists in the app.
"""

import streamlit as st
from typing import Optional
from backend.models.schemas import SystemAnalysisResult, ChatMessage


class State:
    """
    Thin wrapper around st.session_state.
    All methods are @staticmethod — no instance needed.
    Call like: State.get_analysis()
    """

    # Key constants — change here, updates everywhere
    KEY_ANALYSIS     = "analysis_result"
    KEY_CHAT_HISTORY = "chat_history"
    KEY_RAG          = "rag_pipeline"
    KEY_MANAGER      = "risk_manager"
    KEY_ANALYZING    = "is_analyzing"
    KEY_RAG_READY    = "rag_initialized"

    @staticmethod
    def initialize():
        """
        Sets default values for all state keys.
        Called once at app startup (in app.py).
        Streamlit's session_state ignores setdefault-style
        initialization if the key already exists — so this
        is safe to call on every rerun.
        """
        defaults = {
            State.KEY_ANALYSIS:     None,
            State.KEY_CHAT_HISTORY: [],
            State.KEY_RAG:          None,
            State.KEY_MANAGER:      None,
            State.KEY_ANALYZING:    False,
            State.KEY_RAG_READY:    False,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # ── Analysis Result ───────────────────────────────────────

    @staticmethod
    def get_analysis() -> Optional[SystemAnalysisResult]:
        return st.session_state.get(State.KEY_ANALYSIS)

    @staticmethod
    def set_analysis(result: SystemAnalysisResult):
        st.session_state[State.KEY_ANALYSIS] = result

    @staticmethod
    def has_analysis() -> bool:
        return st.session_state.get(State.KEY_ANALYSIS) is not None

    # ── Chat History ──────────────────────────────────────────

    @staticmethod
    def get_chat_history() -> list:
        return st.session_state.get(State.KEY_CHAT_HISTORY, [])

    @staticmethod
    def add_chat_message(message: ChatMessage):
        history = State.get_chat_history()
        history.append(message)
        st.session_state[State.KEY_CHAT_HISTORY] = history

    @staticmethod
    def clear_chat_history():
        st.session_state[State.KEY_CHAT_HISTORY] = []

    # ── RAG Pipeline ──────────────────────────────────────────

    @staticmethod
    def get_rag():
        return st.session_state.get(State.KEY_RAG)

    @staticmethod
    def set_rag(rag):
        st.session_state[State.KEY_RAG] = rag

    @staticmethod
    def is_rag_ready() -> bool:
        return st.session_state.get(State.KEY_RAG_READY, False)

    @staticmethod
    def set_rag_ready(ready: bool):
        st.session_state[State.KEY_RAG_READY] = ready

    # ── Risk Manager ──────────────────────────────────────────

    @staticmethod
    def get_manager():
        return st.session_state.get(State.KEY_MANAGER)

    @staticmethod
    def set_manager(manager):
        st.session_state[State.KEY_MANAGER] = manager

    # ── Analysis Running Flag ─────────────────────────────────

    @staticmethod
    def is_analyzing() -> bool:
        return st.session_state.get(State.KEY_ANALYZING, False)

    @staticmethod
    def set_analyzing(value: bool):
        st.session_state[State.KEY_ANALYZING] = value
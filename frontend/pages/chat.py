"""
chat.py — AI Chat Interface
============================
RAG-powered chatbot for querying risk data.
"""

import streamlit as st
from datetime import datetime
from frontend.state import State
from backend.models.schemas import ChatMessage


SUGGESTED_QUESTIONS = [
    "Which project has the highest risk?",
    "What should I do about PRJ-005?",
    "What is the market situation?",
    "Which projects have payment delays?",
    "Show me mitigation strategies for PRJ-003",
    "Give me a portfolio summary",
]


def render_chat():
    st.markdown(
        '<h2 style="color:#e2e8f0;margin-bottom:4px">AI Risk Assistant</h2>'
        '<p style="color:#8b96aa;font-size:0.9rem;margin-bottom:24px">'
        'Ask questions about your project portfolio in plain English</p>',
        unsafe_allow_html=True
    )

    rag   = State.get_rag()
    ready = State.is_rag_ready()

    # ── Not ready state ────────────────────────────────────────
    if not ready or not rag:
        st.markdown("""
<div style="background:#1e2130;border:2px dashed #3d4460;
     border-radius:16px;padding:40px;text-align:center">
  <div style="font-size:2rem;margin-bottom:12px">💬</div>
  <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;
       margin-bottom:8px">AI Chat Not Ready</div>
  <div style="color:#8b96aa">
    Run a full analysis from the sidebar first.<br>
    The AI will then be able to answer questions about your projects.
  </div>
</div>
""", unsafe_allow_html=True)
        return

    # ── Suggested questions ────────────────────────────────────
    st.markdown(
        '<div class="section-header">Suggested Questions</div>',
        unsafe_allow_html=True
    )
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"sugg_{i}", width="stretch"):
                _send_message(q, rag)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chat history ───────────────────────────────────────────
    history = State.get_chat_history()

    if not history:
        st.markdown("""
<div style="text-align:center;color:#8b96aa;padding:30px;font-size:0.9rem">
  No messages yet. Ask a question above or type below.
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="section-header">Conversation</div>',
            unsafe_allow_html=True
        )
        for msg in history:
            if msg.role == "user":
                st.markdown(f"""
<div class="chat-user">
  <span style="font-size:0.7rem;color:#8b96aa">You</span><br>
  {msg.content}
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="chat-assistant">
  <span style="font-size:0.7rem;color:#8b96aa">🛡️ RiskPulse AI</span><br>
  {msg.content}
</div>
""", unsafe_allow_html=True)

   # ── Chat Input ─────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    user_input = st.chat_input(
        "Ask about project risks, scores, alerts, mitigations..."
    )

    if user_input:
        _send_message(user_input.strip(), rag)
        st.rerun()

        # ── Clear button ───────────────────────────────────────────
        if history:
            if st.button("🗑 Clear conversation", key="clear_chat"):
                State.clear_chat_history()
                st.rerun()

    # ── RAG status ─────────────────────────────────────────────
    rag_stats = rag.get_stats()
    st.markdown(
        f'<div style="font-size:0.72rem;color:#4a5568;margin-top:16px">'
        f'Knowledge base: {rag_stats["document_count"]} chunks | '
        f'LLM: {"Active" if rag_stats["llm_available"] else "Rule-based"}'
        f'</div>',
        unsafe_allow_html=True
    )


def _send_message(text: str, rag):
    """Adds user message, gets AI response, stores both."""
    # Store user message
    State.add_chat_message(ChatMessage(
        role="user",
        content=text,
        timestamp=datetime.now()
    ))

    # Get AI answer
    history = State.get_chat_history()
    with st.spinner("Thinking..."):
        answer = rag.answer_question(text, chat_history=history)

    # Store assistant response
    State.add_chat_message(ChatMessage(
        role="assistant",
        content=answer,
        timestamp=datetime.now(),
        context_used=True
    ))
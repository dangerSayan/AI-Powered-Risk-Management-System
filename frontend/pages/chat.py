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

    st.markdown("""
<div class="rp-page-header">
  <div class="rp-page-title">AI Risk Assistant</div>
  <div class="rp-page-subtitle">
    Ask questions about your project portfolio in plain English
  </div>
</div>
""", unsafe_allow_html=True)

    rag   = State.get_rag()
    ready = State.is_rag_ready()

    # ── Not ready state ────────────────────────────────────────
    if not ready or not rag:
        st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border);
     border-radius:16px;padding:48px 40px;text-align:center;margin-top:24px">
  <div style="font-size:2.2rem;margin-bottom:16px">💬</div>
  <div style="font-size:1.1rem;font-weight:700;color:var(--text-primary);
       margin-bottom:8px;letter-spacing:-0.01em">AI Chat Not Ready</div>
  <div style="color:var(--text-secondary);font-size:0.85rem;line-height:1.6">
    Run a full analysis from the
    <b style="color:var(--accent)">⚙️ Run Analysis</b> tab first.<br>
    The AI will then be able to answer questions about your projects.
  </div>
</div>
""", unsafe_allow_html=True)
        return

    # ── Suggested questions ────────────────────────────────────
    st.markdown('<div class="section-header">Suggested Questions</div>',
                unsafe_allow_html=True)

    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"sugg_{i}", width="stretch"):
                _send_message(q, rag)
                st.rerun()

    # ── Chat history ───────────────────────────────────────────
    history = State.get_chat_history()

    if not history:
        st.markdown("""
<div style="text-align:center;color:var(--text-muted);
     padding:40px 20px;font-size:0.85rem;line-height:1.8">
  <div style="font-size:1.8rem;margin-bottom:12px">🛡️</div>
  No messages yet — ask a question above or type below.
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-header">Conversation</div>',
                    unsafe_allow_html=True)

        for msg in history:
            ts = msg.timestamp.strftime("%H:%M") if hasattr(msg, "timestamp") else ""
            if msg.role == "user":
                st.markdown(f"""
<div class="chat-user">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:6px">
    <span style="font-size:0.68rem;color:var(--accent);
         font-family:'JetBrains Mono',monospace;font-weight:600;
         letter-spacing:0.06em">YOU</span>
    <span style="font-size:0.65rem;color:var(--text-muted);
         font-family:'JetBrains Mono',monospace">{ts}</span>
  </div>
  <div style="color:var(--text-primary)">{msg.content}</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="chat-assistant">
  <div style="display:flex;justify-content:space-between;
       align-items:center;margin-bottom:6px">
    <span style="font-size:0.68rem;color:var(--text-muted);
         font-family:'JetBrains Mono',monospace;font-weight:600;
         letter-spacing:0.06em">🛡️ RISKPULSE AI</span>
    <span style="font-size:0.65rem;color:var(--text-muted);
         font-family:'JetBrains Mono',monospace">{ts}</span>
  </div>
  <div style="color:var(--text-secondary)">{msg.content}</div>
</div>
""", unsafe_allow_html=True)

    # ── Chat input ─────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    user_input = st.chat_input(
        "Ask about project risks, scores, alerts, mitigations..."
    )

    if user_input:
        _send_message(user_input.strip(), rag)
        st.rerun()

    # ── Clear + status row ─────────────────────────────────────
    if history:
        col_clear, col_status = st.columns([1, 3])
        with col_clear:
            if st.button("🗑  Clear conversation", key="clear_chat"):
                State.clear_chat_history()
                st.rerun()

    # ── RAG status footer ──────────────────────────────────────
    rag_stats = rag.get_stats()
    st.markdown(
        f'<div style="font-size:0.68rem;color:var(--text-muted);'
        f'margin-top:12px;font-family:\'JetBrains Mono\',monospace;'
        f'letter-spacing:0.04em">'
        f'KB: {rag_stats["document_count"]} chunks &nbsp;·&nbsp; '
        f'LLM: {"● Active" if rag_stats["llm_available"] else "○ Rule-based"}'
        f'</div>',
        unsafe_allow_html=True
    )


def _send_message(text: str, rag):
    State.add_chat_message(ChatMessage(
        role="user",
        content=text,
        timestamp=datetime.now()
    ))
    history = State.get_chat_history()
    with st.spinner("Thinking..."):
        answer = rag.answer_question(text, chat_history=history)
    State.add_chat_message(ChatMessage(
        role="assistant",
        content=answer,
        timestamp=datetime.now(),
        context_used=True
    ))
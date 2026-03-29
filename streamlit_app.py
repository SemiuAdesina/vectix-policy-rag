"""Streamlit entrypoint for the VectixLogic policy assistant."""

import streamlit as st

from src.streamlit_logic import bootstrap_state, submit_query

SAMPLE_QUESTIONS = [
    "What are the core hours for remote employees?",
    "How many PTO days can be carried over?",
    "What happens if the Solana RPC endpoint is down?",
    "How quickly must a critical client issue be answered?",
]


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
          background:
            linear-gradient(rgba(255,255,255,0.14), rgba(255,255,255,0.14)),
            linear-gradient(90deg, rgba(19,19,19,0.08) 1px, transparent 1px),
            linear-gradient(rgba(19,19,19,0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(19,19,19,0.03) 1px, transparent 1px),
            linear-gradient(rgba(19,19,19,0.03) 1px, transparent 1px),
            radial-gradient(circle at top left, rgba(15,118,110,0.15), transparent 28%),
            radial-gradient(circle at top right, rgba(199,91,57,0.15), transparent 26%),
            linear-gradient(180deg, #f4efe6 0%, #ebe3d5 100%);
          background-size: auto, 120px 120px, 120px 120px, 24px 24px, 24px 24px, auto, auto, auto;
          background-position: 0 0, -1px -1px, -1px -1px, -1px -1px, -1px -1px, 0 0, 100% 0, 0 0;
          background-attachment: fixed;
        }
        [data-testid="stSidebar"] { background: rgba(255,255,255,0.68); }
        [data-testid="stChatMessage"], [data-testid="stVerticalBlock"] .stAlert {
          border-radius: 22px;
        }
        .hero-card, .mini-card, .source-row {
          background: rgba(255,255,255,0.72);
          border: 1px solid rgba(19,19,19,0.10);
          border-radius: 24px;
          padding: 1rem 1.1rem;
          backdrop-filter: blur(10px);
          margin-bottom: 0.85rem;
          color: #151515 !important;
        }
        .hero-card *, .mini-card *, .source-row * { color: inherit !important; }
        .hero-card h2, .hero-card p { margin: 0; }
        .hero-card p { color: #5f5a52; margin-top: 0.65rem; line-height: 1.6; }
        .mini-card { min-height: 122px; }
        .mini-card strong { display: block; margin-bottom: 0.35rem; }
        .eyebrow, .source-label { color: #c75b39; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
        .pill { display: inline-block; margin: 0.15rem 0.35rem 0 0; padding: 0.3rem 0.7rem; border-radius: 999px; background: rgba(15,118,110,0.12); color: #0f766e; font-weight: 700; font-size: 0.82rem; }
        div[data-testid="stButton"] > button {
          min-height: 4.25rem;
          white-space: normal;
          line-height: 1.35;
          border-radius: 18px;
          border: 1px solid rgba(19,19,19,0.10);
          background: rgba(255,255,255,0.78);
          color: #151515 !important;
        }
        div[data-testid="stButton"] > button p,
        div[data-testid="stButton"] > button span {
          color: #151515 !important;
        }
        [data-testid="stChatMessage"],
        [data-testid="stChatMessage"] * {
          color: #151515 !important;
        }
        [data-testid="stExpander"],
        [data-testid="stExpander"] * {
          color: #151515 !important;
        }
        main [data-testid="stMarkdownContainer"] p,
        main [data-testid="stMarkdownContainer"] li,
        main [data-testid="stMarkdownContainer"] span,
        main [data-testid="stMarkdownContainer"] strong {
          color: #151515 !important;
        }
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] textarea::placeholder {
          color: #151515 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_source_pills(sources: list[str]) -> None:
    pills = "".join(f'<span class="pill">{source}</span>' for source in sources)
    st.markdown(f'<div class="source-row"><div class="source-label">Cited Sources</div>{pills}</div>', unsafe_allow_html=True)


def main() -> None:
    """Render the Streamlit experience."""
    st.set_page_config(page_title="VectixLogic Policy Intelligence", page_icon="📘", layout="wide")
    bootstrap_state()
    _inject_styles()

    st.markdown(
        """
        <div class="hero-card">
          <div class="eyebrow">VectixLogic Internal Search</div>
          <h2>Policy Intelligence, styled for the live demo.</h2>
          <p>Ask about PTO, security, pharmacy operations, remote work, expenses, or incident response.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, middle, right = st.columns(3, gap="medium")
    left.markdown('<div class="mini-card"><strong>Grounded answers</strong><br>Corpus-only responses with refusal guardrails.</div>', unsafe_allow_html=True)
    middle.markdown('<div class="mini-card"><strong>Source visibility</strong><br>Clean citations and supporting evidence when relevant.</div>', unsafe_allow_html=True)
    right.markdown('<div class="mini-card"><strong>Demo-ready view</strong><br>Warm grid canvas with a simpler, safer Streamlit layout.</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Demo Controls")
        k_value = st.slider("Retrieved chunks", min_value=2, max_value=8, value=4)
        st.info("Answers stay inside the indexed VectixLogic policy corpus.")
        st.caption("Best flow: remote work, PTO, security, then pharmacy operations.")

    for start in range(0, len(SAMPLE_QUESTIONS), 2):
        cols = st.columns(2, gap="medium")
        for column, prompt in zip(cols, SAMPLE_QUESTIONS[start : start + 2]):
            with column:
                if st.button(prompt, use_container_width=True):
                    st.session_state["queued_prompt"] = prompt

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                _render_source_pills(message["sources"])

    if st.session_state["latest_chunks"]:
        with st.expander("View supporting evidence"):
            for chunk in st.session_state["latest_chunks"]:
                st.markdown(f"**{chunk.get('source', 'Unknown source')}**")
                st.write(chunk.get("content", ""))

    prompt = st.session_state.pop("queued_prompt", None) or st.chat_input("Ask a policy question")
    if prompt:
        submit_query(prompt, k_value)
        st.rerun()


if __name__ == "__main__":
    main()

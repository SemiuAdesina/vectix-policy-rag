"""Rendering helpers for the Streamlit UI."""

from html import escape

import streamlit as st

from src.streamlit_assets import SAMPLE_QUESTIONS, load_streamlit_css


def inject_styles() -> None:
    """Apply the shared visual system used by the Streamlit app."""
    st.markdown(f"<style>{load_streamlit_css()}</style>", unsafe_allow_html=True)


def render_hero() -> None:
    """Render the landing section."""
    st.markdown(
        """
        <section class="hero-shell">
          <div class="eyebrow">VectixLogic Internal Search</div>
          <h1 class="hero-title">Policy Intelligence,<br>designed for live demos.</h1>
          <p class="hero-copy">
            Ask about PTO, security, pharmacy operations, remote work, expenses, or incident response.
            The app answers only from your policy corpus, keeps the response compact, and surfaces the
            retrieved evidence so the demo feels trustworthy instead of magical.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards() -> None:
    """Show quick value props under the hero."""
    cards = [
        ("Grounded answers", "Corpus only", "Guardrails keep answers anchored to the indexed company policies."),
        ("Source visibility", "Always cited", "Every response surfaces policy IDs and supporting snippets for the demo."),
        ("Deploy fit", "Render ready", "Single-screen layout tuned for polished screen-share walkthroughs."),
    ]
    for column, (label, value, copy) in zip(st.columns(3, gap="medium"), cards):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">{escape(label)}</div>
                  <div class="metric-value">{escape(value)}</div>
                  <div class="metric-copy">{escape(copy)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_sidebar(default_k: int) -> int:
    """Render sidebar controls and guidance."""
    with st.sidebar:
        st.markdown("### Demo Controls")
        k_value = st.slider("Retrieved chunks", min_value=2, max_value=8, value=default_k)
        _render_sidebar_card("Scope", "Answers should stay inside VectixLogic policies and procedures. If the corpus does not support the question, the app should refuse.")
        st.markdown("")
        _render_sidebar_card("Best Demo Flow", "Start with a remote work or PTO question, then jump to security or pharmacy operations so the evaluator sees breadth across the corpus.")
    return k_value


def render_prompt_bar() -> None:
    """Offer quick-launch prompt buttons."""
    st.markdown('<div class="section-kicker">Fast Start Prompts</div>', unsafe_allow_html=True)
    for column, prompt in zip(st.columns(len(SAMPLE_QUESTIONS), gap="small"), SAMPLE_QUESTIONS):
        with column:
            if st.button(prompt, use_container_width=True):
                st.session_state["queued_prompt"] = prompt


def render_history() -> None:
    """Render all chat messages in order."""
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                pills = "".join(f'<span class="source-pill">{escape(source)}</span>' for source in message["sources"])
                st.markdown(pills, unsafe_allow_html=True)


def render_sources_panel() -> None:
    """Render the evidence used for the latest answer."""
    chunks = st.session_state["latest_chunks"]
    if not chunks:
        return
    st.markdown('<div class="section-kicker">Retrieved Evidence</div>', unsafe_allow_html=True)
    for chunk in chunks:
        st.markdown(
            f"""
            <div class="snippet-card">
              <div class="snippet-source">{escape(chunk.get("source", "Unknown source"))}</div>
              <div class="snippet-body">{escape(chunk.get("content", "")).replace(chr(10), "<br>")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_sidebar_card(title: str, body: str) -> None:
    """Render one sidebar information card."""
    st.markdown(
        f"""
        <div class="status-card">
          <div class="status-title">{escape(title)}</div>
          <div class="status-body">{escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

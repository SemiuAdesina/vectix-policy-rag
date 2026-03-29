"""State and request helpers for the Streamlit UI."""

from typing import Any

import streamlit as st

from src.rag_app import get_engine


@st.cache_resource(show_spinner=False)
def load_engine() -> Any:
    """Cache engine construction for a smoother UI."""
    return get_engine()


def bootstrap_state() -> None:
    """Initialize session keys used by the app."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("latest_sources", [])
    st.session_state.setdefault("latest_chunks", [])
    st.session_state.setdefault("latest_query", "")


def submit_query(query: str, k_value: int) -> None:
    """Run the RAG pipeline and persist the new message pair."""
    clean_query = query.strip()
    if not clean_query:
        st.warning("Enter a policy question to continue.")
        return

    st.session_state["messages"].append({"role": "user", "content": clean_query})
    st.session_state["latest_query"] = clean_query
    with st.spinner("Searching the policy corpus..."):
        try:
            result = load_engine().ask(clean_query, k=k_value)
        except Exception as exc:  # pragma: no cover
            message = (
                "The interface loaded, but the RAG engine could not answer yet. "
                f"Check that dependencies, the vector store, and API keys are configured. Details: `{exc}`"
            )
            st.session_state["messages"].append({"role": "assistant", "content": message, "sources": []})
            st.session_state["latest_sources"] = []
            st.session_state["latest_chunks"] = []
            return

    st.session_state["messages"].append(
        {
            "role": "assistant",
            "content": result.get("answer", "No answer returned."),
            "sources": result.get("sources", []),
        }
    )
    st.session_state["latest_sources"] = result.get("sources", [])
    st.session_state["latest_chunks"] = result.get("chunks", [])

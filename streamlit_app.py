"""
Streamlit UI for VectixLogic Policy RAG.

Text input and display of answer plus source snippets. Requires a built
vector store (run scripts/build_store.py first) and optionally OPENAI_API_KEY.
"""

import streamlit as st

from src.rag_app import get_engine


st.set_page_config(page_title="VectixLogic Policy Q&A", layout="centered")
st.title("VectixLogic Policy Q&A")
st.caption("Ask about remote work, PTO, security, pharmacy compliance, and other policies.")

query = st.text_input("Your question", placeholder="e.g. What are the core hours for remote work?")
if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching policies..."):
            engine = get_engine()
            result = engine.ask(query.strip(), k=4)
        st.subheader("Answer")
        st.markdown(result.get("answer", ""))
        sources = result.get("sources", [])
        if sources:
            st.caption(f"**Sources:** {', '.join(sources)}")
        chunks = result.get("chunks", [])
        if chunks:
            with st.expander("Source snippets used"):
                for i, c in enumerate(chunks, 1):
                    src = c.get("source", "—")
                    st.markdown(f"**[{i}] {src}**")
                    st.text(c.get("content", "")[:500] + ("..." if len(c.get("content", "")) > 500 else ""))

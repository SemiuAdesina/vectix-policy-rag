# AI tooling

How AI assistants (Cursor, ChatGPT, Claude, Codex) were used to implement this codebase.

## Cursor

- **Rules:** `.cursorrules` enforces file length (≤150 LOC), logging, latency tracking, and dependency injection. The RAG engine, vector store, and ingestion were written to match these rules; Cursor was used to refactor and split modules when they grew.
- **Implementation:** Core modules (`ingestion.py`, `vector_store.py`, `rag_engine.py`, `rag_app.py`) were implemented or edited in Cursor with inline prompts (e.g. “add a latency decorator on ask()”, “return chunks with source for the UI”).
- **Tests:** Test files (`test_ingestion.py`, `test_vector_store.py`, `test_rag_engine.py`) were written in Cursor with AAA style and mock embeddings/LLM; Cursor was used to fix failing tests after dependency or signature changes.
- **Evaluation and UI:** The evaluation script (`run_evaluation.py`), Streamlit app (`streamlit_app.py`), FastAPI app (`api/main.py`), and build script (`scripts/build_store.py`) were added or updated in Cursor to wire a real store and LLM and to report groundedness, citation accuracy, and p50/p95.

## ChatGPT / Claude

- **Design choices:** Used for high-level design (e.g. why ChromaDB, chunk size vs overlap tradeoffs, how to score “citation accuracy” and “groundedness”).
- **Boilerplate:** FastAPI request/response models and Streamlit layout (title, text input, expandable snippets) were drafted in ChatGPT or Claude and then adapted in-repo (import paths, `get_engine()`, result keys).
- **Documentation:** README, design-and-evaluation.md, and this ai-tooling.md were outlined with an AI assistant and then edited to match the actual project (paths, commands, env vars).

## Codex

- **Repo recovery:** Used to restore missing project files from the last committed state while preserving newer source-level improvements already present in the workspace.
- **UI upgrade:** Used to redesign the Streamlit app into a stronger deployed experience and then add a browser-based chat interface at the FastAPI root so `/`, `/chat`, and `/health` are satisfied cleanly.
- **Polish pass:** Used to tighten build behavior, add deterministic seed handling, expand ingestion support beyond Markdown, add test coverage for Policy ID metadata extraction, and align the docs with the current deployed experience.

## Workflow

1. **Spec in repo:** Requirements (Phase 4/5, evaluation JSON, /health, /chat) were specified in the project or in conversation.
2. **Implement in Cursor:** Code and tests were written or modified in Cursor with reference to `.cursorrules` and the existing modules.
3. **Run locally:** `build_store.py` → `streamlit run streamlit_app.py` or `uvicorn api.main:app` → `run_evaluation.py` to validate.
4. **Docs:** Design and AI-tooling docs were written so evaluators can see the rationale and how tools were used.

## What worked / what did not

- **Worked well:** Rapid scaffolding of API models, RAG plumbing, UI structure, and documentation drafts.
- **Worked well:** Fast iteration on refactors, tests, and deployment-facing polish after the core app was already in place.
- **Did not work as well:** AI-generated evaluation heuristics and UI drafts still needed manual review to avoid unfair scoring and to better match the actual assignment requirements.

No proprietary or confidential policy text was pasted into external AI; only structure (e.g. “Policy ID”, “Appendix: Definitions”) and evaluation criteria were described in prompts.

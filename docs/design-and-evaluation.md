# Design and Evaluation

## Why ChromaDB

- **In-process and file-based:** Single `chroma_data/` directory; no separate server for development or small deployments.
- **LangChain integration:** `langchain_chroma.Chroma` provides a drop-in vector store with `similarity_search` and persistent collections.
- **Metadata support:** Policy ID and source path are stored per chunk so answers can cite VL-SEC-019, VL-HR-001, etc.
- **Suitable scale:** The corpus is ~20 policy Markdown files; Chroma handles this easily and keeps the stack simple (no Elasticsearch or Pinecone required for the assignment).

Alternatives considered: FAISS (no persistence by default), Pinecone/Weaviate (external services). Chroma was chosen for simplicity and local persistence.

---

## Chunking strategy

- **Splitter:** `MarkdownTextSplitter` (LangChain) so section structure (headers, lists) is respected where possible.
- **CHUNK_SIZE:** 1000 characters. Policies have short sections (e.g. definitions, scenario rows); 1000 keeps a few paragraphs or a table block together without excessive truncation.
- **CHUNK_OVERLAP:** 200 characters. Overlap reduces boundary effects when a key sentence (e.g. “CTO initiates failover”) sits at a chunk edge and improves retrieval for follow-up terms.
- **Metadata:** Each chunk keeps `source` (file path) from the loader; the ingestion/vector-store pipeline preserves or derives Policy ID (e.g. from filename or frontmatter) so `extract_sources()` can return Policy IDs for citations.

---

## Evaluation

Evaluation is run against **20 questions with gold answers** in `data/eval_20_gold.json`. The script:

1. Calls `engine.ask(question)` for each question.
2. **Groundedness:** Checks that the model’s answer contains the expected terms (from `expected_terms`). If all terms appear, the answer is considered grounded in the retrieved context.
3. **Citation accuracy:** Checks that the cited sources (or the answer text) include the expected Policy ID(s) from `policy_hint` (e.g. VL-SEC-013 or VL-SEC-019).
4. **Latency:** Each `ask()` is timed; after the run, p50 and p95 of these 20 calls are reported.

### How to run

```bash
# Build store first, then:
PYTHONPATH=. python scripts/run_evaluation.py
```

Output includes `groundedness_pct`, `citation_accuracy_pct`, `p50_ms`, `p95_ms`, and per-question details.

### Mock vs real mode

- **No OPENAI_API_KEY:** The app uses mock embeddings and a mock LLM. The vector store is filled with non-meaningful vectors, and answers are generic. You will see **0% groundedness and 0% citation**, and **p50/p95 in the sub-millisecond range** (mock calls only). Delete `chroma_data/` and rebuild once the key is set.
- **With OPENAI_API_KEY in `.env`:** Real OpenAI embeddings and Chat model are used. Rebuild the store with `scripts/build_store.py` (you should *not* see “No OPENAI_API_KEY”), then run evaluation. **Groundedness and citation** can reach target levels (e.g. ≥90%). **Latency** will be higher (typically **~1,000–3,000 ms** p50/p95) due to network calls to OpenAI; these are the numbers to record in the tables below.

Ensure `python-dotenv` is installed (`pip install -r requirements.txt`) so `.env` is loaded.

### Evaluation tables (fill with your run)

Run the evaluation and paste the output numbers here:

```bash
export OPENAI_API_KEY=sk-...   # if not in .env
PYTHONPATH=. python scripts/run_evaluation.py
```

Copy **Groundedness %**, **Citation accuracy %**, **p50_ms**, and **p95_ms** from the script output (or the printed JSON) into the tables below.

**Groundedness and citation (20 questions)**

| Metric                 | Target | Your run |
|------------------------|--------|----------|
| Groundedness %         | ≥ 90   | 80.0     |
| Citation accuracy %    | ≥ 90   | 80.0     |

**Latency (20 calls)**

| Percentile | ms    |
|------------|-------|
| p50        | 3017  |
| p95        | 4766  |

Gold answers in `data/eval_20_gold.json` are for manual or LLM-as-judge scoring if you want to compare model output to a reference answer in addition to the automated groundedness and citation checks.

# VectixLogic RAG Evaluation Guide

Use this guide **before running** ingestion and evaluation to ensure **groundedness** and **Score 5** alignment.

---

## 1. Scenario Coverage (Precision Testing)

### Purpose

Test the RAG's **precision** by asking about **specific scenarios** from the corpus. The model must retrieve the correct policy and cite the exact scenario (e.g., failover time, owner, mitigation), not generic advice.

### Where Scenarios Live

- **VL-SEC-019** (Business Continuity Plan v2): When this file is in `data/raw/`, it contains a **large scenario table** (24+ or 50 scenarios) with columns: Scenario, Likelihood, Impact, Owner, Failover / Mitigation. Use these for evaluation.
- **VL-SEC-013** (Emergency Protocols): Contains concrete scenarios (AWS region failure, UCH muster point, 6-hour backups, first Sunday restoration). Use as fallback or in addition.

### How to Use Before Running

1. **Include scenario-based questions in your evaluation set.** For example:
   - *"What is the failover time if the AWS primary region is unavailable, and who initiates it?"* (Expected: 15 minutes, CTO; cite VL-SEC-013 or VL-SEC-019.)
   - *"Where is the muster point if there is a fire at the UCH site?"* (Expected: main parking lot outside the Pharmacy Department; VL-SEC-013.)
   - If VL-SEC-019 is present: *"What should we do if the Solana RPC endpoint is unreachable?"* (Expected: switch to backup RPC provider; env var swap and redeploy; owner Blockchain Lead.)

2. **When you create your full evaluation questions later**, ensure at least **3–5 questions** target a **specific scenario** from the Business Continuity / Emergency tables (scenario name, owner, or mitigation step). This tests that the RAG retrieves the right row and does not hallucinate.

3. **Expected answer format:** Answers should cite **Policy ID** and, where applicable, the **exact scenario row** (e.g., "Per VL-SEC-013, the CTO initiates failover to the backup region within 15 minutes.").

---

## 2. Glossary Utilization (Exact Terminology)

### Purpose

Every policy file has an **Appendix: Definitions** section. The UI and the AI should **double-check** answers against these definitions so that the RAG uses **exact VectixLogic terminology** (e.g., "muster point," "failover," "RTO," "Quarantine Zone") and does not paraphrase into inconsistent terms.

### How to Use Before Running (UI / Pipeline)

1. **At answer-generation time (e.g., in your RAG chain or UI logic):**
   - After the model generates an answer from retrieved chunks, optionally **re-retrieve** chunks that contain **"Appendix: Definitions"** or **"Definitions"** for the same policy (or for all policies in the retrieved set).
   - **Validate** that key terms in the answer match the **exact wording** in the Appendix: Definitions table (e.g., "muster point" not "meeting point"; "Quarantine Zone" not "quarantine area").
   - If the model used a synonym or looser term, **replace or annotate** with the canonical term from the glossary (e.g., "Per VL-SEC-013, the **muster point** is the main parking lot outside the Pharmacy Department.").

2. **Prompt instruction for the LLM (recommended):**
   - Add to your system or user prompt: *"When answering, use the exact terminology from the policy documents, especially from any 'Appendix: Definitions' or 'Definitions' section in the retrieved context. Do not substitute synonyms for defined terms (e.g., use 'muster point' not 'assembly point')."*

3. **Evaluation:** Include at least **2–3 evaluation questions** that require a **defined term** as the answer (e.g., "What is the designated safe assembly location at UCH in an emergency?" → expected: "muster point" per VL-SEC-013 Appendix). This tests glossary grounding.

---

## 3. Checklist Before Running Ingestion / Evaluation

- [ ] **Scenario coverage:** Evaluation question set includes 3–5 questions that target a **specific scenario** from VL-SEC-013 or VL-SEC-019 (e.g., AWS failover, Solana RPC, muster point, backup frequency).
- [ ] **Glossary utilization:** Prompt or pipeline instructs the model to use **exact terminology** from Appendix: Definitions; 2–3 evaluation questions require a defined term in the answer.
- [ ] **Citation:** Evaluation rubric expects **Policy ID** (e.g., VL-SEC-013, VL-OPS-018) in answers where applicable.
- [ ] **Groundedness target:** Aim for **> 90%** groundedness (answers supported by retrieved chunks and definitions).

---

## 4. Example Evaluation Questions (Seed List)

A small seed list is in **`data/evaluation_questions.json`**. Use it to start your evaluation set; add more scenario-based and glossary-based questions as above.

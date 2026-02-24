# Ethics in AI Development

**Policy ID:** VL-AI-005  
**Effective Date:** January 1, 2026  
**Focus:** Peer-review rules for AI-generated code.  
**Version:** 2.0.1

## 1. Code Generation

Engineers are encouraged to use GitHub Copilot or Cursor. However, all AI-generated code must be peer-reviewed by a human developer before being merged into the `main` branch.

## 2. Bias Mitigation

When building agents for the Nigerian housing market (GIDA), developers must audit the training data to ensure no geographic or tribal bias is present in the recommendation algorithms.

## 3. Transparency

Users interacting with any Vectix Foundry agent must be clearly notified that they are communicating with an AI, not a human representative.

---

## 4. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2024-01-01 | CTO | Initial AI ethics policy. |
| 1.1.0 | 2024-04-01 | CTO | Copilot and Cursor permitted with peer review. |
| 1.2.0 | 2024-07-01 | CTO | main branch merge requirement. |
| 1.3.0 | 2024-10-01 | CTO | GIDA bias mitigation added. |
| 1.4.0 | 2025-01-01 | CTO | Transparency and user notification. |
| 1.5.0 | 2025-04-01 | CTO | Training data audit language. |
| 1.6.0 | 2025-07-01 | CTO | Geographic and tribal bias explicitly named. |
| 1.7.0 | 2025-10-01 | CTO | Vectix Foundry agent scope. |
| 2.0.0 | 2025-12-01 | CTO | Header standardized. |
| 2.0.1 | 2026-01-01 | CTO | Corpus release. |

---

## 5. Appendix: Definitions

| Term | Definition |
|------|------------|
| **AI-generated code** | Code produced with assistance of Copilot, Cursor, or similar tools; must be peer-reviewed. |
| **Peer review** | Review by at least one other human developer before merge to main. |
| **main branch** | Primary branch in version control; protected per VL-TECH-016. |
| **GitHub Copilot** | AI pair-programming tool; permitted under this policy. |
| **Cursor** | AI-assisted IDE; permitted under this policy. |
| **GIDA** | Nigerian housing / real estate platform; recommendation algorithms must be bias-audited. |
| **Bias** | Unfair skew (e.g., geographic, tribal) in data or algorithms; must be mitigated. |
| **Training data** | Data used to train or fine-tune models; must be audited for bias. |
| **Recommendation algorithms** | Systems that suggest or rank options (e.g., properties); subject to bias audit. |
| **Transparency** | Users must be informed they are interacting with AI, not a human. |
| **Vectix Foundry agent** | AI agent deployed on VectixLogic's platform; user-facing. |
| **Human representative** | Live person; distinction from AI must be clear to users. |
| **Merge** | Integrating code into main via pull request and approval. |
| **Geographic bias** | Unfair preference or disadvantage by location. |
| **Tribal bias** | Unfair preference or disadvantage by ethnic or tribal identity. |

---

## 6. Related Documents

- **VL-TECH-016:** Engineering Handbook (code quality, testing).
- **VL-OPS-012:** Client Communication (tone, SLAs).
- **VL-EXE-020:** Company Vision (ethics and product direction).

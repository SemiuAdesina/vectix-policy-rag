# VectixLogic Data Security & Privacy

**Policy ID:** VL-SEC-002  
**Effective Date:** January 1, 2026  
**Focus:** Solana key management and MFA requirements.  
**Version:** 2.0.1

## 1. Access Control

Access to the Vectix Foundry production environment requires Multi-Factor Authentication (MFA). API keys for Solana mainnet must be stored in encrypted environment variables and never committed to GitHub.

## 2. Health Data (HIPAA)

As VectixLogic develops pharmacy management software, all patient data must be encrypted at rest using AES-256. No personally identifiable information (PII) should be used in LLM training prompts.

## 3. Incident Reporting

Any suspected data breach must be reported to the CTO within 2 hours of discovery via the #security-alerts Slack channel.

---

## 4. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2023-09-01 | CTO | Initial security policy. |
| 1.1.0 | 2024-01-01 | CTO | MFA mandated for production. |
| 1.2.0 | 2024-06-01 | CTO | Solana API key handling added. |
| 1.3.0 | 2024-09-01 | CTO | HIPAA and AES-256 requirement. |
| 1.4.0 | 2025-01-01 | CTO | PII and LLM training prohibition. |
| 1.5.0 | 2025-04-01 | CTO | Incident reporting 2-hour SLA. |
| 1.6.0 | 2025-07-01 | CTO | #security-alerts channel designated. |
| 1.7.0 | 2025-10-01 | CTO | GitHub secret scanning referenced. |
| 2.0.0 | 2025-12-01 | CTO | Header standardized. |
| 2.0.1 | 2026-01-01 | CTO | Corpus release. |

---

## 5. Appendix: Definitions

| Term | Definition |
|------|------------|
| **MFA** | Multi-Factor Authentication; second factor (e.g., TOTP, hardware key) required for production access. |
| **Vectix Foundry** | VectixLogic's production platform for APIs, agents, and blockchain tooling. |
| **Solana mainnet** | Public Solana blockchain; API keys must not be committed to version control. |
| **API key** | Secret used to authenticate with external services; must be in encrypted env vars. |
| **GitHub** | Version control and CI/CD platform; no secrets in repos. |
| **HIPAA** | Health Insurance Portability and Accountability Act; US regulation for health data. |
| **AES-256** | Encryption standard for data at rest; required for patient data. |
| **PII** | Personally Identifiable Information; must not be used in LLM training prompts. |
| **LLM** | Large Language Model; training or fine-tuning must not use PII. |
| **Data breach** | Unauthorized access, disclosure, or loss of confidential or personal data. |
| **CTO** | Chief Technology Officer; recipient of security incident reports. |
| **#security-alerts** | Slack channel for reporting and coordinating security incidents. |
| **Encrypted environment variables** | Secrets stored in a secrets manager or env config, not in code. |
| **Production environment** | Live systems serving customers; requires MFA for access. |
| **Incident reporting** | Process of notifying CTO within 2 hours of suspected breach. |

---

## 6. Related Documents

- **VL-OPS-003:** Pharmacy inventory and data handling in operational context.
- **VL-SEC-013:** Emergency protocols and disaster recovery.
- **VL-EXE-020:** Company Vision (security as core value).

# VectixLogic Pharmacy Operations Manual — Drug Supply Chain Security

**Policy ID:** VL-OPS-018  
**Effective Date:** January 1, 2026  
**Focus:** Drug Supply Chain Security Act (DSCSA) and traceability.  
**Version:** 2.0.1

---

## 1. Purpose and Scope

This manual defines how VectixLogic pharmacy inventory systems comply with the Drug Supply Chain Security Act (DSCSA) in the United States and with equivalent traceability and serialization expectations for clients in Nigeria (e.g., NAFDAC, PCN). It applies to all modules that handle prescription drug receipt, storage, dispense, return, or destruction.

---

## 2. DSCSA Overview (United States)

The DSCSA (Title II of the Drug Quality and Security Act, 2013) establishes federal requirements for tracing prescription drugs through the supply chain. Key obligations for dispensers (pharmacies) and for software that supports them include:

- **Product identification:** Transaction Information (TI), Transaction History (TH), and Transaction Statement (TS) must be captured and maintained for each change of ownership.
- **Serialization:** At the package level, serialized product identifiers (e.g., NDC, serial number, lot, expiry) must be verified and recorded where required by the phased implementation.
- **Suspect and illegitimate product:** Procedures to quarantine, investigate, and report suspect or illegitimate product; no distribution until cleared.
- **Record retention:** TI, TH, and TS records must be retained for not less than six years.

VectixLogic systems used by US-based pharmacy clients must support capture and storage of TI/TH/TS and, where applicable, verification of serialized identifiers per the current FDA implementation timeline.

---

## 3. Transaction Information (TI), History (TH), and Statement (TS)

### 3.1 Transaction Information (TI)

TI includes, at a minimum:

- Proprietary or established name of the product; strength and dosage form; NDC (or equivalent); container size; number of containers; lot number; transaction date; date of the transaction.
- For serialized product, the serial number or other unique identifier as required by FDA.

Our pharmacy inventory module must record TI for every receipt (purchase from wholesaler or manufacturer) and every dispense or transfer out. TI is stored in the audit log and in the transaction table with a unique transaction ID and timestamp.

### 3.2 Transaction History (TH)

TH is a cumulative record of all TI for a product (or serialized package) as it moves through the supply chain. VectixLogic maintains TH by linking each incoming transaction to the prior owner’s TH (when provided) and appending the current transaction. TH is retained for the statutory period and is available for FDA inspection or for passing to the next owner upon sale or transfer.

### 3.3 Transaction Statement (TS)

TS is a statement by the seller that it is authorized under the DSCSA, that it received the product from an authorized trading partner, that it did not knowingly ship suspect or illegitimate product, and that it will not ship product that it knows to be suspect or illegitimate. Our system stores the TS (or a reference to it) with each received transaction and can generate a TS for outbound transactions (e.g., returns to wholesaler) when the client performs such transactions.

---

## 4. Serialization and Verification

Where the FDA requires product verification at the package level (e.g., prior to dispense), the system must:

- Accept and store serialized product identifiers (e.g., 2D barcode scan or manual entry of NDC + serial + lot + expiry).
- Verify the identifier against the received TI/TH and flag mismatches (e.g., wrong lot, expired, or not in system) so that the product can be quarantined and investigated.
- Record the verification event (pass/fail, user, timestamp) in the audit log.

For products not yet subject to serialization requirements, the system still records NDC, lot, and expiry for each receipt and dispense to support traceability and recall.

---

## 5. Suspect and Illegitimate Product

### 5.1 Definitions (per DSCSA)

- **Suspect product:** Product that may be counterfeit, diverted, stolen, adulterated, unfit for distribution, or otherwise illegitimate.
- **Illegitimate product:** Product that has been determined to be counterfeit, diverted, stolen, adulterated, unfit for distribution, or otherwise illegitimate.

### 5.2 Procedures in VectixLogic Systems

- **Quarantine:** Any product flagged as suspect (e.g., failed verification, damaged packaging, or alert from trading partner) must be moved to a Quarantine Zone in the system and must not be dispensed or transferred until cleared.
- **Investigation:** The responsible pharmacist or designee documents the investigation (reason, steps taken, outcome) in the system. Records are retained per DSCSA.
- **Disposition:** If product is cleared, it is moved back to active stock. If illegitimate, it must be disposed of in accordance with law and not returned to the supply chain; the system records disposition and, where required, supports reporting to FDA and trading partners.
- **No sale/distribution:** The system enforces that quarantined and illegitimate product cannot be dispensed or shipped.

---

## 6. Integration with Wholesalers and Manufacturers

For US clients, VectixLogic systems may integrate with wholesalers or manufacturers via EDI, API, or file exchange to:

- Receive TI/TH/TS electronically upon purchase and auto-populate transaction records.
- Send TI/TH/TS (and TS statements) when returning product for credit or other lawful transfer.
- Receive and display alerts related to suspect or recalled product so that sites can quarantine and act promptly.

Integration specifications (e.g., ASN, 856, or partner-specific formats) are documented in the technical integration guide for each trading partner.

---

## 7. Nigeria: NAFDAC and PCN Alignment

For Nigerian pharmacy clients (e.g., UCH and other partners), the system supports:

- **NAFDAC registration and product identification:** NAFDAC number and product details are captured for received and dispensed products where required. This supports both local regulation and any future serialization or traceability requirements.
- **PCN record-keeping:** Electronic records are retained for at least 5 years per PCN standards (see VL-COMP-011). Audit logs and transaction records are exportable for inspections.
- **Return for Credit (RFC):** When returning expired or short-dated product to manufacturers, the system generates documentation (e.g., batch, NAFDAC, quantities) that aligns with manufacturer and regulatory expectations; see the pharmacy inventory case studies document for RFC troubleshooting.

---

## 8. Record Retention and Audits

- **US (DSCSA):** TI, TH, TS, and verification records are retained for not less than six years. Data is stored in a manner that allows retrieval by product, transaction ID, and date range for FDA inspection.
- **Nigeria:** Minimum 5 years per PCN; NAFDAC-related records per local requirements.
- **Audits:** VectixLogic undergoes an independent security and compliance audit annually (VL-COMP-011). Internal reviews of DSCSA and NAFDAC/PCN compliance are performed quarterly for US and Nigerian deployments.

---

## 9. Summary

| Area | Requirement |
|------|-------------|
| TI/TH/TS | Capture and retain for every relevant transaction; support pass-through and generation of TS |
| Serialization | Support package-level identifier capture and verification where required by FDA |
| Suspect/illegitimate | Quarantine, investigate, document; no dispense or distribution until cleared |
| Retention (US) | ≥ 6 years for DSCSA records |
| Retention (Nigeria) | ≥ 5 years per PCN |
| Integration | Support electronic TI/TH/TS with trading partners where applicable |

---

## 10. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2024-06-01 | Compliance | Initial DSCSA manual. |
| 1.1.0 | 2024-09-01 | Compliance | TI/TH/TS capture and retention. |
| 1.2.0 | 2024-12-01 | Compliance | Serialization and verification. |
| 1.3.0 | 2025-03-01 | Compliance | Suspect and illegitimate procedures. |
| 1.4.0 | 2025-06-01 | Compliance | Nigeria NAFDAC and PCN alignment. |
| 1.5.0 | 2025-09-01 | Compliance | Integration with wholesalers. |
| 1.6.0 | 2025-12-01 | Compliance | 6-year US retention, 5-year Nigeria. |
| 1.7.0 | 2025-12-15 | Compliance | Cross-reference VL-OPS-018-CS. |
| 2.0.0 | 2025-12-01 | Compliance | Header standardized. |
| 2.0.1 | 2026-01-01 | Compliance | Corpus release. |

---

## 11. Appendix: Definitions

| Term | Definition |
|------|------------|
| **DSCSA** | Drug Supply Chain Security Act (US); traceability and serialization for prescription drugs. |
| **TI** | Transaction Information; required data elements for each transaction. |
| **TH** | Transaction History; cumulative chain of TI for a product. |
| **TS** | Transaction Statement; seller's attestation per DSCSA. |
| **NDC** | National Drug Code (US) or equivalent product identifier. |
| **Serialization** | Package-level unique identifier (e.g., serial number) for verification. |
| **Suspect product** | Product that may be counterfeit, diverted, adulterated, or otherwise illegitimate. |
| **Illegitimate product** | Product determined to be counterfeit, diverted, or unfit; must not be distributed. |
| **Quarantine Zone** | System state for suspect/illegitimate product; no dispense until cleared. |
| **NAFDAC** | National Agency for Food and Drug Administration and Control (Nigeria). |
| **PCN** | Pharmacists Council of Nigeria; see VL-COMP-011. |
| **Trading partner** | Authorized manufacturer, wholesaler, or dispenser in the supply chain. |
| **RFC** | Return for Credit; see VL-OPS-003, VL-OPS-018-CS. |
| **EDI** | Electronic Data Interchange; format for TI/TH/TS exchange. |
| **Verification** | Checking serialized identifier against TI/TH; pass/fail logged. |

---

## 12. Related Documents

- **VL-OPS-003:** Expired Drug Inventory Management (quarantine, RFC).
- **VL-OPS-018-CS:** Pharmacy Inventory Case Studies (RFC troubleshooting).
- **VL-COMP-011:** Regulatory Compliance (PCN, FDA, audit).
- **VL-EXE-020:** Company Vision (compliance by design).

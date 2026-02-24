# Business Continuity & Emergency Plan

**Policy ID:** VL-SEC-013  
**Effective Date:** January 1, 2026  
**Focus:** Disaster recovery for AWS and physical safety.  
**Version:** 2.0.1

## 1. System Outage

In the event of an AWS region failure, the CTO will initiate the disaster recovery protocol to failover to the backup region within 15 minutes.

## 2. Physical Safety (Ibadan Office)

In case of fire or structural emergency at the UCH site, the muster point is the main parking lot outside the Pharmacy Department.

## 3. Data Loss

Backups are performed every 6 hours. Restoration is tested monthly on the first Sunday.

---

## 4. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2023-09-01 | CTO | Initial emergency plan. |
| 1.1.0 | 2024-01-01 | CTO | AWS failover 15 minutes. |
| 1.2.0 | 2024-04-01 | CTO | UCH muster point. |
| 1.3.0 | 2024-07-01 | CTO | 6-hour backup frequency. |
| 1.4.0 | 2024-10-01 | CTO | Monthly restoration test. |
| 1.5.0 | 2025-01-01 | CTO | First Sunday test date. |
| 1.6.0 | 2025-04-01 | CTO | Physical safety (Ibadan). |
| 1.7.0 | 2025-07-01 | CTO | Data loss and restoration. |
| 2.0.0 | 2025-12-01 | CTO | Header standardized. |
| 2.0.1 | 2026-01-01 | CTO | Corpus release. |

---

## 5. Appendix: Definitions

| Term | Definition |
|------|------------|
| **AWS region failure** | Extended outage of an Amazon Web Services region; triggers failover. |
| **Failover** | Switching to backup region or system to restore service. |
| **15 minutes** | Target time to complete failover to backup region. |
| **Disaster recovery** | Process and technology to restore operations after an incident. |
| **Muster point** | Designated safe assembly location (e.g., UCH parking lot). |
| **UCH** | University College Hospital, Ibadan. |
| **Pharmacy Department** | Area at UCH; muster point is outside, main parking lot. |
| **Backups** | Copies of data and config taken on a schedule (every 6 hours). |
| **6 hours** | Frequency of backup runs. |
| **Restoration** | Process of restoring data/systems from backup. |
| **First Sunday** | Day of month when restoration is tested (monthly). |
| **CTO** | Chief Technology Officer; initiates DR protocol. |
| **Physical safety** | Fire, structural emergency; evacuate to muster point. |
| **Data loss** | Loss of data due to failure or corruption; mitigated by backups. |
| **Backup region** | AWS region used when primary region is unavailable. |

---

## 6. Related Documents

- **VL-SEC-019:** Business Continuity v2 (full risk assessment).
- **VL-OPS-012:** Client Communication (1-hour critical response).
- **VL-EXE-020:** Company Vision (resilience).

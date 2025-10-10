# ASR Copilot Status Pack (2024-03-22)

**Overall RAG:** At Risk  
**Data Health Score:** 92/100 (Strong)

## Executive Summary
- SPI 0.428 and CPI 0.732 flag schedule and cost pressure against the 2024-03-22 baseline.
- Data Health pinpoints three tasks missing updated effort plus one blocked workstream; chase drafts are ready for HITL approval.
- FCC shot clocks show 16 days left on the collocation window and 76 days on the 150-day new site clock.
- Top risks remain vendor slippage, OSS regressions, and transport window overrun—all with standing mitigations.
- Safe Mode is ON; outputs remain deterministic and auditable (Markdown + charts only).

## Data Health Score
- Completeness: 3 issue(s), Freshness: 3 issue(s), Consistency: 1 issue(s)
  - Completeness: 38/40 – Vendor interoperability lab has no updated effort even though work started 2024-02-12.
  - Freshness: 22/25 – Vendor interoperability lab has not been updated since the planned start on 2024-02-12.
  - Consistency: 22/25 – Workstream B: RAN upgrade clusters (Vendor B) is blocked; mitigation needs logging.
  - Conformance: 10/10 – No gaps detected.

## Earned Value Metrics
| Metric | Value |
| ------ | ----- |
| PV | 760.00 |
| EV | 325.00 |
| AC | 444.00 |
| SV | -435.00 |
| CV | -119.00 |
| SPI | 0.428 |
| CPI | 0.732 |
| EAC | 1885.26 |
| ETC | 1441.26 |

## Telco Compliance Signals
| Clock | Deadline | Days Remaining | Status | Description |
| ----- | -------- | -------------- | ------ | ----------- |
| FCC Shot Clock – 90 days (collocation) | 2024-04-07 | 16 | Amber | Track collocation modifications under the 90-day FCC requirement. |
| FCC Shot Clock – 150 days (new site) | 2024-06-06 | 76 | Green | New site builds must close out permitting within 150 days or risk timelines slipping. |

### Permitting Checklist
| Item | Status | Owner | Next Action |
| ---- | ------ | ----- | ----------- |
| NEPA / Section 106 correspondence logged | Pending | Permitting Lead | Upload the latest SHPO/THPO correspondence to keep audit trails tight. |
| 6409(a) eligibility documented | Pending | Regulatory Counsel | Confirm eligible facilities memo is filed to maintain expedited handling. |
| Structural calculations attached | Missing | Engineering | Drop structural calcs and stamped drawings for the construction packet. |
| Power service / inspection scheduled | Missing | Field Operations | Coordinate with the utility to secure inspection and power turn-up dates. |

## Top Risks
| ID | Risk | Severity | Due | Owner | Mitigation |
| -- | ---- | -------- | --- | ----- | ---------- |
| R-201 | Vendor B radio units arriving 3 weeks late | 2.75 (High) | 2024-03-04 | Priya Raman | Escalate to vendor exec sponsor; pull ahead buffer stock via contingency PO. |
| R-203 | OSS API regression delays automation | 1.60 (Medium) | 2024-03-18 | Jerry Wu | Expand automated tests and add shadow environment smoke runs. |
| R-202 | Transport swap maintenance window overrun | 1.40 (Low) | 2024-02-27 | Noah Bennett | Stage rollback plan and pre-approve overtime with NOC. |
| R-205 | Change advisory board rejects migration plan | 1.00 (Low) | 2024-04-22 | Leah Chen | Pre-brief CAB reviewers and align on risk mitigations one sprint earlier. |
| R-204 | Edge integration lab capacity constraints | 0.90 (Low) | 2024-03-11 | Zara Hayes | Increase shared lab hours; schedule overnight lab access with vendors. |

## What Changed Since Last Snapshot
No changes detected.

## Chase Queue (Preview)
| Gap | Owner | Channel | Priority | Message |
| --- | ----- | ------- | -------- | ------- |
| Missing updated estimate for Vendor interoperability lab | Marco Lee | Teams | Medium | Hi Marco, the task “Vendor interoperability lab” still shows zero actual hours even though it kicked off on 2024-02-12. Can you drop an updated estimate or actual by end of day so we can clear the completeness flag and keep the Data Health Score in the green? |
| Missing updated estimate for Edge core integration gate | Ana Gomez | Teams | Medium | Hi Ana, the task “Edge core integration gate” still shows zero actual hours even though it kicked off on 2024-02-26. Can you drop an updated estimate or actual by end of day so we can clear the completeness flag and keep the Data Health Score in the green? |
| Missing updated estimate for Service automation hardening (API) | Jerry Wu | Teams | Medium | Hi Jerry, the task “Service automation hardening (API)” still shows zero actual hours even though it kicked off on 2024-03-04. Can you drop an updated estimate or actual by end of day so we can clear the completeness flag and keep the Data Health Score in the green? |
| Blocked task needs mitigation update: Workstream B: RAN upgrade clusters (Vendor B) | Priya Raman | Email | High | Heads-up Priya — “Workstream B: RAN upgrade clusters (Vendor B)” is still marked blocked. Can you add the mitigation or next action in Jira so everyone sees how we’re clearing it? |

## ROI Snapshot
- Annual savings estimate: $35,280.00
- Monthly savings estimate: $2,940.00
- Annual hours reclaimed: 360.0

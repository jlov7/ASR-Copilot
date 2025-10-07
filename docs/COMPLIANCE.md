# Compliance & Responsible AI Alignment

## NIST AI RMF Mapping
| Core Function | Alignment |
| ------------- | --------- |
| Govern | Documented governance artifacts (PRD, PLAN, SECURITY). Roles/responsibilities outlined in `docs/AGENTS.md`. Safe Mode default ensures conservative posture. |
| Map | Dataset schemas documented; assumptions recorded in PRD. Local cache scope identified; data lineage captured via dataset hash in exports. |
| Measure | EVALS plan defines accuracy, regression, latency, and cost metrics. pytest/CI instrumentation supports continuous measurement. |
| Manage | Risk controls enumerated (threat model, adapter guardrails). ROI view surfaces operational impact; compliance checklist ensures consistent reviews. |

## Responsible AI Controls
- **Transparency**: All analytics rely on deterministic formulas with docstrings; UI displays calculation tooltips and references.
- **Explainability**: Status Pack includes textual justification for RAG assessments, risk scores, and ROI calculations.
- **Human Oversight**: Outputs presented as recommendations; PM must confirm before distribution. Export flow reminds user to review content.
- **Data Minimization**: Only necessary fields ingested; no persistent identifiers stored beyond local session.
- **Bias & Fairness**: No personal attributes processed; risk scoring purely operational.

## Regulatory Considerations
- **Data Residency**: Local execution keeps data on user's machine; note requirement when deploying to cloud.
- **Privacy (GDPR/CCPA)**: Users control uploaded data; provide purge capability and ensure exports contain only relevant information.
- **Auditability**: Logs include request IDs; exports embed dataset metadata to support review.

## Oversight Checklist (Per Release)
- ☐ Verify Safe Mode defaulted and documented.
- ☐ Review adapter code for read-only operations.
- ☐ Confirm `.env` instructions align with security posture.
- ☐ Run EVALS suite and archive results.
- ☐ Update CHANGELOG with compliance-relevant changes.

## Open Compliance Questions
- Formalize DPA/SLA templates for enterprise pilots.
- Determine long-term storage policy for generated exports.
- Assess accessibility compliance through third-party audit before GA.


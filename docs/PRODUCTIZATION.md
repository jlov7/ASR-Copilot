# From Prototype to Enterprise

## 0. Principles
- **Deterministic first** (templates, math, traceable fields).
- **Human-in-the-loop** for any stakeholder-facing send or write-backs.
- **Minimal footprint**: adapters are stateless, auditable, and easily swapped.

## 1. Governance & Risk (NIST AI RMF aligned)
- **Govern**: Roles, approvals, audit trails, data retention.
- **Map**: Intended use and limits (no automated reassignments, no silent write-back).
- **Measure**: Test harnesses for adapters, EVM math parity tests, “golden” report snapshots.
- **Manage**: Incident playbooks, model/version registry (even for deterministic logic).
> See `/docs/EVALUATION_CHECKLIST.md` for the full control list and evidence.

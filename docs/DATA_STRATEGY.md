# Data Strategy: From Messy Inputs to Trustworthy Outputs

## Goals
- Make data quality visible (and fixable) via a transparent **Data Health Score**.
- Normalize multi-source PM data to a **Canonical Project Data Contract**.
- Close gaps with a **Chase Queue** that drafts targeted requests to owners.

## Canonical Contract (v0.3)
- Project(id, name, sponsor, methodology, health, start, end, budget, currency)
- Milestone(id, project_id, name, due_date, status)
- Task(id, milestone_id, assignee, status, estimate, actuals, blocked_by[])
- Risk(id, project_id, title, probability, impact, owner, mitigation, status)
- Issue(id, project_id, title, severity, owner, next_step, target_date, status)
- Decision(id, project_id, title, decided_on, approver, link)
- BudgetSnapshot(project_id, as_of, pv, ev, ac, eac, variance)
- Dependency(id, from_project, to_project, type, criticality, status)

## Adapters
- Each source (Jira/Planview/ServiceNow/Smartsheet/CSV) maps to the contract via small, testable mappers (see `/adapters/*`). Enums are normalized (e.g., "Doing/Active" → `in_progress`).
- **Safe Mode** defaults to `mock` adapters for demos; live tokens are ignored unless explicitly enabled.

## Data Health Score
- **Completeness** (required fields present): 0–40 pts
- **Freshness** (days since last update per object type): 0–25 pts
- **Consistency** (status vs dates, SPI/CPI sanity): 0–25 pts
- **Conformance** (schema/enums valid): 0–10 pts
- Score gates “one-click export” and is shown atop every dashboard.

## Telco Siting & Permitting (example signals)
- Missing **NEPA/Section 106** docs or **SHPO/THPO** correspondence → risk & shot-clock warnings.
- 6409(a) eligibility checks and **FCC shot clocks (90/150 days)** surfaced as milestones with alerts. [Checklist]
> See `/docs/TELCO_COMPLIANCE.md` for the ready-made checklist-to-signal mapping.

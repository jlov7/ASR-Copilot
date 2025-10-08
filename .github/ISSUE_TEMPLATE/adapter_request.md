---
name: Adapter request
about: Propose a new integration or live data source
title: ""
labels: adapter
---

**Target system**
(Jira portfolio, ServiceNow table, Slack workspace, etc.)

**Use case**
(What automation loop step benefits from this adapter? Ingestion / Analytics / Narrative / Export)

**Access pattern**
- Read-only endpoints required:
- Expected payload shape:
- Frequency (manual, scheduled, autopilot):

**Guardrails & Safe Mode**
(Secrets, rate limits, approval steps. Reference docs/SECURITY.md if changes are needed.)

**Acceptance criteria**
- [ ] Local mock adapter parity
- [ ] Live adapter behind Safe Mode toggle
- [ ] Tests updated (`pytest -m live` when applicable)
- [ ] Documentation updated (README, docs/EXTENDING.md)

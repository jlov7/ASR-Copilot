# Pilot Playbook – Assist → Orchestrate → Autopilot

This playbook makes it clear how ASR Copilot graduates from a deterministic proof-of-concept to an enterprise-capable copilot. Each rung adds scope, telemetry, and guardrails while keeping program managers accountable for outcomes.

## Phase 1 – Assist (Weeks 0–4)
- **Scope:** Guided Mode only, bundled sample datasets, Safe Mode locked on.
- **Objectives:** Confirm narrative resonance, validate RAG/EVM explanations with PMO and finance leads.
- **Guardrails:** No API credentials, exports reviewed manually, golden snapshot test (`pytest -k golden`) runs before every demo.
- **Exit criteria:** 3+ executive demos delivered, qualitative feedback captured in `docs/CHANGELOG.md`, ROI presets tuned for the target portfolio.

## Phase 2 – Orchestrate (Weeks 5–8)
- **Scope:** Read-only adapters (Jira/Slack) enabled for two pilot programs; nightly ingest via scheduled dry-run.
- **Objectives:** Prove live data safety, measure hours saved vs. baseline, capture mitigation accuracy vs. human updates.
- **Guardrails:** Safe Mode toggled per environment, credentials stored in platform secret manager, adapter sanity checks logged.
- **Exit criteria:** Change board approves read-only integrations, latency/error metrics captured, PMO sign-off on automation loop observability.

## Phase 3 – Autopilot (Weeks 9–12)
- **Scope:** Scheduled exports to staging Slack/SharePoint channels with human approval; multi-program roll-out.
- **Objectives:** Reduce manual formatting, keep exec packs deterministic, track variance between golden run and live datasets.
- **Guardrails:** Approval workflow enforced before outward sharing, anomaly detection on CPI/SPI deltas, full audit log retention.
- **Exit criteria:** ≤5% deviation between golden run and live nightly exports, exec-pack distribution automated with PMO approval, production readiness review passed.

## Roll-forward checklist
- [ ] Hosted demo (`render.yaml`) stood up with Safe Mode enforced.
- [ ] Golden snapshot updated after any analytics change; diffs reviewed.
- [ ] CI pipeline green (backend pytest, frontend build) before enabling live adapters.
- [ ] Security review logged in `docs/SECURITY.md` with data handling notes.
- [ ] Deployment runbook appended to `docs/PLAN.md` with owner, RACI, and cutover timeline.


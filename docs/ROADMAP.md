# Enterprise Roadmap

ASR Copilot already delivers Assist-level autonomy in Safe Mode. This roadmap frames the next gates for stakeholders evaluating production rollout.

## Gate 1 – Assist (today)

- Deterministic ingestion of CSV/Markdown artifacts (backlog, risk register, status notes, EVM baseline).
- Analytics: CPI/SPI, Top 5 risks, deterministic change detection, ROI estimator.
- Narrative synthesis with guardrails and Safe Mode default (no outbound calls).
- Local-first storage, reproducible exports, typed API contracts, prebuilt demo data.

**Outcomes:** Weekly status prep drops from 8–12 hours to minutes. PMs reclaim time while execs trust the evidence trail.

## Gate 2 – Orchestrate (pilot)

- Scheduled runs with dry-run simulator and Safe Mode overrides per adapter.
- Read-only adapters for Jira, Slack, ServiceNow, Confluence, and data warehouses.
- Tenant-aware storage, access control (RBAC), and observability instrumentation (OpenTelemetry).
- Audit dashboards that show Automation Loop health, adapter telemetry, and export lineage.

**Outcomes:** Multi-program PMOs automate data refreshes safely, track coverage, and measure leading indicators (risks surfaced pre-sprint boundary).

## Gate 3 – Autopilot (future)

- Change-proposal workflows with approvals embedded in Jira/ServiceNow.
- Write-back adapters gated by policy, redaction, and SOC2-style logging.
- Forecasting extensions (Monte Carlo, confidence bands) with human-in-the-loop overrides.
- Program portfolio view with API hooks for financial systems.

**Outcomes:** Status packs go from “assistive prep” to “hands-off autopilot,” freeing entire PMO headcount for strategic initiatives.

## Metrics to watch

- Minutes saved per weekly status cycle.
- % of risks surfaced before the sprint boundary.
- % of status packs generated without manual edits.
- Adapter coverage (mock vs. live) and Safe Mode dwell time.

# ASR Copilot – Product Requirements Document

## Overview
ASR Copilot (Autonomy–Status–Risk Copilot) streamlines enterprise TMT/Telco program management by automating data ingestion, earned value analytics, risk storytelling, and executive reporting. The MVP ships as a local-first demo with no external integrations required, while preserving clear adapter plug-points for Jira, Slack, and ServiceNow.

## Problem Statement
Program managers spend disproportionate time (8–12 hours weekly) aggregating status inputs, computing EVM, and formatting updates. Manual workflows are error-prone, lack early warning signals, and delay executive decisions. Distributed teams further complicate risk traceability and ROI justification for automation investments.

## Personas
- **Delivery Program Manager (Primary)**: Needs real-time CPI/SPI deltas, top risks, and “what changed” narratives to drive stand-ups and steer partners.
- **PMO Lead (Secondary)**: Oversees multiple programs, wants portfolio-ready exports, consistent RAG logic, and audit trails for risk mitigations.
- **Executive Sponsor (Tertiary)**: Consumes executive one-pagers, demands forecast confidence, and inspects ROI claims when funding tooling.

## Goals
1. Deliver a zero-credential “no-integration” workflow that ingests CSV/MD artifacts and produces an executive-ready status pack in minutes.
2. Surface actionable analytics: CPI/SPI, risk severity × imminence, and schedule risk thresholds.
3. Provide rationalization evidence through an ROI calculator tied to PM task automation.
4. Maintain enterprise-grade guardrails: Safe Mode, deterministic summaries, and documented compliance hooks.

## Non-goals (MVP)
- Bi-directional sync or write-backs to Jira/Slack/ServiceNow.
- Portfolio aggregation across multiple programs (single program focus).
- Real-time streaming updates (batch uploads only).
- Predictive resource leveling or cost management beyond EVM metrics.

## Scope
### In-Scope
- CSV/Markdown ingestion for backlog tasks, risks, status notes, and EVM baseline.
- FastAPI backend with persisted local cache, Pydantic schemas, ROI persistence.
- React SPA with onboarding tour, dashboard, risk heatmap, ROI view, export controls.
- Mock adapters for Jira/Slack/ServiceNow with Safe Mode defaulting to mock.
- Status Pack exporter (Markdown + PNG charts) to `/out/` directory.

### Out-of-Scope
- Authentication, SSO, or RBAC.
- Multi-team collaboration features (comments, shared sessions).
- Advanced AI reasoning beyond deterministic summarization templates.

## Assumptions
- Enterprise programs can export required CSV/MD artifacts in provided schema without customization.
- Users run the POC on macOS/Linux with Python 3.10 and Node 18 available.
- Network connectivity may be restricted; all mock functionality must work offline.
- Exec stakeholders accept generated Markdown/PNG artifacts for demos.

## Success Metrics
- **Efficiency**: Reduce weekly status-prep effort by ≥60% (self-reported time saved via ROI view).
- **Adoption**: ≥3 successful demo runs (Status Pack generated) per pilot PMO.
- **Accuracy**: CPI/SPI calculations within ±2% of manual baseline for sample data.
- **Reliability**: 0 critical errors during demo script (run_demo.sh) in internal QA.

## Privacy & Safety Constraints
- Safe Mode on by default to prevent outbound API calls.
- No storage of uploaded artifacts beyond local cache; optional purge endpoint.
- Deterministic summarization templates (no LLM calls) to avoid leaking context.
- Logs redact environment variables and tokens; `.env.example` documents required vars.

## Acceptance Criteria
- `bash app/scripts/run_demo.sh` starts backend + frontend, loads sample data, and generates `/out/status_pack_<timestamp>.md`.
- Frontend renders onboarding tour, empty states, skeleton loaders, error recovery banners, ROI view, and risk heatmap.
- `pytest` passes on first run.
- README provides a 3-minute demo script that non-PM users can follow end-to-end.
- Status Pack includes RAG summary, EVM metrics, Top risks, and “what changed since yesterday.”

## Open Questions (Deferred)
- How to prioritize multi-program rollups for PMO leads.
- Whether to integrate with enterprise identity providers.
- Approach for continuous data sync versus batch uploads.

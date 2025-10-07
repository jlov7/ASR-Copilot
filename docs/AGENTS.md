# Agent Roles & Guardrails

Although the MVP operates deterministically, we define agent abstractions to support future autonomous workflows.

## Agent Directory
- **IngestionAgent**
  - Purpose: Validate and normalize uploaded CSV/MD artifacts.
  - Tools: CSV parser, Markdown diff engine.
  - Triggers: File upload event, "Load sample data" CTA.
  - Guardrails: Reject files with missing required columns; log validation report to diagnostics endpoint.
- **AnalyticsAgent**
  - Purpose: Compute EVM metrics, risk scores, ROI projections.
  - Tools: `app/core/evm`, `app/core/risk_scoring`, `app/core/roi` modules.
  - Triggers: Data ingestion success, scheduled re-computation (manual trigger for now).
  - Guardrails: Deterministic calculations only; surface traceable intermediate values.
- **NarrativeAgent**
  - Purpose: Generate executive-ready summaries and "what changed" storytelling.
  - Tools: Template-based summarizer, Markdown exporter.
  - Triggers: Export request, dashboard refresh.
  - Guardrails: No generative AI; templates reference structured data only.
- **AdapterAgent**
  - Purpose: Coordinate between mock/live adapters for Jira, Slack, ServiceNow.
  - Tools: Adapter registry, Safe Mode toggle, `.env` configuration.
  - Triggers: User toggles Safe Mode, config panel updates, export to Slack.
  - Guardrails: Default to mock; if live mode, enforce read-only operations and redact credentials in logs.

## Decision Logic
- Safe Mode gate ensures AdapterAgent cannot reach external networks without explicit toggle.
- IngestionAgent must complete successfully before AnalyticsAgent runs; failed ingestion short-circuits pipeline and returns validation errors to UI.
- NarrativeAgent requires both analytics results and diffs; if diffs missing (first upload), gracefully omits that section.

## Escalation & Stop Rules
- Repeated ingestion failures (>3 within 10 minutes) disable automatic retries until user action.
- Export errors trigger fallback to local Markdown-only pack; Slack push suppressed when Safe Mode active or token missing.
- Agents must never store secrets or original artifacts outside local cache directory; provide `purge` endpoint to wipe.

## Future Extensions
- Scheduler agent for nightly re-imports.
- Recommendation agent to suggest mitigation owners based on historical patterns (requires additional data and approvals).


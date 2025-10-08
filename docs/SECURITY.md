# Security Overview

## Threat Model (STRIDE-lite)
| Threat | Scenario | Mitigation |
| ------ | -------- | ---------- |
| Spoofing | Malicious actor fakes adapter credentials to access external APIs. | Safe Mode default (no outbound). Validate `.env` tokens via explicit enablement, log warnings, provide visual indicator when live mode active. |
| Tampering | Uploaded CSV/MD manipulated to execute code or corrupt cache. | Parse using safe libraries, sanitize inputs, restrict file types, store in local cache directory with strict permissions. |
| Repudiation | Users dispute actions taken via adapters. | Maintain request audit trail with timestamps and sanitized payload metadata in logs; include request IDs on UI errors. |
| Information Disclosure | Sensitive data leaked via logs or exports. | Redact secrets, limit logs to high-level context, avoid storing raw files beyond cache, support purge endpoint. |
| Denial of Service | Large file uploads or repeated requests degrade service. | Enforce file size limit (5 MB), rate-limit expensive operations, memoize analytics results. |
| Elevation of Privilege | Local scripts executed with elevated permissions. | No shell execution from user inputs, run server as regular user, document safe deployment recommendations.

## Secrets Handling
- `.env.example` enumerates optional adapter tokens (`JIRA_TOKEN`, `SLACK_BOT_TOKEN`, `SERVICENOW_TOKEN`).
- Secrets never checked into source control; gitignore `.env`.
- Safe Mode prevents any adapters from reading `.env` unless user expressly disables it in UI and restarts backend.
- Adapter mode changes persist to `.cache/adapter_modes.json` and are surfaced in the UI; Safe Mode keeps adapters in mock mode regardless of the saved preference.
- Logs redact tokens via middleware; diagnostics exports omit secret-bearing environment variables.
- Jira live adapter is constrained by configurable JQL (`JIRA_JQL_FILTER`) and `JIRA_MAX_RESULTS` to maintain a minimal read-only footprint when Safe Mode is disabled.

## Local-First Mode
- Default run path stores cache and exports under project directory (`.cache/`, `/out/`).
- Provide `purge_cache` endpoint / CLI flag to remove cached analytics.
- Status pack exports include timestamp, dataset hash, and safe file names to avoid collisions.

## Data Protection & Privacy
- Uploaded data processed in-memory and cached as JSON; no outbound transmission unless user enables live adapters.
- Markdown export sanitizes HTML; no active scripting.
- ROI assumptions stored locally in `roi_settings.json`; can be deleted via settings panel.

## Logging & Monitoring
- Structured logs with level, timestamp, request_id; stored in `logs/app.log` rolling file.
- Error logs include stack trace and sanitized payload metadata (column names, counts) but no raw data rows.
- Provide CLI command to tail logs for demo troubleshooting.
- Automation runs (Ingestion → Analytics → Narrative → Export) are persisted to `logs/automation_loop.json` for auditing and replay in the UI.

## Secure Coding Practices
- FastAPI dependency injection for config and Safe Mode enforcement.
- Pydantic validation ensures typed inputs, reducing injection risk.
- Unit tests cover boundary conditions for EVM, risk scoring, diffing, ROI calculations.
- Pre-commit ensures format/lint to catch obvious issues.

## Deployment Guidance (Future)
- For remote deployments, run behind HTTPS reverse proxy with Basic Auth.
- Use service accounts with read-only permissions for adapters.
- Rotate tokens frequently and monitor adapter logs for unusual activity.

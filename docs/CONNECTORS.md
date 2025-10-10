# Connectors & Safe Mode

## Demo Defaults
- **Safe Mode = ON**: no outbound calls. We load `sample/*.csv` and show mocked Jira/ServiceNow/Teams responses for a repeatable demo.

## Switching to Live (read-only first)
1. Disable Safe Mode from **Settings → Safe Mode** (or set `ASR_SAFE_MODE=false`).
2. Flip Jira to `live` in **Settings → Adapters** (persists to `cache/adapter_modes.json`).
3. Provide credentials via environment variables:
   - `JIRA_BASE_URL=https://your-domain.atlassian.net`
   - `JIRA_USER_EMAIL=you@example.com`
   - `JIRA_TOKEN=<api token>`
   - `JIRA_PROJECT_KEY=ABC`
   - Optional: `JIRA_JQL_FILTER=issueType in (Story, Task)` and `JIRA_MAX_RESULTS=200`
4. Keep `WRITE_BACK=false` to enforce human-in-the-loop approvals.

## Supported Sources (v0.3)
- Jira (boards, issues, sprints), ServiceNow (incidents/changes), Planview (milestones), Smartsheet, CSV.
- Comms: Email/Teams for the **Chase Queue** and “Send Status” flows.

## Live sync (alpha)
- `POST /api/ingest/live` builds a dataset snapshot from live adapters.
- The current implementation pulls Jira backlog data (read-only), normalizes statuses, and drafts baseline/notes so analytics and exports render deterministically.
- Response mirrors file-based ingest (`UploadResponse`), so the frontend refresh flow does not change.
- Run `POST /api/settings/adapter-check` with `{ "adapter": "jira" }` to verify credentials before calling live ingest.
- Each live sync writes an audit artifact to `out/live/snapshot_<hash>_<timestamp>.json` so reviewers can inspect the exact payload captured from Jira/ServiceNow.
- Override export targets via environment variables:
  - `ASR_LIVE_EXPORT_TARGET` = `disk` (default), `s3`, or `azure`
  - Disk overrides: `ASR_LIVE_EXPORT_PATH=/var/lib/asr/live`
  - S3: set `ASR_LIVE_EXPORT_BUCKET`, optional `ASR_LIVE_EXPORT_PREFIX` and `ASR_LIVE_EXPORT_REGION`
  - Azure Blob: set `ASR_LIVE_EXPORT_AZURE_URL`, `ASR_LIVE_EXPORT_AZURE_CONTAINER`, optional `ASR_LIVE_EXPORT_AZURE_PREFIX`, and `ASR_LIVE_EXPORT_AZURE_CREDENTIAL` (SAS token or key)
- Export handlers require the corresponding SDKs when targeting cloud storage (`boto3` for S3, `azure-storage-blob` for Azure).

## Extension Guide
- New source = new mapper: extend `app/backend/services/live_ingestion.py` and `app/backend/adapters/__init__.py`.
- Add unit tests under `app/tests/` (see `test_live_ingestion.py`) with scrubbed fixtures for parity.

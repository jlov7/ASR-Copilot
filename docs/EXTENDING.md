# Extending ASR Copilot

This guide shows where to plug in new adapters, metrics, and UI cards so your team can tailor ASR Copilot to additional workflows.

## Live adapters: what's required

Before toggling any adapter to **Live** mode:

- [ ] Set the necessary environment variables in `.env` (`JIRA_*`, `SLACK_*`, `SERVICENOW_*`) with **read-only** credentials or bot tokens.
- [ ] Disable Safe Mode in the top navigation (`ASR_SAFE_MODE=false` or toggle in-app) so outbound requests are permitted.
- [ ] Confirm scopes are limited to the data you need (e.g., Jira project browse, read-only ServiceNow tables, Slack channel post target).
- [ ] Restart the backend after changing environment variables so adapters pick up fresh config.
- [ ] Use **Settings → Adapters → Sanity check** to verify credentials before demoing to stakeholders.

## Add a new adapter

1. **Create the adapter module**  
   - Place a new module under `app/backend/adapters/`.  
   - Implement the `AdapterBase` interface (see `jira.py` for a reference). Focus on read-only calls while Safe Mode is on.

2. **Register the adapter**  
   - Update `app/backend/adapters/__init__.py` to expose the adapter in `ADAPTER_REGISTRY`.  
   - If you need configuration, add environment variables to `.env.example` and surface them in `Settings` (see `config.py`).

3. **Wire up an API route**  
   - Add a FastAPI route under `app/backend/routes/adapters/` to expose adapter health checks or data fetches.  
   - Reuse Pydantic models for typed responses; update `app/frontend/src/types/` accordingly.

4. **Surface the adapter in the UI**  
   - Extend the Adapters panel (`Settings → Adapters`) in the React app to let users toggle Mock/Live and run “Sanity check” calls.
   - Keep Safe Mode guardrails: live adapters stay disabled until credentials exist and Safe Mode is off.

5. **Document it**  
   - Append the adapter to `docs/ARCHITECTURE.md` and `docs/ROADMAP.md` (Orchestrate phase).  
   - Add an issue template checklist item ensuring tests/docs are updated.

## Add a new metric or dashboard card

1. **Backend analytics**  
   - Implement the calculation in `app/core/`. Follow the patterns from `evm.py` or `risk_scoring.py`.  
   - Update `app/backend/models.py` with a typed schema and extend `build_dashboard_payload` to include the metric.

2. **Frontend rendering**  
   - Add the new field to `app/frontend/src/types/index.ts`.  
   - Create a card component under `app/frontend/src/components/` or extend `DashboardView.tsx`.  
   - Include ARIA labels, keyboard focus states, and tooltip copy that keeps the story human-friendly.

3. **Status pack exports**  
   - If the metric should appear in the Markdown/PDF exports, update `app/core/status_pack.py` to add sections or charts.

4. **Tests**  
   - Add unit tests under `app/tests/` and, if applicable, Vitest coverage for the UI.  
   - Update golden datasets (`data/samples/`) so demos stay deterministic.

5. **Docs & demo**  
- Refresh screenshots under `docs/SCREENSHOTS/`.  
  - Mention the new card in `docs/DEMO-SCRIPT.md` and the README “Demo shows” section.

## From Demo → Enterprise

When you graduate the demo into an enterprise deployment, plan for:

- **SSO & RBAC** – front the FastAPI app with SSO and map roles (viewer, editor, admin) to adapter privileges.
- **Centralized secrets** – move credentials to Vault/Secrets Manager and rotate regularly.
- **Audit logging** – capture adapter access, exports, and purges in a tamper-evident log.
- **Rate-limit & failure tests** – run adapter dry-runs against staging tenants to exercise throttling and retries.
- **Multi-tenant configuration** – parameterize dataset/cache directories and export paths per customer or program.
- **Privacy review** – document retention, purge controls, and redaction in line with your security/compliance checklist.

With these steps you can introduce new telemetry while keeping the agentic guardrails and Safe Mode posture intact.

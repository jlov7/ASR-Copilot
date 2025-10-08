# ASR Copilot

[![Run the Demo](https://img.shields.io/badge/Run%20the%20Demo-bash-blue?logo=gnubash)](#quickstart) [![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-Codespaces-24292e?logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=jlov7%2FASR-Copilot) [![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](LICENSE) [![CI](https://github.com/jlov7/ASR-Copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/jlov7/ASR-Copilot/actions/workflows/ci.yml)

ASR Copilot (Autonomy–Status–Risk Copilot) is a production-quality proof-of-concept that automates the most time-consuming, rationalizable PM workflows for enterprise TMT/Telco programs. It ingests CSV/Markdown status artifacts (no credentials required), computes earned value metrics, surfaces a live risk watchlist, narrates what changed since yesterday, and assembles a shareable executive status pack with a single click.

> **See it in 15 seconds** → Click **Instant Demo (no files needed)** below.  
> ASR Copilot turns weekly status drudgery into a 3-minute executive update: *health (RAG)* → *EVM (CPI/SPI)* → *Top risks* → *What changed* → *1-click export*.  
> **No integrations. Safe Mode by default. Deterministic analytics.**

![ASR Copilot overview](docs/SCREENSHOTS/overview.gif)

[📈 Why this matters](WHY.md) · [🎤 Presenter notes](docs/DEMO-SCRIPT.md)

| Before | After (ASR Copilot) | Impact example (tunable) |
| --- | --- | --- |
| Manual aggregation of spreadsheets, inconsistent narratives, risks discovered late (3–4 hrs/week/PM). | Upload CSV/MD → CPI/SPI gauges + risk deltas + “what changed” timeline → one-click executive status pack (minutes). | 30 PMs × 3.5 hrs/week × $120/hr × 48 wks ≈ **$604,800/yr**. A 70% reduction via ASR Copilot ≈ **$423,360/yr** reclaimed (adjust in the ROI panel). |

**Screenshot gallery:** `docs/SCREENSHOTS/landing.png`, `tour-step.png`, `evm.png`, `risks.png`, `roi.png`, `export-toast.png`

## Why it matters
Program managers in large enterprises spend 8–12 hours per week aggregating status, chasing risks, and preparing exec-ready updates. ASR Copilot shrinks that cycle to minutes by:
- PMOs lose **3–4 hrs/week per PM** to duplicative status reporting and swivel-chair data pulls from Jira, spreadsheets, and slides.
- Weekly status packs score **4.5/5 automation readiness** in enterprise interviews—highly standardized, low-risk to draft automatically.
- Normalizing backlog, risk, and status-note inputs without integrations.
- Calculating CPI/SPI deltas and early schedule risk warnings.
- Auto-drafting executive narratives, mitigations, and ROI evidence to rationalize automation investments.

### Why agentic AI (safely) helps PMOs
1. **Automates drudgery, not decisions** – deterministic agents normalize inputs and pre-assemble evidence so PMs stay focused on steering calls.  
2. **Auditability first** – SPI = EV ÷ PV and CPI = EV ÷ AC; trusted control limits make rationalization defensible.  
3. **Guardrails on integrations** – Safe Mode is the default, adapters are read-only, logs redact secrets.  
4. **Real productivity gains** – enterprises see the biggest uplift when AI accelerates many workflows, not a single task.

## Key capabilities
- **Instant Demo (no files)**: Preload Telco 5G, cloud migration, or CPE swap scenarios with Safe Mode locked on—ideal for skeptical execs.
- **No-integration uploads**: Bring your own CSV/Markdown artifacts to refresh analytics in minutes.
- **Executive cockpit**: RAG banner, EVM gauges, Top 5 risks, ROI estimator with complexity presets, and “what changed” timeline.
- **Status Pack exports**: Generates Markdown + PNG charts in `/out/` and optionally posts to Slack when credentials exist.
- **Adapters**: Mock Jira/Slack/ServiceNow providers ship by default; live adapters activate via `.env` tokens.
- **Safety-first**: Local-first storage, Safe Mode toggle to disable outbound calls, and deterministic summarization.
- **Hosted safe demo**: Deployable to Render or Fly via `render.yaml` with Safe Mode enforced and only offline sample data.
- **Automation loop**: Visual runbook tracks Ingestion → Analytics → Narrative → Export, with one-click dry runs for stakeholders.
- **Adapters control**: Guided panel to switch mock/live modes, run sanity checks, and highlight Safe Mode guardrails.
- **Presenter shortcuts**: Hit `Shift + ?` during the demo to reveal keyboard shortcuts (tour, sample load, export, dry-run).
- **Reset & purge controls**: Reset to sample data in one click and purge cached datasets/exports via **Settings → Privacy** before screen shares.

### Security at a glance
- **Safe Mode locked on**: The demo, Instant Demo, and hosted templates run without outbound calls.
- **Mock adapters only**: Jira/Slack/ServiceNow stay read-only until you intentionally provide credentials.
- **Local-first exports**: Status packs land in `/out/` on your machine; secrets never persist to disk.

## Screenshot gallery
![Landing page](docs/SCREENSHOTS/landing.png)
![Guided tour step](docs/SCREENSHOTS/tour-step.png)
![EVM gauges and RAG](docs/SCREENSHOTS/evm.png)
![Risk watchlist](docs/SCREENSHOTS/risks.png)
![ROI panel](docs/SCREENSHOTS/roi.png)
![Export toast](docs/SCREENSHOTS/export-toast.png)

## Architecture snapshot
- **Backend**: FastAPI (Python 3.10+) with Pydantic contracts, modular `app/core` analytics (EVM, risks, diffs, summarizer), adapter layer, and status pack exporter.
- **Frontend**: Vite + React + TypeScript SPA with guided onboarding tour, skeleton loaders, accessible dashboard, and ROI configurator.
- **Data flow**: Ingested files parsed into structured JSON, validated, analyzed, and cached; frontend consumes typed endpoints.
- **Tooling**: pytest, ruff, black, eslint, prettier, husky-style git hooks via pre-commit.

## Quickstart

### Option A – Local toolchain
1. **Prerequisites**
   - Python 3.10+
   - Node.js 18+
   - `pip`, `npm`, and `uvicorn`
2. **Install backend dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Install frontend dependencies**
   ```bash
   cd app/frontend
   npm install
   ```
4. **Run the local demo**
   ```bash
   cd ..
   ./scripts/run_demo.sh
   ```
   The script boots FastAPI at `http://127.0.0.1:8000` and Vite at `http://127.0.0.1:5173`, preloads sample data, and opens the dashboard.
    - **Windows PowerShell:** `.\app\scripts\run_demo.ps1`

### Option B – Docker Compose (no local installs)
1. Build and run:
   ```bash
   docker compose -f compose.yaml up --build
   ```
2. Visit `http://localhost:5173` (frontend) and `http://localhost:8000` (backend). The compose file mounts `data/samples`, `out/`, and `logs/` so exports persist on the host.

### Option C – GitHub Codespaces / Dev Containers
- Click the “Open in Codespaces” badge above or run `gh codespace create --repo jlov7/ASR-Copilot`.
- The devcontainer installs Python + Node dependencies automatically; use `./app/scripts/run_demo.sh` inside the Codespace.
- To use locally with VS Code Dev Containers or Docker Desktop, open the repo in a devcontainer and run `make demo`.

### Option D – Hosted Safe Demo (Render)
1. Fork this repo (or use it as a template) so you can connect Render.
2. In the Render dashboard choose **New → Blueprint** and point it at `render.yaml`.
3. Deploy with the default environment variables (`ASR_SAFE_MODE=true`, `ADAPTER_MODE=mock`). Instant Demo stays offline-only.
4. Render serves the FastAPI backend and the pre-built React frontend from the same service at the generated URL.

## Vite + React rationale
- Granular control over accessibility and onboarding flows.
- Straightforward integration with FastAPI JSON contracts via generated TypeScript types.
- Supports progressive enhancements (tour, skeleton loaders) without heavy frameworks.

## Demo script (≈3 minutes)
Grab the presenter-ready flow in `docs/DEMO-SCRIPT.md`. It mirrors the GIF: tour → load sample → health + risks → timeline → ROI → export toast. Each step includes plain-English narration so any teammate can deliver the demo confidently.

## Project layout (high level)
```
README.md
requirements.txt
app/
  backend/
  core/
  frontend/
  scripts/
  tests/
docs/
data/samples/
.tooling/
```
A detailed tree lives in `docs/ARCHITECTURE.md`.

### Documentation quick links
- [WHY.md](WHY.md) – value story, before/after table, autonomy ladder  
- [docs/PRD.md](docs/PRD.md) – problem statement, personas, acceptance criteria  
- [docs/PLAN.md](docs/PLAN.md) – milestones, risks, demo coordination  
- [docs/DEPLOY.md](docs/DEPLOY.md) – pilot playbook for Assist → Orchestrate → Autopilot rollouts  
- [docs/AGENTS.md](docs/AGENTS.md) – agent roles, triggers, and guardrails  
- [docs/DATA-SCHEMA.md](docs/DATA-SCHEMA.md) – CSV/Markdown contracts, EVM formulas, sample data dictionary  
- [docs/EVM-PRIMER.md](docs/EVM-PRIMER.md) – CPI/SPI primer with worked example  
- [docs/EXTENDING.md](docs/EXTENDING.md) – how to add adapters, metrics, and cards  
- [docs/DEMO-SCRIPT.md](docs/DEMO-SCRIPT.md) – presenter-ready 3-minute flow  
- [docs/ROADMAP.md](docs/ROADMAP.md) – Assist → Orchestrate → Autopilot rollout plan  
- [docs/DEMOS.md](docs/DEMOS.md) – 3-minute & 10-minute demo walkthroughs  
- [docs/DEMO-DECK.md](docs/DEMO-DECK.md) – ready-to-present executive pitch deck (Markdown)  
- [docs/SECURITY.md](docs/SECURITY.md) – STRIDE-lite control set, Safe Mode posture  
- [docs/EVALS.md](docs/EVALS.md) – evaluation metrics, ROI scenario table, regression plan  
- [docs/CHANGELOG.md](docs/CHANGELOG.md) – release history & demo cues

## Repository metadata
- Suggested GitHub description: `Agentic AI copilot that turns PM status rituals into a 3-minute update (Instant Demo included).`
- Suggested topics: `project-management`, `agentic-ai`, `evm`, `telco`, `pmo`

## Environment configuration
- Copy `.env.example` to `.env` when enabling live adapters.
- Safe Mode (default) ensures zero outbound requests and relies on bundled mock adapters.
- Secrets are never stored or logged; redact tokens before sharing logs.
- For Jira live mode set `JIRA_BASE_URL`, `JIRA_USER_EMAIL`, `JIRA_TOKEN`, `JIRA_PROJECT_KEY`, and optionally `JIRA_JQL_FILTER`/`JIRA_MAX_RESULTS`; then disable Safe Mode to sync read-only backlog data.
- Run `pytest -m live` to execute Jira integration tests after supplying real credentials.
- Toggle adapters in-app via **Settings → Adapters**; live mode is disabled until Safe Mode is off and environment variables are present.

## Testing
- `pytest -k golden` verifies the deterministic dashboard payload stays aligned with `out/golden/dashboard_5g.json`.
- Run `pytest` for backend analytics, automation loop logging, and adapter guardrail coverage.
- `npm run test -- --run` executes frontend unit tests (Vitest) and accessibility smoke checks.
- Pre-commit hooks enforce formatting and linting prior to commits.
- For end-to-end sanity, use `python -m app.scripts.capture_media` to rebuild the demo walkthrough screenshots/GIFs.

## API reference
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Accessibility & UX commitments
- WCAG AA color contrast, keyboard focus outlines, ARIA landmarks, and screen reader friendly chart summaries.
- Skeleton states for dashboard cards, empathetic empty states with direct CTAs, and graceful error banners with retry guidance.

## Contributing & next steps
- Read the [CONTRIBUTING guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR.
- Extend adapters under `app/backend/adapters` to integrate live Jira/Slack/ServiceNow endpoints.
- Expand evaluation metrics (latency, cost) using the scaffolding in `docs/EVALS.md`.
- Share feedback in the `docs/CHANGELOG.md` discussion log to inform the next sprint.
- File issues for Docker/Codespaces improvements or ecosystem adapters (e.g., ServiceNow change integration).
- Use the **Refresh Media Assets** workflow (Actions tab) if you tweak the UI and need new screenshots.
- Issue templates live in `.github/ISSUE_TEMPLATE/`; start with the adapter request template when proposing new integrations.

## License
Distributed under the [Apache 2.0 License](LICENSE). See the license file for details and the NOTICE requirements for derivative work.

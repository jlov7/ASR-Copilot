# ASR Copilot

*Agentic AI copilot that turns PM status rituals into a 3-minute update (Instant Demo included).*

[![Run the Instant Demo](https://img.shields.io/badge/Run%20the%20Instant%20Demo-local-blue?logo=gnubash)](QUICKSTART.md#1-instant-demo-no-files-runs-locally) [![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-Codespaces-24292e?logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=jlov7%2FASR-Copilot) [![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-3e5)](https://render.com/deploy?repo=https://github.com/jlov7/ASR-Copilot) [![CI](https://github.com/jlov7/ASR-Copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/jlov7/ASR-Copilot/actions/workflows/ci.yml) [![Coverage](docs/badges/backend-coverage.svg)](docs/badges/backend-coverage.svg) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-3DDC84?logo=pre-commit&logoColor=white)](.tooling/pre-commit-config.yaml) [![CodeQL](https://github.com/jlov7/ASR-Copilot/actions/workflows/codeql.yml/badge.svg)](https://github.com/jlov7/ASR-Copilot/actions/workflows/codeql.yml) [![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/jlov7/ASR-Copilot?label=OpenSSF%20Scorecard)](https://github.com/jlov7/ASR-Copilot/actions/workflows/scorecard.yml) [![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](LICENSE)

> **Security posture: Safe Mode ON.** No outbound calls, adapters stay in mock mode, exports stay local. [Read SECURITY.md](docs/SECURITY.md)

<figure>
  <video controls width="100%" poster="docs/media/instant-demo.gif">
    <source src="docs/media/instant-demo.mp4" type="video/mp4">
    Your browser does not support embedded video. Watch the Instant Demo walkthrough in `docs/media/instant-demo.mp4`.
  </video>
  <figcaption>Instant Demo walkthrough: tour → health/EVM → risks → timeline → ROI → export.</figcaption>
</figure>

> Quick path? Jump to **[Quickstart for non-devs](QUICKSTART.md)** for three 60-second launch options (Local, Codespaces, Render).

## What this POC is / isn’t
- Deterministic analytics and explainable agents that automate the PM ritual, not the decisions.
- No credentials required out of the box—Safe Mode locks off outbound calls and ships with mock adapters.
- A polished Instant Demo plus rich docs so execs, PMs, and engineers can evaluate enterprise readiness in minutes.

## Table of contents
- [Why it matters](#why-it-matters)
- [Key capabilities](#key-capabilities)
- [Security at a glance](#security-at-a-glance)
- [Screenshot gallery](#screenshot-gallery)
- [Architecture snapshot](#architecture-snapshot)
- [Quickstart](#quickstart)
- [Vite + React rationale](#vite--react-rationale)
- [Demo script (≈3 minutes)](#demo-script-3-minutes)
- [Project layout (high level)](#project-layout-high-level)
- [Repository metadata](#repository-metadata)
- [Environment configuration](#environment-configuration)
- [Testing](#testing)
- [API reference](#api-reference)
- [Accessibility & UX commitments](#accessibility--ux-commitments)
- [Contributing & next steps](#contributing--next-steps)

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

> Need screenshots and copyable commands? See [QUICKSTART.md](QUICKSTART.md) for the three 60-second launch paths.

- **Option A – Local Instant Demo (no files)**  
  Create a `.venv`, `pip install -r requirements.txt`, run `npm install` in `app/frontend`, then `make demo`. The script seeds sample data, launches FastAPI (`8000`) + Vite (`5173`), and opens the dashboard with Safe Mode locked on.

- **Option B – Docker Compose (self-contained)**  
  `docker compose -f compose.yaml up --build` boots both services with sample data mounted from `data/samples/`. Visit `http://localhost:5173`, no local Python/Node needed.

- **Option C – GitHub Codespaces / Dev Containers**  
  Click the Codespaces badge or run `gh codespace create --repo jlov7/ASR-Copilot`, wait for the devcontainer to provision, then execute `make dev`. Forward ports 8000/5173 and click Instant Demo.

- **Option D – Hosted Safe Demo (Render Blueprint)**  
  Use the Deploy to Render badge, accept defaults from `render.yaml`, and open the generated URL. Safe Mode stays enabled; only the curated demo scenarios are exposed.

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
- **Description** (GitHub → About): `Agentic AI copilot that turns PM status rituals into a 3-minute update (Instant Demo included).`
- **Topics**: `project-management`, `agentic-ai`, `evm`, `telco`, `pmo`
- Keep these in sync with the README tagline so the repo stays discoverable.

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
- Need a starter task? Copy one of the ready-made prompts in [docs/GOOD-FIRST-ISSUES.md](docs/GOOD-FIRST-ISSUES.md).

## License
Distributed under the [Apache 2.0 License](LICENSE). See the license file for details and the NOTICE requirements for derivative work.

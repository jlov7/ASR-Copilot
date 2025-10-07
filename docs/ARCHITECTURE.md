# Architecture Overview

## High-Level Diagram (Textual)
```
┌────────────┐    Upload CSV/MD    ┌───────────────┐
│  Frontend  │ ───────────────────▶│  FastAPI API  │
│ (React)    │                     │ (app/backend) │
└─────┬──────┘                     └──────┬────────┘
      │  JSON (REST)                      │
      ▼                                   ▼
┌────────────┐                ┌────────────────────┐
│ State Mgmt │◀──────────────▶│ Analytics Core     │
│ (Redux-lite│                │ (app/core/*)       │
│  hooks)    │                └──────┬─────────────┘
└─────┬──────┘                       │
      │                              │
      ▼                              ▼
┌────────────┐                ┌────────────────────┐
│ LocalCache │                │ Adapters Registry  │
│ (.cache)   │                │ (mock & live)      │
└────────────┘                └────────────────────┘
```

## Backend Modules (`app/backend`)
- `main.py`: FastAPI app factory, routers, middleware, Safe Mode enforcement.
- `config.py`: Settings management (Safe Mode, adapter mode, paths).
- `models.py`: Pydantic schemas (Task, Risk, StatusNote, EvmMetrics, RiskSummary, StatusPack, ROI settings, API responses).
- `routes/` (submodule):
  - `ingest.py`: Upload endpoints, sample data loader.
  - `analytics.py`: Endpoints returning summaries (status, risks, ROI).
  - `export.py`: Trigger status pack generation (Markdown + PNG).
  - `settings.py`: Safe Mode toggle, ROI persistence.
- `services/`:
  - `ingestion.py`: CSV parsing, schema validation, caching.
  - `status.py`: Orchestrates analytics core modules, composes dashboard payload.
  - `exporter.py`: Builds Markdown, charts, writes to `/out/`, optionally Slack.
- `adapters/`: Live and mock adapters with shared interface.
- `logging.py`: Structured logging setup.

## Core Analytics Modules (`app/core`)
- `evm.py`: PV/EV/AC calculations, SPI/CPI/EAC/ETC formulas with docstrings.
- `risk_scoring.py`: Severity scoring, heatmap preparation, mitigation suggestions.
- `diffs.py`: Compare current vs previous uploads (tasks, risks, status notes) using `difflib`.
- `summarizer.py`: Deterministic narrative generator for RAG, risks, changes.
- `roi.py`: ROI assumptions persistence, savings projection logic.

## Data Model
- **Task**: `id`, `title`, `owner`, `status`, `start_date`, `finish_date`, `planned_hours`, `actual_hours`, `blocked`, `dependency_ids`.
- **Risk**: `id`, `summary`, `probability`, `impact`, `owner`, `due_date`, optional mitigation.
- **StatusNote**: `date`, `author`, `content` (Markdown).
- **EVM Metrics**: `pv`, `ev`, `ac`, `sv`, `cv`, `spi`, `cpi`, `eac`, `etc`, `vac`, `baseline_date`.
- **DashboardPayload**: Combines metrics, risk summary, changes timeline, ROI snapshot, metadata.

## Adapter Boundary
- `BaseAdapter` defines `fetch_backlog`, `fetch_risks`, `fetch_status_notes` signatures (backlog project key stored in adapter configuration).
- Mock adapters source from `data/samples/`.
- Live adapters (`jira.py`, `slack.py`, `servicenow.py`) read `.env` tokens and operate only when Safe Mode off. Jira adapter honours `JIRA_JQL_FILTER` and `JIRA_MAX_RESULTS` to keep the read-only query scoped.
- Adapter registry selects implementation based on configuration.

## Error Taxonomy
| Code | HTTP Status | Meaning | Example |
| ---- | ----------- | ------- | ------- |
| `INGEST-001` | 400 | Missing required columns | Task CSV missing `planned_hours`. |
| `INGEST-002` | 422 | Invalid data type | Probability outside 0..1 range. |
| `ANALYTICS-001` | 500 | EVM computation failure | Division by zero due to AC=0 edge case. |
| `EXPORT-001` | 500 | Status pack write failure | OS permission error writing to `/out/`. |
| `ADAPTER-001` | 403 | Live adapter blocked | Safe Mode preventing external call. |

## Persistence & Caching
- Processed datasets stored as JSON in `.cache/<dataset_id>/`.
- ROI assumptions saved to `.cache/roi_settings.json`.
- Last snapshot stored for diffing (`.cache/last_snapshot.json`).

## Extensibility Points
- **Adapters**: Add new integrations by implementing `BaseAdapter`.
- **Analytics**: Additional metrics modules loadable via plugin registry.
- **Exports**: Extend `exporter.py` to add PPTX/PDF output.
- **Frontend**: Component-oriented architecture with typed API clients; add views by extending route definitions and query hooks.

## Deployment Notes
- Local demo uses `uvicorn` + `npm run dev`. For production, run `uvicorn` behind ASGI server and `npm run build` served via CDN or static hosting.
- Logging configuration switchable between console and JSON file output.

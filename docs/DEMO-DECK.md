# ASR Copilot – Executive Demo Deck

## Slide 1 – Problem & Stakes
- PMs spend 3–4 hrs/week on status aggregation, risk rollups, and exec formatting.
- Manual cycle produces inconsistent narratives and late risk discovery.
- Leadership needs CPI/SPI-backed evidence for rationalization decisions.

## Slide 2 – Solution Overview
- Drop CSV/Markdown exports → Safe Mode (no credentials) normalizes tasks, risks, notes.
- Backend computes EVM, risk severity, and diffs; React cockpit surfaces insights instantly.
- One-click export packages RAG summary, top risks, ROI snapshot, and “what changed.”

## Slide 3 – Before vs. After
| Before (Manual) | After (ASR Copilot) |
| --- | --- |
| Spreadsheet wrangling, ad-hoc narratives, late escalations. | Upload → CPI/SPI gauges + risk heatmap + diff timeline in minutes. |
| 30 PMs × 3.5 hrs/week × $120/hr × 48 wks ≈ $604,800/yr. | 70% cycle reduction ≈ $423,360/yr reclaimed (editable ROI presets). |
| No guardrails for integrations. | Safe Mode default, read-only adapters, redacted logs. |

## Slide 4 – Live Flow (60–90s)
1. Launch Safe Mode demo (`./app/scripts/run_demo.sh`).
2. Guided tour highlights upload, dashboard, ROI, export.
3. Load sample data → CPI 0.87 / SPI 0.82 surfaces vendor delay risk.
4. Export Status Pack → Markdown + PNG charts ready for exec email.

## Slide 5 – Enterprise Path
- Phase 1 (Pilot): Local-first, Safe Mode, anonymized sample data.
- Phase 2 (Read-only live): Provide adapter tokens, enable audit logging/CodeQL/CI.
- Phase 3 (Scale): Multi-project tenancy, SSO front door, nightly scheduler agent.
- Docs to share: [SECURITY.md](./SECURITY.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [EVALS.md](./EVALS.md).

*Tip: Convert this Markdown with your presentation tool of choice (e.g., Marp, Deckset, PowerPoint import) and drop in the screenshots from `docs/media/`.*

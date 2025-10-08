# Demo Playbooks

## 3-Minute Walkthrough (default)
Follow the presenter script in [docs/DEMO-SCRIPT.md](./DEMO-SCRIPT.md). The headline beats:
1. **Launch Safe Mode demo** – run `./app/scripts/run_demo.sh` (or `./run_demo.ps1` on Windows); highlight that no credentials are required.
2. **Run the guided tour** – click “Start guided tour,” watch the Step 1 of 5 breadcrumb, and replay link.
3. **Load sample data** – press “Load sample program”; skeleton loaders flip to live metrics.
4. **Narrate the story** – three workstreams, two vendors, tight dependency chain; CPI/SPI under pressure with `Explain this` popover.
5. **Top risks** – draft mitigation from the risk table and show the Automation Loop checks.
6. **What changed** – toggle “Recent (Top 5)” versus “Full history” and group changes by category to highlight risks vs tasks.
7. **ROI panel** – toggle presets, tweak sliders, copy assumptions.
8. **Export** – click “Export Status Pack,” point to the toast path, “Reveal,” and “Copy Markdown.”
9. **Safe Mode reminder** – highlight the header banner and adapter toggles for future live runs.
10. **Keyboard cue** – press `Shift + ?` to show the shortcuts panel for presenters who need a script.

## 10-Minute Executive Briefing
1. **Context (1 min)** – PMO pain (manual aggregation, slow risk surfacing, inconsistent packs).
2. **Ingestion (1 min)** – show CSV schemas in [docs/DATA-SCHEMA.md](./DATA-SCHEMA.md) and how Safe Mode keeps data local.
3. **Analytics (2 min)** – walk the dashboard: CPI/SPI gauges with tooltips, risk heatmap, diff pills.
4. **Autonomy story (2 min)** – cover [docs/AGENTS.md](./AGENTS.md) guardrails; humans-in-the-loop decisions.
5. **Live adapters (1 min)** – demonstrate Safe Mode banner, `.env` toggles, read-only enforcement.
6. **ROI deep dive (2 min)** – iterate presets and slider multipliers; copy the assumptions for email follow-up.
7. **Export + follow on (1 min)** – show Markdown + PNG pack, mention GitHub Actions / Docker for enterprise hand-off.

## Talking Points
- CPI < 1 and SPI < 1 flag schedule and cost risk early; mitigation ready in risk list.
- Diff timeline captures “what changed since yesterday” for exec mailers.
- ROI panel assumptions persist locally; presets align with low/medium/high PMO complexity.
- Safe Mode banner reassures security; toggle surfaces adapter modal describing read-only scope.

## Assets
- Screenshots live under `docs/SCREENSHOTS/` and map to the README gallery.
- The animated walkthrough is `docs/media/demo-flow.gif`; regenerate via `python -m app.scripts.capture_media`.

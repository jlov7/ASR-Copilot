# Demo Playbooks

## 3-Minute Walkthrough (default)
1. **Launch Safe Mode demo** – run `./app/scripts/run_demo.sh`; highlight that no credentials are required.
2. **Run the guided tour** – click “Start guided tour” and step through the five overlays.
3. **Load sample data** – press “Try with sample data”; skeleton loaders flip to live metrics.
4. **Narrate the story** – three workstreams, two vendors, tight dependency chain; CPI/SPI under pressure.
5. **Top risks** – call out the late-shipment vendor risk and mitigation notes.
6. **What changed** – show the diff timeline (new risk, updated mitigation).
7. **ROI panel** – toggle preset from Medium → High, tweak sliders, show savings delta.
8. **Export** – click “Export Status Pack,” open the generated Markdown in `/out/`.
9. **Safe Mode reminder** – highlight the header banner and how to enable live adapters later.

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
- Screenshots live under `docs/media/` and are referenced in the README.
- For recorded demos, reuse `docs/media/demo-flow-placeholder.gif` until real footage is captured.

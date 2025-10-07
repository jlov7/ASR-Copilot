# UX Copy Inventory

## Landing / Tour
- Hero headline: "Automate your status rituals."
- Sub-head: "Upload your backlog, risks, and notes—ASR Copilot delivers executive clarity in minutes."
- CTA buttons: `Start guided tour`, `Try with sample data`, `Upload your files`.
- Safe Mode tooltip: "Safe Mode keeps all adapters local-only. Provide credentials later to connect live systems."
- Tour step headlines:
  1. "Upload once, align instantly."
  2. "Know your CPI/SPI pulse."
  3. "Triage the top risks fast."
  4. "See what changed since yesterday."
  5. "Prove ROI with defensible numbers."
- Tour final CTA: `Done – take me to the dashboard`.

## Dashboard Copy
- RAG badge labels: `On Track`, `Watch`, `At Risk`.
- Schedule risk banner: "Early warning: Planned finish slips by {{days}} days." / "Schedule confidence within tolerance." when clear.
- KPI tooltip copy examples:
  - PV: "Planned Value based on scheduled hours through today."
  - EV: "Earned Value using completed + in-progress weights."
  - CPI: "Cost Performance Index (EV / AC). >1.0 is favorable."
- Risk list empty: "No risks logged. Import your risk register to populate the watchlist." CTA `Upload risks.csv`.
- Risk severity chip text: `High`, `Medium`, `Low` with accessible aria-label "Risk severity {{level}}".
- Heatmap summary caption: "Bubble size reflects time to due date. Tab to focus each risk for details."
- Changes timeline section intro: "Here’s what moved since your last update." Empty state: "No changes detected yet. Once we’ve seen at least two uploads, we’ll highlight the deltas."

## ROI Calculator
- Section header: "Show me the ROI."
- Assumption labels: `Task frequency (per month)`, `Hours saved per task`, `PM hourly cost`, `Team size impacted`.
- Sensitivity slider labels:
  - `Time saved multiplier`
  - `Frequency multiplier`
- Result headline: "Projected annual savings: ${{amount}}".
- Sub-copy: "Tweak your assumptions to match your program reality. We’ll remember them for next time."
- Reset button: `Reset to defaults`.

## Status Pack Export
- Button text: `Export Status Pack`.
- Success toast: "Status Pack ready in /out/status_pack_<timestamp>.md".
- Slack optional tooltip: "Add a Slack token in .env to send executive updates in one click."
- Error toast: "Export failed—check file permissions or rerun in Safe Mode."

## Error & Recovery Copy
- Generic error banner: "We hit a snag. Retry or download details for your engineering team."
- Retry button: `Retry processing`.
- Download diagnostics: `Download JSON diagnostics`.
- Offline banner: "Looks like you’re offline. We’ll auto-retry when the connection returns."

## Footer / Misc
- Footer text: "ASR Copilot – built for TMT/Telco PMs navigating complex autonomy programs."
- Replay tour link: `Replay onboarding tour`.
- Accessibility note: "Need keyboard shortcuts? Press '?' for the cheat sheet."

# EVM Primer

Earned Value Management (EVM) is the heartbeat of ASR Copilot’s health indicators. This primer explains the key terms we surface in the dashboard, how we calculate them, and how to interpret the gauges.

## Core concepts

- **Planned Value (PV)** – The budgeted hours/cost for the work you scheduled up to a given date.
- **Earned Value (EV)** – The value of the work actually completed, weighted by planned effort.
- **Actual Cost (AC)** – The effort actually spent so far (we treat hours as the cost proxy in Safe Mode).

From these baselines we derive:

- **Schedule Variance (SV)** = EV − PV. Negative SV indicates you are behind schedule.
- **Cost Variance (CV)** = EV − AC. Negative CV indicates you are overspending.
- **Schedule Performance Index (SPI)** = EV ÷ PV. SPI below 0.90 signals schedule pressure.
- **Cost Performance Index (CPI)** = EV ÷ AC. CPI below 0.90 signals cost pressure.
- **Estimate at Completion (EAC)** = AC + (BAC − EV) ÷ CPI. Forecast of total cost at completion.
- **Variance at Completion (VAC)** = BAC − EAC. Negative VAC means you expect to miss the budget.

## Worked example

| Metric | Example value | How we read it |
| --- | --- | --- |
| PV | 380 hrs | Planned effort through the current baseline date. |
| EV | 310 hrs | Weighted effort actually earned so far. |
| AC | 356 hrs | Actual hours logged to date. |
| SV | −70 hrs | 70 hours behind schedule (EV < PV). |
| CV | −46 hrs | 46 hours over budget (EV < AC). |
| SPI | 0.82 | Behind schedule; follow-up with workstream owners. |
| CPI | 0.87 | Cost pressure; escalate with finance or vendor. |

In this scenario the SPI and CPI gauges both fall into the amber/red range, so ASR Copilot elevates the RAG banner and highlights the affected risks/timeline entries.

## Deep dive

- The gauges clamp at 0.5–1.5 for readability but we keep raw values in exports.
- Baseline dates come from the `evm_baseline.csv` you upload; samples ship in `data/samples/`.
- `docs/DATA-SCHEMA.md` outlines the CSV columns we expect (planned vs. actual hours, task identifiers, etc.).

Need to go deeper? Open an issue tagged **adapter request** to connect live Jira or ServiceNow data while keeping Safe Mode guardrails.

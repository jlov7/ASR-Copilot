# Data Schema & Earned Value Formulas

## Backlog Tasks (`tasks.csv`)
| Column | Type | Required | Description |
| ------ | ---- | -------- | ----------- |
| `id` | string | ✓ | Unique task identifier (e.g., T-201). |
| `title` | string | ✓ | Human-readable task summary. |
| `owner` | string | ✓ | Primary owner / assignee. |
| `status` | enum | ✓ | One of `Not Started`, `In Progress`, `Complete`, `Blocked`. |
| `start` | ISO date | ✓ | Planned start date. |
| `finish` | ISO date | ✓ | Planned finish / due date. |
| `planned_hours` | float | ✓ | Planned effort in hours (feeds PV/BAC). |
| `actual_hours` | float | ✓ | Logged effort in hours. |
| `blocked` | boolean | ✓ | Whether the task is actively blocked. |
| `dependency_ids` | string | – | Semi-colon delimited predecessor task ids. |

## Risk Register (`risks.csv`)
| Column | Type | Required | Description |
| ------ | ---- | -------- | ----------- |
| `id` | string | ✓ | Unique risk identifier. |
| `summary` | string | ✓ | Risk description. |
| `probability` | float (0-1) | ✓ | Likelihood of occurrence. |
| `impact` | int (1-5) | ✓ | Relative impact score. |
| `owner` | string | ✓ | Mitigation owner. |
| `due` | ISO date | ✓ | Target date for mitigation. |
| `mitigation` | string | – | Planned mitigation narrative. |

## Status Notes (`status_notes.md`)
Markdown document segmented by headings:
```
# Weekly Status Notes – Program Name

## YYYY-MM-DD
- Bullet updates…
```
Each `##` heading records notes for a given day; diffing compares content by date.

## EVM Baseline (`evm_baseline.csv`)
| Column | Type | Required | Description |
| ------ | ---- | -------- | ----------- |
| `date` | ISO date | ✓ | Snapshot date. |
| `pv` | float | ✓ | Planned Value at snapshot date. |
| `ev` | float | ✓ | Earned Value at snapshot date. |
| `ac` | float | ✓ | Actual Cost at snapshot date. |

## Earned Value Formulas
- **SPI = EV ÷ PV** (schedule performance). SPI < 1 signals schedule pressure.
- **CPI = EV ÷ AC** (cost performance). CPI < 1 signals cost overrun.
- **SV = EV – PV** (schedule variance in hours). Negative values indicate slippage.
- **CV = EV – AC** (cost variance in hours). Negative values indicate overspend.
- **BAC = Σ planned_hours** (budget at completion proxy).
- **EAC = AC + (BAC – EV) ÷ CPI** (estimate at completion).
- **ETC = EAC – AC** (estimate to complete).
- **VAC = BAC – EAC** (variance at completion).

Tooltips within the UI link back to this document to reinforce transparency.

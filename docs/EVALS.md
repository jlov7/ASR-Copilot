# Evaluation Strategy

## Objectives
- Ensure analytics correctness (EVM, risk scoring, diffs).
- Guard against regressions in data ingestion and export flows.
- Measure latency and resource utilization for local demo viability.
- Track perceived ROI improvements via UX instrumentation (future).

## Evaluation Types
1. **Functional Accuracy**
   - pytest unit tests for EVM formulas, risk severity, diff summaries.
   - Golden-file tests for status pack Markdown structure.
2. **Integration Tests**
   - API contract tests using httpx/pytest to confirm schema adherence.
   - Frontend Vitest tests hitting mocked API responses.
3. **Performance Checks**
   - Measure ingestion + analytics latency on sample dataset (<1.5s target).
   - Export pipeline should complete within 3s for sample data.
4. **UX/Accessibility Checks**
   - Cypress/Playwright smoke (future) to validate keyboard navigation.
   - eslint-plugin-jsx-a11y enforced during linting.

## Metrics & Targets
| Metric | Tool | Target |
| ------ | ---- | ------ |
| CPI/SPI accuracy delta | pytest numeric comparison | ±2% vs baseline |
| Risk ranking stability | pytest sorted order check | Deterministic order per severity, due date |
| API response time | integration test timer | P95 < 500ms for cached results |
| Export success rate | scripted run | 100% success across 5 runs |
| Frontend bundle size | Vite build stats | < 1.5 MB gzipped |
| ROI preset regression | pytest + Vitest snapshot | Low/Medium/High presets within ±5% of baselines |

## ROI Scenario Table
| Scenario | Preset | Time Saved % | Frequency % | Expected Annual Savings Check |
| -------- | ------ | ------------ | ----------- | ----------------------------- |
| Base PMO | Medium | 100% | 100% | Matches stored baseline value |
| Optimistic automation | Medium | 120% | 110% | ≥ baseline × 1.32 |
| High complexity stress | High | 100% | 120% | ≥ $250k annualized |
| Low complexity conservative | Low | 80% | 90% | ≤ baseline × 0.75 |

## Regression Suite Trigger
- Pre-commit runs unit + lint.
- GitHub Actions workflow executes `pytest`, `npm run test`, `npm run lint`, and export smoke.

## Data for Testing
- `data/samples/` used as canonical dataset.
- Synthetic risk cases to ensure heatmap coverage (varied probability/impact).

## Reporting
- Store evaluation artifacts under `out/evals/<timestamp>/` for extended runs.
- Summaries appended to `docs/CHANGELOG.md` per release.

## Roadmap
- Add scenario-based evals (upload malformed CSV, re-import previous day).
- Introduce coverage tooling (coverage.py, c8) for backend/frontend.
- Integrate accessibility automated tooling (axe) in CI.

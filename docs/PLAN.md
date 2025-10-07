# Execution Plan – ASR Copilot POC (2 Weeks)

## Timeline Overview
| Week | Milestones |
| ---- | ---------- |
| Week 1 | Finalize architecture/design docs; scaffold backend/frontend; implement ingestion pipeline; ship EVM & risk engines with unit tests; sample data ready. |
| Week 2 | Complete React dashboard (onboarding, skeletons, ROI view); integrate exports + adapters; harden security/compliance docs; finalize CI/tooling; polish demo script. |

## Detailed Work Breakdown
### Week 1
- Validate requirements, confirm data schemas, and socialize product vision.
- Scaffold repository structure, create documentation suite, seed sample datasets.
- Implement FastAPI service skeleton with Pydantic models and Safe Mode flag.
- Build EVM calculator, risk scoring, diff engine; cover with pytest.
- Implement local persistence (JSON cache) and ROI assumption storage.

### Week 2
- Build React SPA: landing, onboarding tour, dashboard cards, ROI calculator.
- Implement skeleton loaders, empty/error states, accessibility instrumentation.
- Harden ROI experience with complexity presets (low/medium/high) and sensitivity sliders tied to backend multipliers.
- Hook up adapters (mock default) and safe toggles; wire Slack export stub.
- Build status pack exporter (Markdown + PNG), connect export button.
- Add run scripts, lint/test automation, GitHub Actions skeleton, pre-commit config.
- Finalize documentation (UX, security, compliance, evals) and demo choreography.

## Critical Path
1. Backend ingestion & analytics (blocks frontend data bindings).
2. Frontend dashboard (blocks demo readiness).
3. Export pipeline (blocks acceptance criteria on status pack).

## Risks & Mitigations
| Risk | Probability | Impact | Mitigation |
| ---- | ----------- | ------ | ---------- |
| React scope creep delays UI polish | Medium | High | Leverage component library stubs, prioritize core dashboard first, add stretch goals later. |
| EVM formulas misaligned with sample data | Low | High | Unit-test against canonical PM textbook examples; validate with baseline CSV. |
| Export pipeline flaky on different OS | Medium | Medium | Use pure-Python matplotlib and file-safe names; include tests to verify file creation. |
| Tooling friction (Node/Python versions) | Medium | Medium | Document prerequisites clearly; provide run scripts with validation checks. |

## Dependencies & Assumptions
- Local execution environment with Python 3.10+, Node 18+, and no firewall blocking localhost.
- Sample data accepted as authoritative truth for demo scenarios.
- Users comfortable running shell scripts; README covers alternatives when not.

## Acceptance Criteria Recap
- Demo script completes end-to-end without manual intervention.
- Exported Status Pack contains RAG, EVM, Top risks, and changes sections.
- Tests and lint pass via `pytest` and `npm run test` / `npm run lint`.
- Documentation covers PRD, UX, onboarding, security, compliance, evals, architecture, agents, changelog.

## Demo Run Script (Summary)
1. Execute `app/scripts/run_demo.sh`.
2. Walk product tour, load sample data, highlight dashboard insights.
3. Trigger export, inspect `/out/` output, showcase ROI adjustments.

## Next Steps (Post-POC)
- Expand adapter coverage (Jira JQL filters, Slack attachments, ServiceNow queries).
- Add portfolio rollup with multi-project dashboards.
- Integrate live notifications and team collaboration features.

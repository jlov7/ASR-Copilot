# Changelog

## v0.1.0 – Initial POC Release
- ✅ Documentation suite established (PRD, PLAN, UX, ONBOARDING, SECURITY, COMPLIANCE, EVALS, ARCHITECTURE, AGENTS, UX copy).
- ✅ FastAPI + React scaffold with deterministic analytics and Safe Mode.
- ✅ Sample datasets bundled for backlog, risks, status notes, and EVM baseline.
- ✅ EVM calculator, risk scoring engine, diff storyteller, ROI view.
- ✅ Jira live adapter scaffolding with JQL filter + ROI presets/sliders + enriched network modernization sample data.
- ✅ Status Pack export to Markdown + PNG; mock Slack adapter stubbed.
- ✅ Run scripts, pytest coverage, lint/format tooling, GitHub Actions skeleton.

### Demo Cues
1. Start `./app/scripts/run_demo.sh` and confirm Safe Mode banner.
2. Walk through onboarding tour (5 steps) and load sample data.
3. Highlight CPI < 1 and SPI slightly < 1 to showcase schedule warning.
4. Review Risk heatmap—call out high probability/high impact item and suggested mitigation.
5. Show "What changed" list (new risk added, mitigation updated, status note diff).
6. Adjust ROI assumption (increase frequency) and show updated annual savings.
7. Export Status Pack, open generated Markdown, and preview PNG charts.
8. Wrap with compliance story: Safe Mode, local-first storage, documented controls.

## v0.2.0 – Demo polish & agentic upgrades
- 🎯 Added `WHY.md`, EVM primer, extending guide, demo script, roadmap, and screenshot gallery quick links.
- 🧭 Guided tour now shows progress breadcrumbs, replay link, and an onboarding checklist.
- 🧊 Empty state tiles narrate the demo path (load sample, upload data, Safe Mode primer).
- 📈 Dashboard cards include “Explain this” microcopy; export toast offers reveal + copy actions.
- 🔄 Automation loop tab visualizes Ingestion → Analytics → Narrative → Export with dry-run simulator.
- 🛡️ Safe Mode banner upgraded with contextual link; adapters panel controls mock/live modes and sanity checks.
- 🗂️ Added compose.yaml, Makefile helpers, devcontainer, and Windows PowerShell demo script for zero-friction setups.
- 📝 Introduced CODEOWNERS, issue/PR templates, and contribution hygiene updates.
- 🧪 Dashboard tests updated; automation loop logged in `logs/automation_loop.json` for auditability.

# Onboarding & First-Run Experience

## First-Run Flow
1. **Welcome Splash**: Displays value proposition and buttons: "Start guided tour" and "Load sample data".
2. **Guided Tour (5 steps)**:
   - Step 1: Landing screen – explains file upload options, highlights Safe Mode indicator.
   - Step 2: Status header – describes RAG score, CPI/SPI gauges, schedule risk banner.
   - Step 3: Risk watchlist – shows severity chips and mitigation insights.
   - Step 4: "What changed" timeline – demonstrates how daily updates are summarized.
   - Step 5: ROI view – encourages tailoring assumptions and exporting the Status Pack.
3. **Completion**: Tour completion triggers confetti micro-animation, marks onboarding_complete flag in localStorage, and surfaces "Next steps" checklist.

## Sample Data CTA
- Button text: "Try with sample data".
- Action: Calls `/api/demo/load` endpoint to copy sample CSV/MD into cache and return computed dashboard payload.
- Success: Notifies user with toast "Sample program loaded (updated today)" and scrolls to dashboard.

## In-App Checklist
- Items (with checkboxes):
  1. Upload your backlog CSV.
  2. Upload risk register CSV.
  3. Paste weekly status notes.
  4. Review ROI scenario.
  5. Export status pack.
- Displayed in sidebar until all items marked complete; persisted in localStorage.

## Empty State Copy
- **Dashboard Empty**: "No data yet. Upload your CSVs or try the sample program to see ASR Copilot in action." CTA buttons for upload and sample data.
- **ROI Empty**: "We need at least one upload to estimate time saved." Provide link to sample data and doc describing assumptions.

## Error Handling
- Upload validation: Show inline list of issues (e.g., missing columns), link to `/docs/PRD.md` schema appendix.
- Backend failure: Display banner "We hit a snag while processing your data" with `Retry` and `Download logs` (captures JSON error message).
- Export failure: Show modal with steps to verify write permissions to `/out/`.

## Re-Onboarding
- "Replay tour" button in footer resets onboarding flags and restarts guided tour.
- Detects when dataset schema changes and prompts to revisit onboarding if necessary.


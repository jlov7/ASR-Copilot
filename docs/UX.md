# UX Design – ASR Copilot

## User Journeys
1. **First-Time PM (No credentials)**
   - Launch app → Landing screen explains value prop.
   - Click "Start guided tour" → 5-step modal overlays highlight upload, dashboard, ROI, export, adapters.
   - Use "Load sample data" button → Dashboard populates with skeleton loaders transitioning to data.
   - Review RAG banner, EVM gauges, risks, ROI → Export status pack.
2. **Returning PM (Daily check-in)**
   - Landing remembers recent dataset (local cache) and prompts to refresh.
   - Dashboard shows "Last updated" timestamp, "What changed" callout, and next steps.
   - Adjust ROI assumptions if process changes; optionally toggle Safe Mode off to prep adapters.
3. **PMO Lead (Demo)**
   - Skips tour, uploads fresh CSV/MD exports.
   - Uses risk heatmap to discuss mitigation sequencing and uses Slack export (if configured).

## Information Architecture
- **Global layout**: Top nav (ASR Copilot logo, Safe Mode toggle, Export), left onboarding actions, main content area with accessible sections.
- **Dashboard sections (top-to-bottom)**:
  1. Status header (RAG state, CPI/SPI summary, schedule risk flag).
  2. KPI strip with cards (PV, EV, AC, EAC, ETC) and tooltips describing formulas.
  3. Risk watchlist (Top 5, severity × imminence, mitigation text, due date chips).
  4. Risk heatmap (probability vs impact) with keyboard focusable points.
  5. "What changed" timeline (timeline view of added/updated items, diff highlights).
  6. ROI calculator (editable assumptions, time saved per task, annualized savings graph).

## State Handling
- **Empty states**: Friendly illustrations (text) with CTA "Load sample data" or "Upload files".
- **Skeleton loaders**: Pulse placeholders for cards, table rows, and chart frames while data fetch resolves.
- **Error recovery**: Inline banners with summary, detail, and "Retry" button; fallback instructions to check file format.

## Accessibility
- WCAG AA color palette with 4.5:1 contrast minimum.
- All interactive elements keyboard accessible; focus outlines visible.
- ARIA landmarks (`main`, `header`, `nav`) and role annotations for charts.
- Text equivalents for charts (summary paragraphs below heatmap and gauges).
- Tour steps support `Esc` to exit; focus traps within modal.

## Component Inventory
- `StatusHeader` (RAG badge, metrics overview).
- `KpiGauge` (CPI/SPI, accessible description, color-coded thresholds).
- `MetricCard` (PV, EV, AC, etc.).
- `RiskList` (Top 5 table with severity chips and mitigation text).
- `RiskHeatmap` (SVG scatter with tooltips + keyboard nav).
- `ChangesTimeline` (diff summary list with icons for added/updated/resolved).
- `RoiCalculator` (complexity presets, sensitivity sliders, assumption inputs, savings output).
- `OnboardingTour` (Modal with 5 steps, checkboxes to mark complete).
- `FileUploadPanel` (drag/drop CSV or select).
- `StatusPackButton` (triggers export, shows spinner while running).
- `SafeModeToggle` (Switch component with tooltip).

## Visual Guidelines
- Primary color: Deep blue (#1245A6). Accent: Amber (#FFB547). Background neutrals (#F5F7FA).
- Error states: Crimson (#C73535). Success: Emerald (#2E8B57).
- Typography: Inter (system fallback), 16px base.
- Use subtle drop shadows for cards; keep spacing 24px grid.

## Microinteractions
- Skeleton placeholders fade into content with 200ms ease-in-out.
- Tour steps use progress dots; final step shows "Done" CTA that marks onboarding complete in localStorage.
- Export button animates with spinner icon and success confirmation toast.
- ROI slider updates savings figure in real time with counting animation.

## Responsiveness
- Minimum width 1024px targeted for desktop demo; degrade gracefully down to 768px with stacked sections.
- Charts adapt to available width; heatmap maintains 3:2 aspect ratio.
- Navigation condenses to icon-only row under 900px.

## Error & Offline Handling
- Backend failures show descriptive message, include `request_id` for logs.
- Upload validation errors highlight offending rows (line number references) when available.
- Safe Mode ensures adapters UI shows "Disabled in Safe Mode" tag.
- Offline detection (navigator.onLine check) triggers banner suggesting reload when connection restored.

# 3-Minute Demo Script

Use this script when you run the Safe Mode demo with bundled sample data. It matches the GIF and screenshots referenced in the README.

## Setup

1. Run `./app/scripts/run_demo.sh` (or `./run_demo.ps1` on Windows) from the repo root.
2. Wait for the browser window to open at `http://127.0.0.1:5173`.
3. Confirm Safe Mode is ON in the header banner.

## Narrative (≈ 3 minutes)

1. **Tour kickoff (0:00–0:30)**  
   - Click **Start guided tour**.  
   - Read the tooltip copy aloud; it narrates the autonomy program storyline.  
   - Mention the “Step X of 5” breadcrumb and replay link for future presenters.

2. **Load sample data (0:30–0:50)**  
   - Click **Load sample program** in the empty-state tiles.  
   - Call out that no credentials are required; everything stays local.

3. **Program health (0:50–1:20)**  
   - Highlight the RAG banner and CPI/SPI gauges.  
   - Tap the **Explain this** icon to show the EVM primer popover.  
   - Note the Safe Mode banner and the Automation Loop checks (Ingest → Analytics → Narrative → Export).

4. **Risk watchlist (1:20–1:45)**  
   - Call out severity, owner, and due-date chips.  
   - Click **Draft mitigation** on the top risk to copy the templated narrative snippet; mention the Automation Loop status checks.

5. **Timeline (1:45–2:15)**  
   - Toggle between **Recent (Top 5)** and **Full history**.  
   - Switch the grouping to **Category** to separate tasks, risks, and notes; highlight the icons for added/updated/removed lines.  
   - Remind presenters they can hit `Shift + ?` to open the shortcuts helper.

6. **ROI panel (2:15–2:45)**  
   - Switch from Medium to High complexity preset.  
   - Adjust the sensitivity sliders and mention copy-to-clipboard for assumptions.

7. **Export pack (2:45–3:00)**  
   - Click **Export Status Pack**.  
   - Point to the toast that shows the file path, “Reveal in Finder/Explorer,” and “Copy Markdown” buttons.

## Wrap-up

Reinforce the autonomy ladder: Assist (today), Orchestrate (pilot), Autopilot (future) as documented in `docs/ROADMAP.md`. Invite stakeholders to review `WHY.md` for the before/after value story.

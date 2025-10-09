# Good First Issues (Ready to Copy into GitHub)

Use these templates to create starter issues that match the polish tasks outlined in the launch checklist. Each issue links back to the relevant docs/sections so new contributors can ramp quickly.

## Issue 1 – Polish README Badges & Metadata
- **Summary:** Ensure README badges, security callouts, and repo description stay in sync with the latest wording.
- **Why:** Signals production quality to first-time visitors.
- **Acceptance:** Badges render without broken URLs; README tagline + metadata text matches GitHub About box; security callout links to `docs/SECURITY.md`.

## Issue 2 – Quickstart Verification Runbook
- **Summary:** Walk through `QUICKSTART.md` and confirm all three paths (Local demo, Codespaces, Render) work end-to-end.
- **Why:** Keeps the instant demo promise credible for non-devs.
- **Acceptance:** Each path documented with screenshots/logs; submit fixes for any drift; update Quickstart doc if steps change.

## Issue 3 – Instant Demo Media Refresh
- **Summary:** Re-record `docs/media/instant-demo.mp4` + GIF when UI changes.
- **Why:** README video is the first impression for execs.
- **Acceptance:** Follow `docs/SCREENSHOTS/README.md` workflow; PR includes updated MP4/GIF plus any screenshot diffs.

## Issue 4 – Accessibility Regression Checks
- **Summary:** Spot-check keyboard-only flows (banner, progress rail, export preview modal) after UI tweaks.
- **Why:** A11y promise is part of the enterprise trust story.
- **Acceptance:** Document findings; file follow-up bugs if focus order or tooltips regress; verify eslint a11y rules stay green.

## Issue 5 – Export Preview UX Enhancements
- **Summary:** Gather feedback on the new preview modal (copy, layout, additional chart metadata).
- **Why:** Preview is a key reassurance step before sharing exports.
- **Acceptance:** Capture user notes, propose actionable tweaks (e.g., add download button), and raise separate PRs if needed.

## Issue 6 – Security & CI Monitoring
- **Summary:** Confirm CodeQL, Scorecard, and Dependabot runs succeed after merges.
- **Why:** Keeps supply-chain hygiene visible for stakeholders.
- **Acceptance:** Record status of the latest runs; open follow-up tasks if there are failing checks or missing permissions.

> Tip: when opening these issues, tag them with `good first issue` and reference the matching section in `README.md` so contributors can self-serve context.

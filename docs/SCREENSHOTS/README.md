# Screenshot Gallery

This folder houses the image assets referenced in the README gallery (`landing.png`, `tour-step.png`, `evm.png`, `risks.png`, `roi.png`, `export-toast.png`). Regenerate these whenever the UI changes so the documentation stays current.

## Refresh workflow

1. Ensure dependencies are installed (`pip install -r requirements.txt` and `npm install` in `app/frontend`).
2. Run the capture helper:
   ```bash
   source .venv/bin/activate  # if not already active
   python -m app.scripts.capture_media
   ```
3. Copy the generated PNGs from `docs/media/` into this directory with the filenames listed above.
4. Commit the updated screenshots alongside any UI changes so reviewers see the latest experience.

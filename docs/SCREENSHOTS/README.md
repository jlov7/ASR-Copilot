# Screenshot Gallery

This folder houses the image assets referenced in the README gallery (`landing.png`, `tour-step.png`, `evm.png`, `risks.png`, `roi.png`, `export-toast.png`) plus the overview GIF (`overview.gif`). Regenerate these whenever the UI changes so the documentation stays current. The video assets for the Instant Demo live in `docs/media/instant-demo.mp4` and `instant-demo.gif`.

## Refresh workflow

1. Ensure dependencies are installed (`pip install -r requirements.txt` and `npm install` in `app/frontend`).
2. Run the capture helper:
   ```bash
   source .venv/bin/activate  # if not already active
   python -m app.scripts.capture_media
   ```
3. Use `ffmpeg` to rebuild the 60-second Instant Demo video + GIF when flows change:
   ```bash
   ffmpeg -y -loop 1 -t 12 -i docs/SCREENSHOTS/tour-step.png \
     -loop 1 -t 12 -i docs/SCREENSHOTS/evm.png \
     -loop 1 -t 12 -i docs/SCREENSHOTS/risks.png \
     -loop 1 -t 12 -i docs/media/dashboard.png \
     -loop 1 -t 12 -i docs/SCREENSHOTS/roi.png \
     -loop 1 -t 12 -i docs/SCREENSHOTS/export-toast.png \
     -filter_complex_script docs/media/instant_demo_filter.txt \
     -map "[outv]" -r 30 -c:v libx264 -pix_fmt yuv420p -movflags +faststart docs/media/instant-demo.mp4
   ffmpeg -y -i docs/media/instant-demo.mp4 -vf "fps=12,scale=960:-1:flags=lanczos" -loop 0 docs/media/instant-demo.gif
   ```
4. Copy the generated PNGs, GIF, and MP4 from `docs/media/` into this directory with the filenames listed above (the script produces higher-fidelity assets than the lightweight placeholders committed here).
5. Commit the updated screenshots alongside any UI changes so reviewers see the latest experience.

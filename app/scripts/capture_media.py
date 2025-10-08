"""Generate real screenshots and demo GIF for documentation."""

from __future__ import annotations

import asyncio
import glob
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import imageio.v2 as imageio
import markdown
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIST = ROOT / "frontend" / "dist"
DOC_MEDIA_DIR = ROOT.parent / "docs" / "media"
OUT_DIR = ROOT.parent / "out"


def ensure_dirs() -> None:
    DOC_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def wait_for_server(url: str, timeout: float = 15.0) -> None:
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url) as response:  # noqa: S310
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"Timeout waiting for {url}")


async def main() -> None:
    ensure_dirs()

    # Seed sample data
    subprocess.run([sys.executable, "-m", "app.scripts.seed_data"], check=True, cwd=ROOT.parent)

    # Start backend and static server
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    static_server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "4173", "--directory", str(FRONTEND_DIST)],
        cwd=ROOT.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_for_server("http://127.0.0.1:8000/healthz")
        wait_for_server("http://127.0.0.1:4173")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--force-device-scale-factor=1.5"])
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=1.5,
            )
            page = await context.new_page()

            # Load dashboard and sample data
            await page.goto("http://127.0.0.1:4173", wait_until="networkidle")
            skip_button = page.get_by_role("button", name="Skip tour")
            if await skip_button.is_visible(timeout=1000):
                await skip_button.click()
                await page.wait_for_timeout(200)
            await page.evaluate("localStorage.setItem('asr_onboarding_complete','done')")
            await page.get_by_role("button", name="Try with sample data").click()
            await page.wait_for_timeout(2000)
            roi_heading = page.get_by_role("heading", name="Show me the ROI")
            await roi_heading.wait_for(timeout=10000)
            await roi_heading.scroll_into_view_if_needed()
            await page.wait_for_timeout(250)

            dashboard_path = DOC_MEDIA_DIR / "dashboard.png"
            await page.screenshot(path=str(dashboard_path), full_page=True)

            # Export status pack
            await page.get_by_role("button", name="Export Status Pack").first.click()
            await page.wait_for_timeout(2000)

            markdown_files = sorted(OUT_DIR.glob("status_pack_*.md"), key=os.path.getmtime)
            if not markdown_files:
                raise RuntimeError("No status pack generated")
            latest_md = markdown_files[-1]
            status_html = DOC_MEDIA_DIR / "status_pack_preview.html"
            html_content = markdown.markdown(
                latest_md.read_text(encoding="utf-8"),
                extensions=["tables", "fenced_code"],
            )
            status_html.write_text(
                """<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; color: #0b1f4b; }
h1, h2, h3 { color: #1245a6; }
table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
th, td { border: 1px solid #d0d8f5; padding: 8px; text-align: left; }
code { background: #f7f9ff; padding: 2px 4px; border-radius: 4px; }
</style></head><body>"""
                + html_content
                + "</body></html>",
                encoding="utf-8",
            )

            await page.goto(status_html.as_uri(), wait_until="networkidle")
            await page.wait_for_timeout(500)
            status_pack_path = DOC_MEDIA_DIR / "status-pack.png"
            await page.screenshot(path=str(status_pack_path), full_page=True)

            frames: list[Path] = []

            async def snapshot(name: str) -> Path:
                temp_path = DOC_MEDIA_DIR / name
                await page.screenshot(path=str(temp_path), full_page=True)
                return temp_path

            await page.goto("http://127.0.0.1:4173", wait_until="networkidle")
            await page.wait_for_selector('text="Start guided tour"')
            skip_button = page.get_by_role("button", name="Skip tour")
            if await skip_button.is_visible(timeout=1000):
                await skip_button.click()
                await page.wait_for_timeout(200)
            await page.evaluate("localStorage.setItem('asr_onboarding_complete','done')")
            frames.append(await snapshot("frame-tour.png"))
            await page.get_by_role("button", name="Start guided tour").click()
            await page.wait_for_timeout(500)
            frames.append(await snapshot("frame-tour-step.png"))
            await page.get_by_role("button", name="Skip tour").click()
            await page.wait_for_timeout(500)
            await page.get_by_role("button", name="Try with sample data").click()
            await page.wait_for_timeout(1200)
            frames.append(await snapshot("frame-dashboard.png"))

            gif_frames = [imageio.imread(frame) for frame in frames]
            gif_path = DOC_MEDIA_DIR / "demo-flow.gif"
            imageio.mimsave(gif_path, gif_frames, duration=1.0)

            for frame in frames:
                frame.unlink(missing_ok=True)
            status_html.unlink(missing_ok=True)

            await context.close()
    finally:
        for proc in (static_server, backend):
            proc.terminate()
        for proc in (static_server, backend):
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

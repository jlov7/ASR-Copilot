"""Minimal smoke test for status pack export."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.backend.config import get_settings
from app.backend.services import cache
from app.backend.services.ingestion import load_sample_dataset
from app.backend.services.status import build_dashboard_payload
from app.core.status_pack import generate_status_pack


def main() -> None:
    settings = get_settings()
    snapshot = cache.load_current(settings)
    if snapshot is None:
        snapshot = load_sample_dataset(settings)
        cache.save_snapshot(settings, snapshot)
    payload = build_dashboard_payload(settings, snapshot)
    result = generate_status_pack(payload, settings.out_dir)
    print(f"Markdown: {result.markdown_path}")
    print(f"Charts: {result.chart_paths}")


if __name__ == "__main__":
    main()

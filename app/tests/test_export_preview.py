from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.backend.config import Settings
from app.backend.services import cache
from app.backend.services.samples import load_guided_dataset
from app.backend.services.status import build_dashboard_payload
from app.core.status_pack import generate_status_pack_preview


def test_generate_status_pack_preview(tmp_path) -> None:
    settings = Settings(
        data_dir=Path("data/samples"),
        cache_dir=tmp_path / "cache",
        out_dir=tmp_path / "out",
        log_dir=tmp_path / "logs",
    )
    settings.ensure_directories()

    snapshot = load_guided_dataset(
        settings,
        scenario="5g",
        seed=7,
        timestamp=datetime(2024, 6, 3, 17, 45, 0),
    )
    cache.save_snapshot(settings, snapshot)

    payload = build_dashboard_payload(settings, snapshot)
    preview = generate_status_pack_preview(payload)

    assert preview.dataset_hash == snapshot.dataset_hash
    assert "Executive Summary" in preview.markdown
    assert len(preview.charts) == 2
    for chart in preview.charts:
        assert chart.data_uri.startswith("data:image/png;base64,")
        assert chart.name

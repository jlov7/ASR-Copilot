from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.encoders import jsonable_encoder

from app.backend.config import Settings
from app.backend.services import cache
from app.backend.services.samples import load_guided_dataset
from app.backend.services.status import build_dashboard_payload


def _round_floats(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, list):
        return [_round_floats(item) for item in value]
    if isinstance(value, dict):
        return {key: _round_floats(item) for key, item in value.items()}
    return value


def _sanitize_payload(payload) -> dict[str, Any]:
    encoded = jsonable_encoder(payload)
    return _round_floats(encoded)


@pytest.mark.parametrize("scenario", ["5g"])
def test_guided_scenario_matches_golden(tmp_path, scenario: str) -> None:
    """Ensure guided scenarios stay deterministic for executive demos."""
    cache_dir = tmp_path / "cache"
    out_dir = tmp_path / "out"
    log_dir = tmp_path / "logs"
    settings = Settings(
        data_dir=Path("data/samples"),
        cache_dir=cache_dir,
        out_dir=out_dir,
        log_dir=log_dir,
    )
    settings.ensure_directories()

    snapshot = load_guided_dataset(
        settings,
        scenario,
        seed=42,
        timestamp=datetime(2024, 3, 15, 12, 0, 0),
    )
    cache.save_snapshot(settings, snapshot)

    payload = build_dashboard_payload(settings, snapshot)
    sanitized = _sanitize_payload(payload)

    golden_path = Path("out/golden") / f"dashboard_{scenario}.json"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))

    assert sanitized == expected

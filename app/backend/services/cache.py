"""Dataset cache utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.backend.config import Settings
from app.backend.models import DatasetSnapshot


def _load(path: Path) -> Optional[DatasetSnapshot]:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return DatasetSnapshot.parse_obj(payload)


def load_current(settings: Settings) -> Optional[DatasetSnapshot]:
    """Load the latest dataset snapshot from disk."""
    return _load(settings.current_snapshot_path)


def load_previous(settings: Settings) -> Optional[DatasetSnapshot]:
    """Load the previous dataset snapshot for diffing."""
    return _load(settings.previous_snapshot_path)


def save_snapshot(settings: Settings, snapshot: DatasetSnapshot) -> None:
    """Persist dataset snapshot and rotate previous snapshot."""
    current_path = settings.current_snapshot_path
    previous_path = settings.previous_snapshot_path
    if current_path.exists():
        current_payload = json.loads(current_path.read_text(encoding="utf-8"))
        previous_path.write_text(json.dumps(current_payload, indent=2), encoding="utf-8")
    current_path.write_text(snapshot.json(indent=2), encoding="utf-8")


def purge(settings: Settings) -> None:
    """Delete cached snapshots."""
    for path in (settings.current_snapshot_path, settings.previous_snapshot_path):
        if path.exists():
            path.unlink()

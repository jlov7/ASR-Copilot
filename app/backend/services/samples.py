"""Guided sample dataset loader utilities."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import HTTPException

from app.backend.config import Settings
from app.backend.models import DatasetSnapshot
from app.backend.services.ingestion import (
    compute_dataset_hash,
    parse_baseline,
    parse_risks,
    parse_status_notes,
    parse_tasks,
)

GUIDED_DIR_NAME = "guided"
GUIDED_BASE_TIMESTAMP = datetime(2024, 3, 15, 12, 0, 0)

# Slugs for guided scenarios surfaced in the UI.
SCENARIO_ALIASES: dict[str, str] = {
    "5g": "5g",
    "cloud": "cloud",
    "cpe": "cpe",
}


def _guided_root(settings: Settings) -> Path:
    """Return the directory that houses guided scenario datasets."""
    return (settings.data_dir.parent / GUIDED_DIR_NAME).resolve()


def list_guided_scenarios(settings: Settings) -> Iterable[str]:
    """Yield scenario identifiers that have datasets on disk."""
    root = _guided_root(settings)
    if not root.exists():
        return []
    return sorted(
        entry.name
        for entry in root.iterdir()
        if entry.is_dir() and (entry / "tasks.csv").exists()
    )


def _scenario_dir(settings: Settings, scenario: str) -> Path:
    slug = SCENARIO_ALIASES.get(scenario.lower())
    if not slug:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown guided scenario '{scenario}'. Available: {', '.join(sorted(SCENARIO_ALIASES))}.",
        )
    root = _guided_root(settings)
    path = (root / slug).resolve()
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Guided scenario assets missing for '{scenario}'. Expected at {path}.",
        )
    return path


def _timestamp_for_seed(seed: int | None) -> datetime:
    """Derive a deterministic timestamp for a guided scenario based on seed."""

    if seed is None:
        return GUIDED_BASE_TIMESTAMP
    minutes = int(seed) % (14 * 24 * 60)  # wrap every two weeks
    return (GUIDED_BASE_TIMESTAMP + timedelta(minutes=minutes)).replace(microsecond=0)


def load_guided_dataset(
    settings: Settings,
    scenario: str,
    *,
    seed: int | None = None,
    timestamp: datetime | None = None,
) -> DatasetSnapshot:
    """Load a guided scenario dataset into a snapshot."""
    scenario_dir = _scenario_dir(settings, scenario)
    tasks_path = scenario_dir / "tasks.csv"
    risks_path = scenario_dir / "risks.csv"
    notes_path = scenario_dir / "status_notes.md"
    baseline_path = scenario_dir / "evm_baseline.csv"

    missing = [
        str(path)
        for path in (tasks_path, risks_path, notes_path, baseline_path)
        if not path.exists()
    ]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Guided scenario '{scenario}' missing required files: {', '.join(missing)}",
        )

    tasks = parse_tasks(tasks_path.read_bytes())
    risks = parse_risks(risks_path.read_bytes())
    notes = parse_status_notes(notes_path.read_text(encoding="utf-8"))
    baseline = parse_baseline(baseline_path.read_bytes())

    dataset_hash = compute_dataset_hash(tasks, risks, notes)
    resolved_timestamp = (timestamp or _timestamp_for_seed(seed)).replace(microsecond=0)

    snapshot = DatasetSnapshot(
        tasks=tasks,
        risks=risks,
        status_notes=notes,
        baseline=baseline,
        dataset_hash=dataset_hash,
        last_updated=resolved_timestamp,
    )
    return snapshot

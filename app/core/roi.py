"""ROI calculation helpers."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import List, Tuple

from app.backend.models import (
    RoiAssumption,
    RoiModifiers,
    RoiPreset,
    RoiSnapshot,
)

DEFAULT_PRESET = "medium"
DEFAULT_MODIFIERS = RoiModifiers(time_saved_multiplier=1.0, frequency_multiplier=1.0)


def _assumptions(*entries: RoiAssumption) -> List[RoiAssumption]:
    return [entry.copy(deep=True) for entry in entries]


PRESET_LIBRARY: dict[str, dict] = {
    "low": {
        "label": "Low complexity PMO",
        "description": "Single tower delivery, monthly reporting cadence, minimal executive formatting.",
        "assumptions": _assumptions(
            RoiAssumption(
                task_name="Status assembly",
                frequency_per_month=2,
                hours_saved=2.5,
                pm_hourly_cost=85,
                team_size=1,
            ),
            RoiAssumption(
                task_name="Risk register grooming",
                frequency_per_month=1,
                hours_saved=1.5,
                pm_hourly_cost=85,
                team_size=1,
            ),
            RoiAssumption(
                task_name="Executive deck formatting",
                frequency_per_month=0.5,
                hours_saved=3,
                pm_hourly_cost=95,
                team_size=1,
            ),
        ),
    },
    "medium": {
        "label": "Medium complexity PMO",
        "description": "Three workstreams, weekly status cycles, standard exec read-out.",
        "assumptions": _assumptions(
            RoiAssumption(
                task_name="Status assembly",
                frequency_per_month=4,
                hours_saved=4,
                pm_hourly_cost=95,
                team_size=1,
            ),
            RoiAssumption(
                task_name="Risk register grooming",
                frequency_per_month=2,
                hours_saved=2.5,
                pm_hourly_cost=95,
                team_size=1,
            ),
            RoiAssumption(
                task_name="Executive deck formatting",
                frequency_per_month=1,
                hours_saved=6,
                pm_hourly_cost=105,
                team_size=1,
            ),
            RoiAssumption(
                task_name="Stakeholder escalation prep",
                frequency_per_month=1,
                hours_saved=3,
                pm_hourly_cost=105,
                team_size=1,
            ),
        ),
    },
    "high": {
        "label": "High complexity PMO",
        "description": "Multi-region launch with weekly steering and heavy executive packaging.",
        "assumptions": _assumptions(
            RoiAssumption(
                task_name="Status assembly",
                frequency_per_month=6,
                hours_saved=5,
                pm_hourly_cost=110,
                team_size=2,
            ),
            RoiAssumption(
                task_name="Risk register grooming",
                frequency_per_month=4,
                hours_saved=3.5,
                pm_hourly_cost=105,
                team_size=2,
            ),
            RoiAssumption(
                task_name="Executive deck formatting",
                frequency_per_month=2,
                hours_saved=7,
                pm_hourly_cost=120,
                team_size=2,
            ),
            RoiAssumption(
                task_name="Steering committee analytics",
                frequency_per_month=2,
                hours_saved=4,
                pm_hourly_cost=120,
                team_size=2,
            ),
        ),
    },
}


def _available_presets() -> List[RoiPreset]:
    presets: List[RoiPreset] = []
    for name, meta in PRESET_LIBRARY.items():
        presets.append(
            RoiPreset(
                name=name,
                label=meta["label"],
                description=meta["description"],
                assumptions=[assumption.copy(deep=True) for assumption in meta["assumptions"]],
            )
        )
    return presets


def _preset_assumptions(preset: str) -> List[RoiAssumption]:
    meta = PRESET_LIBRARY.get(preset) or PRESET_LIBRARY[DEFAULT_PRESET]
    return [assumption.copy(deep=True) for assumption in meta["assumptions"]]


def _default_state() -> Tuple[str, RoiModifiers, List[RoiAssumption]]:
    return DEFAULT_PRESET, DEFAULT_MODIFIERS.copy(deep=True), _preset_assumptions(DEFAULT_PRESET)


def load_state(path: Path) -> Tuple[str, RoiModifiers, List[RoiAssumption]]:
    """Load ROI state from disk with backwards-compatible fallback."""
    if not path.exists():
        return _default_state()

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict):
        preset = payload.get("preset", DEFAULT_PRESET)
        modifiers_payload = payload.get("modifiers", {})
        assumptions_payload = payload.get("assumptions", [])
        modifiers = RoiModifiers(
            time_saved_multiplier=float(modifiers_payload.get("time_saved_multiplier", 1.0)),
            frequency_multiplier=float(modifiers_payload.get("frequency_multiplier", 1.0)),
        )
        assumptions = [RoiAssumption(**entry) for entry in assumptions_payload] or _preset_assumptions(preset)
        return preset, modifiers, assumptions

    # Legacy format (list of assumptions only)
    assumptions = [RoiAssumption(**entry) for entry in payload]
    preset, modifiers, _ = _default_state()
    return preset, modifiers, assumptions


def save_state(
    path: Path,
    preset: str,
    modifiers: RoiModifiers,
    assumptions: Iterable[RoiAssumption],
) -> None:
    """Persist ROI state to disk."""
    payload = {
        "preset": preset,
        "modifiers": modifiers.dict(),
        "assumptions": [assumption.dict() for assumption in assumptions],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def compute_roi(
    preset: str,
    modifiers: RoiModifiers,
    assumptions: Iterable[RoiAssumption],
) -> RoiSnapshot:
    """Calculate monthly and annual savings for the given ROI state."""
    assumption_list = [assumption.copy(deep=True) for assumption in assumptions]
    total_annual = 0.0
    total_hours = 0.0

    for assumption in assumption_list:
        adjusted_frequency = assumption.frequency_per_month * modifiers.frequency_multiplier
        adjusted_hours_saved = assumption.hours_saved * modifiers.time_saved_multiplier
        annual_occurrences = adjusted_frequency * 12
        hours_saved = adjusted_hours_saved * annual_occurrences * assumption.team_size
        total_hours += hours_saved
        total_annual += hours_saved * assumption.pm_hourly_cost

    monthly_savings = total_annual / 12
    return RoiSnapshot(
        annual_savings=round(total_annual, 2),
        monthly_savings=round(monthly_savings, 2),
        total_hours_saved=round(total_hours, 2),
        assumptions=assumption_list,
        selected_preset=preset,
        modifiers=modifiers,
        available_presets=_available_presets(),
    )

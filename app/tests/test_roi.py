from __future__ import annotations

from app.backend.models import RoiAssumption, RoiModifiers
from app.core import roi as roi_core


def test_compute_roi_applies_modifiers():
    assumptions = [
        RoiAssumption(
            task_name="Status assembly",
            frequency_per_month=2,
            hours_saved=4,
            pm_hourly_cost=100,
            team_size=1,
        )
    ]
    modifiers = RoiModifiers(time_saved_multiplier=1.2, frequency_multiplier=1.1)
    snapshot = roi_core.compute_roi("medium", modifiers, assumptions)

    adjusted_frequency = 2 * 1.1
    adjusted_hours = 4 * 1.2
    annual_occurrences = adjusted_frequency * 12
    expected_hours = adjusted_hours * annual_occurrences * 1
    expected_annual = expected_hours * 100

    assert snapshot.total_hours_saved == round(expected_hours, 2)
    assert snapshot.annual_savings == round(expected_annual, 2)
    assert snapshot.modifiers.time_saved_multiplier == 1.2
    assert snapshot.available_presets


def test_save_and_load_state_roundtrip(tmp_path):
    path = tmp_path / "roi_state.json"
    assumptions = [
        RoiAssumption(
            task_name="Exec deck",
            frequency_per_month=1.5,
            hours_saved=5,
            pm_hourly_cost=120,
            team_size=1,
        )
    ]
    modifiers = RoiModifiers(time_saved_multiplier=0.9, frequency_multiplier=1.05)
    roi_core.save_state(path, preset="high", modifiers=modifiers, assumptions=assumptions)

    preset, loaded_modifiers, loaded_assumptions = roi_core.load_state(path)
    assert preset == "high"
    assert loaded_modifiers.time_saved_multiplier == modifiers.time_saved_multiplier
    assert loaded_assumptions[0].task_name == "Exec deck"

"""Earned Value Management (EVM) calculations."""

from __future__ import annotations

from datetime import date
from typing import Iterable, Optional, Tuple

from app.backend.models import EvmBaselinePoint, Task


STATUS_WEIGHTS = {
    "Not Started": 0.0,
    "In Progress": 0.5,
    "Complete": 1.0,
    "Blocked": 0.25,
}


def _latest_baseline(
    baseline: Iterable[EvmBaselinePoint],
) -> Optional[EvmBaselinePoint]:
    """Return the most recent baseline point, if available."""
    try:
        return max(baseline, key=lambda point: point.date)
    except ValueError:
        return None


def _weighted_ev(tasks: Iterable[Task]) -> float:
    """Compute earned value by weighting planned hours by task completion."""
    ev_total = 0.0
    for task in tasks:
        weight = STATUS_WEIGHTS.get(task.status, 0.0)
        ev_total += task.planned_hours * weight
    return round(ev_total, 2)


def _actual_cost(tasks: Iterable[Task]) -> float:
    """Compute actual cost as the sum of recorded actual hours."""
    return round(sum(task.actual_hours for task in tasks), 2)


def _planned_value(
    baseline: Optional[EvmBaselinePoint], tasks: Iterable[Task]
) -> Tuple[float, date]:
    """Determine planned value and associated baseline date."""
    if baseline is not None:
        return round(baseline.pv, 2), baseline.date
    # Fallback: use total planned hours as-of today when baseline missing.
    total_planned = round(sum(task.planned_hours for task in tasks), 2)
    return total_planned, date.today()


def calculate_metrics(
    tasks: Iterable[Task],
    baseline: Iterable[EvmBaselinePoint],
) -> dict:
    """Calculate core EVM metrics."""
    task_list = list(tasks)
    baseline_list = list(baseline)
    latest_baseline = _latest_baseline(baseline_list)

    pv, baseline_date = _planned_value(latest_baseline, task_list)
    ev = _weighted_ev(task_list)
    ac = _actual_cost(task_list)
    sv = round(ev - pv, 2)
    cv = round(ev - ac, 2)
    spi = round(ev / pv, 3) if pv else None
    cpi = round(ev / ac, 3) if ac else None
    bac = round(sum(task.planned_hours for task in task_list), 2)

    eac = None
    etc = None
    vac = None
    if cpi:
        eac = round(ac + ((bac - ev) / cpi), 2)
        etc = round(eac - ac, 2)
        vac = round(bac - eac, 2)

    return {
        "pv": pv,
        "ev": ev,
        "ac": ac,
        "sv": sv,
        "cv": cv,
        "spi": spi,
        "cpi": cpi,
        "bac": bac,
        "eac": eac,
        "etc": etc,
        "vac": vac,
        "baseline_date": baseline_date,
    }

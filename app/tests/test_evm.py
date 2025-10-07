from datetime import date

import pytest

from app.backend.models import EvmBaselinePoint, Task
from app.core.evm import calculate_metrics


def _sample_tasks() -> list[Task]:
    return [
        Task(
            id="T101",
            title="Integrate autonomy stack",
            owner="Ana Gomez",
            status="In Progress",
            start_date=date(2023, 9, 1),
            finish_date=date(2023, 9, 30),
            planned_hours=120,
            actual_hours=110,
            blocked=False,
            dependency_ids=[],
        ),
        Task(
            id="T102",
            title="Field testing prep",
            owner="Marco Lee",
            status="Complete",
            start_date=date(2023, 9, 5),
            finish_date=date(2023, 9, 20),
            planned_hours=80,
            actual_hours=78,
            blocked=False,
            dependency_ids=["T101"],
        ),
        Task(
            id="T103",
            title="Vendor alignment",
            owner="Sophia Patel",
            status="In Progress",
            start_date=date(2023, 9, 10),
            finish_date=date(2023, 9, 25),
            planned_hours=60,
            actual_hours=35,
            blocked=True,
            dependency_ids=["T101"],
        ),
        Task(
            id="T104",
            title="Telecom compliance forms",
            owner="Jerry Wu",
            status="Not Started",
            start_date=date(2023, 9, 15),
            finish_date=date(2023, 10, 5),
            planned_hours=55,
            actual_hours=0,
            blocked=False,
            dependency_ids=[],
        ),
        Task(
            id="T105",
            title="Sprint 18 demo",
            owner="Leah Chen",
            status="Complete",
            start_date=date(2023, 9, 18),
            finish_date=date(2023, 9, 27),
            planned_hours=40,
            actual_hours=45,
            blocked=False,
            dependency_ids=["T102"],
        ),
        Task(
            id="T106",
            title="Operations handoff deck",
            owner="Olivia Park",
            status="In Progress",
            start_date=date(2023, 9, 20),
            finish_date=date(2023, 10, 10),
            planned_hours=70,
            actual_hours=20,
            blocked=False,
            dependency_ids=["T102"],
        ),
        Task(
            id="T107",
            title="Latency optimization",
            owner="Kai Nair",
            status="Complete",
            start_date=date(2023, 9, 12),
            finish_date=date(2023, 9, 22),
            planned_hours=65,
            actual_hours=68,
            blocked=False,
            dependency_ids=["T101"],
        ),
    ]


def test_calculate_metrics_matches_expected():
    tasks = _sample_tasks()
    baseline = [
        EvmBaselinePoint(
            date=date(2023, 9, 27),
            pv=380,
            ev=325,
            ac=345,
        )
    ]
    metrics = calculate_metrics(tasks, baseline)
    assert metrics["pv"] == 380
    assert metrics["ev"] == 310  # weighted EV from tasks
    assert metrics["ac"] == 356
    assert metrics["sv"] == -70
    assert metrics["cv"] == -46
    assert metrics["spi"] == pytest.approx(0.816, rel=1e-3)
    assert metrics["cpi"] == pytest.approx(0.871, rel=1e-3)
    assert metrics["bac"] == 490
    assert metrics["eac"] == pytest.approx(562.66, rel=1e-3)
    assert metrics["etc"] == pytest.approx(206.66, rel=1e-3)
    assert metrics["vac"] == pytest.approx(-72.66, rel=1e-3)
    assert metrics["baseline_date"] == date(2023, 9, 27)

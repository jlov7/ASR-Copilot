from datetime import date, datetime

from app.backend.models import DatasetSnapshot, EvmBaselinePoint, Risk, StatusNote, Task
from app.core.diffs import generate_changes


def _snapshot(tasks, risks, notes, timestamp: datetime) -> DatasetSnapshot:
    return DatasetSnapshot(
        tasks=tasks,
        risks=risks,
        status_notes=notes,
        baseline=[EvmBaselinePoint(date=date(2023, 9, 27), pv=380, ev=320, ac=340)],
        dataset_hash="hash",
        last_updated=timestamp,
    )


def test_generate_changes_detects_add_update_remove():
    prev = _snapshot(
        tasks=[
            Task(
                id="T1",
                title="Legacy task",
                owner="Ana",
                status="In Progress",
                start_date=date(2023, 9, 1),
                finish_date=date(2023, 9, 10),
                planned_hours=20,
                actual_hours=10,
                blocked=False,
                dependency_ids=[],
            )
        ],
        risks=[
            Risk(
                id="R1",
                summary="Legacy risk",
                probability=0.4,
                impact=4,
                owner="Marco",
                due_date=date(2023, 9, 30),
                mitigation=None,
            )
        ],
        notes=[
            StatusNote(
                date=date(2023, 9, 20),
                content="Initial note.",
            )
        ],
        timestamp=datetime(2023, 9, 27, 10, 0, 0),
    )

    current = _snapshot(
        tasks=[
            Task(
                id="T1",
                title="Legacy task",
                owner="Ana",
                status="Complete",
                start_date=date(2023, 9, 1),
                finish_date=date(2023, 9, 10),
                planned_hours=20,
                actual_hours=18,
                blocked=False,
                dependency_ids=[],
            ),
            Task(
                id="T2",
                title="New task",
                owner="Leah",
                status="Not Started",
                start_date=date(2023, 9, 15),
                finish_date=date(2023, 9, 25),
                planned_hours=30,
                actual_hours=0,
                blocked=False,
                dependency_ids=[],
            ),
        ],
        risks=[],
        notes=[
            StatusNote(
                date=date(2023, 9, 20),
                content="Initial note modified.",
            )
        ],
        timestamp=datetime(2023, 9, 28, 9, 0, 0),
    )

    changes = generate_changes(prev, current)
    change_types = {(item.entity_type, item.change_type) for item in changes.items}
    assert ("task", "updated") in change_types
    assert ("task", "added") in change_types
    assert ("risk", "removed") in change_types
    assert ("note", "updated") in change_types
    assert changes.has_changes

from datetime import date, datetime
from pathlib import Path

from app.backend.config import Settings
from app.backend.models import DatasetSnapshot, EvmBaselinePoint, Risk, StatusNote, Task
from app.backend.services import automation


def _make_settings(tmp_path: Path) -> Settings:
    settings = Settings(
        cache_dir=tmp_path / ".cache",
        out_dir=tmp_path / "out",
        log_dir=tmp_path / "logs",
        data_dir=Path("data/samples"),
    )
    settings.ensure_directories()
    return settings


def _sample_snapshot(timestamp: datetime) -> DatasetSnapshot:
    tasks = [
        Task(
            id="T1",
            title="Network backbone rollout",
            owner="Ana",
            status="In Progress",
            start_date=date(2024, 1, 1),
            finish_date=date(2024, 1, 31),
            planned_hours=120,
            actual_hours=60,
            blocked=False,
            dependency_ids=[],
        )
    ]
    risks = [
        Risk(
            id="R1",
            summary="Vendor slip on radios",
            probability=0.6,
            impact=4,
            owner="Marco",
            due_date=date(2024, 1, 20),
            mitigation="Escalate to vendor PM",
        )
    ]
    notes = [
        StatusNote(
            date=date(2024, 1, 5),
            author="Leah",
            content="## Progress\n- Backbone install is on track",
        )
    ]
    baseline = [
        EvmBaselinePoint(date=date(2024, 1, 10), pv=120, ev=90, ac=70)
    ]
    return DatasetSnapshot(
        tasks=tasks,
        risks=risks,
        status_notes=notes,
        baseline=baseline,
        dataset_hash="hash1234",
        last_updated=timestamp,
    )


def test_record_dataset_refresh_creates_run(tmp_path):
    settings = _make_settings(tmp_path)
    snapshot = _sample_snapshot(datetime.utcnow())

    status = automation.record_dataset_refresh(settings, snapshot, trigger="upload")

    assert status.trigger == "upload"
    assert status.last_run is not None
    assert any(step.key == "ingestion" and step.status == "ok" for step in status.steps)
    assert any(step.key == "export" and step.status == "pending" for step in status.steps)


def test_record_export_result_updates_latest_run(tmp_path):
    settings = _make_settings(tmp_path)
    snapshot = _sample_snapshot(datetime.utcnow())
    automation.record_dataset_refresh(settings, snapshot, trigger="upload")

    status = automation.record_export_result(
        settings,
        status="ok",
        note="Markdown status_pack.md; Charts status_pack.png; Posted to Slack.",
        duration_ms=850,
    )

    export_step = next(step for step in status.steps if step.key == "export")
    assert export_step.status == "ok"
    assert "Markdown" in (export_step.note or "")
    assert export_step.duration_ms == 850

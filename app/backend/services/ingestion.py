"""CSV/Markdown ingestion utilities."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from fastapi import HTTPException, UploadFile

from app.backend.config import Settings
from app.backend.models import (
    DatasetSnapshot,
    EvmBaselinePoint,
    Risk,
    StatusNote,
    Task,
    UploadResponse,
)

REQUIRED_TASK_COLUMNS = {
    "id",
    "title",
    "owner",
    "status",
    "start",
    "finish",
    "planned_hours",
    "actual_hours",
    "blocked",
    "dependency_ids",
}

REQUIRED_RISK_COLUMNS = {
    "id",
    "summary",
    "probability",
    "impact",
    "owner",
    "due",
    "mitigation",
}

REQUIRED_BASELINE_COLUMNS = {"date", "pv", "ev", "ac"}


def _ensure_columns(name: str, csv_columns: Iterable[str], required: set[str]) -> None:
    missing = required - set(csv_columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"{name} missing required columns: {', '.join(sorted(missing))}",
        )


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "y"}


def _parse_dependencies(field: str) -> List[str]:
    if not field:
        return []
    parts = re.split(r"[;|]", field)
    return [item.strip() for item in parts if item.strip()]


def _load_csv_bytes(upload_file: UploadFile) -> bytes:
    content = upload_file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail=f"{upload_file.filename} is empty.")
    return content


def _decode_csv(content: bytes) -> List[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="Provided CSV has no rows.")
    return rows


def parse_tasks(content: bytes) -> List[Task]:
    rows = _decode_csv(content)
    _ensure_columns("tasks.csv", rows[0].keys(), REQUIRED_TASK_COLUMNS)
    tasks: List[Task] = []
    for row in rows:
        try:
            tasks.append(
                Task(
                    id=row["id"].strip(),
                    title=row["title"].strip(),
                    owner=row["owner"].strip() or "Unassigned",
                    status=row["status"].strip(),
                    start_date=date.fromisoformat(row["start"].strip()),
                    finish_date=date.fromisoformat(row["finish"].strip()),
                    planned_hours=float(row["planned_hours"]),
                    actual_hours=float(row.get("actual_hours") or 0.0),
                    blocked=_parse_bool(row.get("blocked", "false")),
                    dependency_ids=_parse_dependencies(row.get("dependency_ids", "")),
                )
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=422,
                detail=f"Invalid task row for id {row.get('id')}: {exc}",
            ) from exc
    return tasks


def parse_risks(content: bytes) -> List[Risk]:
    rows = _decode_csv(content)
    _ensure_columns("risks.csv", rows[0].keys(), REQUIRED_RISK_COLUMNS)
    risks: List[Risk] = []
    for row in rows:
        try:
            risks.append(
                Risk(
                    id=row["id"].strip(),
                    summary=row["summary"].strip(),
                    probability=float(row["probability"]),
                    impact=int(row["impact"]),
                    owner=row["owner"].strip(),
                    due_date=date.fromisoformat(row["due"].strip()),
                    mitigation=(row.get("mitigation") or "").strip() or None,
                )
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=422,
                detail=f"Invalid risk row for id {row.get('id')}: {exc}",
            ) from exc
    return risks


def parse_baseline(content: bytes) -> List[EvmBaselinePoint]:
    rows = _decode_csv(content)
    _ensure_columns("evm_baseline.csv", rows[0].keys(), REQUIRED_BASELINE_COLUMNS)
    baseline: List[EvmBaselinePoint] = []
    for row in rows:
        try:
            baseline.append(
                EvmBaselinePoint(
                    date=date.fromisoformat(row["date"].strip()),
                    pv=float(row["pv"]),
                    ev=float(row["ev"]),
                    ac=float(row["ac"]),
                )
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=422,
                detail=f"Invalid baseline row for date {row.get('date')}: {exc}",
            ) from exc
    return baseline


def parse_status_notes(content: str) -> List[StatusNote]:
    lines = content.splitlines()
    notes: List[StatusNote] = []
    current_date: Optional[date] = None
    buffer: List[str] = []
    for line in lines:
        if line.startswith("## "):
            if current_date:
                notes.append(
                    StatusNote(
                        date=current_date,
                        content="\n".join(buffer).strip(),
                    )
                )
            buffer = []
            raw_date = line.removeprefix("## ").strip()
            try:
                current_date = date.fromisoformat(raw_date)
            except ValueError as exc:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid status note date heading: {raw_date}",
                ) from exc
        elif line.startswith("#"):
            continue
        else:
            buffer.append(line)
    if current_date:
        notes.append(
            StatusNote(
                date=current_date,
                content="\n".join(buffer).strip(),
            )
        )
    if not notes:
        # fallback to treat entire content as single note
        notes.append(
            StatusNote(
                date=date.today(),
                content=content.strip(),
            )
        )
    return notes


def _compute_dataset_hash(tasks: List[Task], risks: List[Risk], notes: List[StatusNote]) -> str:
    payload = {
        "tasks": [task.dict() for task in tasks],
        "risks": [risk.dict() for risk in risks],
        "notes": [note.dict() for note in notes],
    }
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_dataset_hash(tasks: List[Task], risks: List[Risk], notes: List[StatusNote]) -> str:
    """Expose deterministic dataset hash computation for snapshot builders."""

    return _compute_dataset_hash(tasks, risks, notes)


def ingest_payload(
    tasks_file: UploadFile,
    risks_file: UploadFile,
    status_notes_file: UploadFile,
    baseline_file: UploadFile,
) -> DatasetSnapshot:
    tasks = parse_tasks(_load_csv_bytes(tasks_file))
    risks = parse_risks(_load_csv_bytes(risks_file))
    baseline = parse_baseline(_load_csv_bytes(baseline_file))
    notes_bytes = status_notes_file.file.read()
    if not notes_bytes:
        raise HTTPException(status_code=400, detail="Status notes file is empty.")
    notes = parse_status_notes(notes_bytes.decode("utf-8"))
    dataset_hash = _compute_dataset_hash(tasks, risks, notes)
    snapshot = DatasetSnapshot(
        tasks=tasks,
        risks=risks,
        status_notes=notes,
        baseline=baseline,
        dataset_hash=dataset_hash,
        last_updated=datetime.utcnow(),
    )
    return snapshot


def load_sample_dataset(settings: Settings) -> DatasetSnapshot:
    """Load dataset from bundled sample files."""
    tasks_path = settings.data_dir / "tasks.csv"
    risks_path = settings.data_dir / "risks.csv"
    notes_path = settings.data_dir / "status_notes.md"
    baseline_path = settings.data_dir / "evm_baseline.csv"

    missing = [path for path in (tasks_path, risks_path, notes_path, baseline_path) if not path.exists()]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Sample data missing: {', '.join(str(path) for path in missing)}",
        )

    tasks = parse_tasks(tasks_path.read_bytes())
    risks = parse_risks(risks_path.read_bytes())
    notes = parse_status_notes(notes_path.read_text(encoding="utf-8"))
    baseline = parse_baseline(baseline_path.read_bytes())
    dataset_hash = _compute_dataset_hash(tasks, risks, notes)
    return DatasetSnapshot(
        tasks=tasks,
        risks=risks,
        status_notes=notes,
        baseline=baseline,
        dataset_hash=dataset_hash,
        last_updated=datetime.utcnow(),
    )


def to_upload_response(snapshot: DatasetSnapshot) -> UploadResponse:
    """Convert snapshot to API-friendly upload response."""
    return UploadResponse(
        dataset_hash=snapshot.dataset_hash,
        task_count=len(snapshot.tasks),
        risk_count=len(snapshot.risks),
        note_dates=[note.date for note in snapshot.status_notes],
        baseline_points=len(snapshot.baseline),
        last_updated=snapshot.last_updated,
    )

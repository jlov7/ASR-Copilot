"""Diff engine for tasks, risks, and status notes."""

from __future__ import annotations

from datetime import datetime
from difflib import unified_diff
from typing import Dict, List, Optional, Tuple

from app.backend.models import (
    ChangeItem,
    ChangesSummary,
    DatasetSnapshot,
    Risk,
    StatusNote,
    Task,
)


def _task_signature(task: Task) -> Tuple:
    return (
        task.title,
        task.owner,
        task.status,
        task.start_date,
        task.finish_date,
        task.planned_hours,
        task.actual_hours,
        task.blocked,
        tuple(task.dependency_ids),
    )


def _risk_signature(risk: Risk) -> Tuple:
    return (
        risk.summary,
        risk.probability,
        risk.impact,
        risk.owner,
        risk.due_date,
        risk.mitigation,
    )


def _note_signature(note: StatusNote) -> Tuple:
    return (note.author, note.content.strip())


def _compare_maps(
    prev: Dict[str, Tuple],
    curr: Dict[str, Tuple],
    entity_type: str,
    titles: Dict[str, str],
    change_timestamp: datetime,
) -> List[ChangeItem]:
    changes: List[ChangeItem] = []
    for entity_id, signature in curr.items():
        if entity_id not in prev:
            changes.append(
                ChangeItem(
                    id=entity_id,
                    entity_type=entity_type,  # type: ignore[arg-type]
                    change_type="added",
                    title=titles[entity_id],
                    detail="New entry added.",
                    timestamp=change_timestamp,
                )
            )
        elif prev[entity_id] != signature:
            changes.append(
                ChangeItem(
                    id=entity_id,
                    entity_type=entity_type,  # type: ignore[arg-type]
                    change_type="updated",
                    title=titles[entity_id],
                    detail="Updated fields detected.",
                    timestamp=change_timestamp,
                )
            )

    for entity_id in prev:
        if entity_id not in curr:
            changes.append(
                ChangeItem(
                    id=entity_id,
                    entity_type=entity_type,  # type: ignore[arg-type]
                    change_type="removed",
                    title=titles.get(entity_id, entity_id),
                    detail="Entry removed from latest upload.",
                    timestamp=change_timestamp,
                )
            )
    return changes


def _note_diff(previous: Optional[str], current: str) -> str:
    if not previous:
        return "New note added."
    diff_lines = unified_diff(
        previous.splitlines(),
        current.splitlines(),
        lineterm="",
    )
    formatted = "\n".join(diff_lines)
    return formatted or "No textual differences found."


def generate_changes(
    previous: Optional[DatasetSnapshot],
    current: DatasetSnapshot,
) -> ChangesSummary:
    """Produce a comparison summary between two dataset snapshots."""
    if previous is None:
        return ChangesSummary(
            items=[
                ChangeItem(
                    id="initial-load",
                    entity_type="note",
                    change_type="added",
                    title="Initial dataset",
                    detail="First dataset uploaded; baselining established.",
                    timestamp=current.last_updated,
                )
            ],
            has_changes=True,
        )

    changes: List[ChangeItem] = []
    timestamp = current.last_updated

    prev_tasks = {task.id: _task_signature(task) for task in previous.tasks}
    curr_tasks = {task.id: _task_signature(task) for task in current.tasks}
    task_titles = {task.id: task.title for task in current.tasks + previous.tasks}
    changes.extend(
        _compare_maps(prev_tasks, curr_tasks, "task", task_titles, timestamp)
    )

    prev_risks = {risk.id: _risk_signature(risk) for risk in previous.risks}
    curr_risks = {risk.id: _risk_signature(risk) for risk in current.risks}
    risk_titles = {
        risk.id: risk.summary for risk in current.risks + previous.risks
    }
    changes.extend(
        _compare_maps(prev_risks, curr_risks, "risk", risk_titles, timestamp)
    )

    prev_notes = {note.date.isoformat(): _note_signature(note) for note in previous.status_notes}
    curr_notes = {note.date.isoformat(): _note_signature(note) for note in current.status_notes}
    all_dates = set(prev_notes) | set(curr_notes)
    for note_date in sorted(all_dates):
        current_entry = curr_notes.get(note_date)
        previous_entry = prev_notes.get(note_date)
        if current_entry and not previous_entry:
            changes.append(
                ChangeItem(
                    id=note_date,
                    entity_type="note",
                    change_type="added",
                    title=f"Status note {note_date}",
                    detail="New status note recorded.",
                    timestamp=timestamp,
                )
            )
        elif current_entry and previous_entry and current_entry != previous_entry:
            diff_text = _note_diff(previous_entry[1], current_entry[1])
            changes.append(
                ChangeItem(
                    id=note_date,
                    entity_type="note",
                    change_type="updated",
                    title=f"Status note {note_date}",
                    detail=diff_text,
                    timestamp=timestamp,
                )
            )
        elif previous_entry and not current_entry:
            changes.append(
                ChangeItem(
                    id=note_date,
                    entity_type="note",
                    change_type="removed",
                    title=f"Status note {note_date}",
                    detail="Status note removed from latest upload.",
                    timestamp=timestamp,
                )
            )

    return ChangesSummary(
        items=sorted(changes, key=lambda item: item.timestamp, reverse=True),
        has_changes=bool(changes),
    )

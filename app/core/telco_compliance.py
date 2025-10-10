"""Telco compliance signal mapping for the dashboard."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable, List

from app.backend.models import (
    ComplianceChecklistItem,
    ComplianceCountdown,
    CompliancePanel,
    DatasetSnapshot,
)


def _reference_date(snapshot: DatasetSnapshot) -> date:
    candidates: List[date] = [snapshot.last_updated.date()]
    if snapshot.status_notes:
        candidates.append(max(note.date for note in snapshot.status_notes))
    if snapshot.baseline:
        candidates.append(max(point.date for point in snapshot.baseline))
    return max(candidates)


def _project_start(snapshot: DatasetSnapshot) -> date:
    if snapshot.tasks:
        return min(task.start_date for task in snapshot.tasks)
    return snapshot.last_updated.date()


def _status_from_remaining(days_remaining: int) -> str:
    if days_remaining <= 0:
        return "red"
    if days_remaining <= 30:
        return "amber"
    return "green"


def _has_phrase(haystacks: Iterable[str], phrase: str) -> bool:
    needle = phrase.lower()
    return any(needle in text.lower() for text in haystacks)


def build_telco_compliance(snapshot: DatasetSnapshot) -> CompliancePanel:
    """Produce FCC shot clock and permitting checklist signals."""
    reference_date = _reference_date(snapshot)
    project_start = _project_start(snapshot)
    days_elapsed = max(0, (reference_date - project_start).days)

    collocation_deadline = project_start + timedelta(days=90)
    new_site_deadline = project_start + timedelta(days=150)
    collocation_remaining = max(0, (collocation_deadline - reference_date).days)
    new_site_remaining = max(0, (new_site_deadline - reference_date).days)

    shot_clocks = [
        ComplianceCountdown(
            key="fcc_collocation_90",
            label="FCC Shot Clock – 90 days (collocation)",
            deadline=collocation_deadline,
            days_remaining=collocation_remaining,
            status=_status_from_remaining(collocation_remaining),
            description="Track collocation modifications under the 90-day FCC requirement.",
        ),
        ComplianceCountdown(
            key="fcc_new_site_150",
            label="FCC Shot Clock – 150 days (new site)",
            deadline=new_site_deadline,
            days_remaining=new_site_remaining,
            status=_status_from_remaining(new_site_remaining),
            description="New site builds must close out permitting within 150 days or risk timelines slipping.",
        ),
    ]

    note_texts = [note.content for note in snapshot.status_notes]
    has_section_106 = _has_phrase(note_texts, "section 106") or _has_phrase(note_texts, "nepa")
    has_eligible_facilities = _has_phrase(note_texts, "6409") or _has_phrase(note_texts, "eligible facilities")
    has_structural = _has_phrase(note_texts, "structural") or _has_phrase(note_texts, "engineering calc")
    has_power = _has_phrase(note_texts, "power") or _has_phrase(note_texts, "utility")

    checklist = [
        ComplianceChecklistItem(
            key="nepa_section_106",
            label="NEPA / Section 106 correspondence logged",
            status="complete" if has_section_106 else "pending",
            owner="Permitting Lead" if has_section_106 else "Permitting Lead",
            action="Upload the latest SHPO/THPO correspondence to keep audit trails tight.",
        ),
        ComplianceChecklistItem(
            key="eligible_facilities",
            label="6409(a) eligibility documented",
            status="complete" if has_eligible_facilities else "pending",
            owner="Regulatory Counsel",
            action="Confirm eligible facilities memo is filed to maintain expedited handling.",
        ),
        ComplianceChecklistItem(
            key="structural",
            label="Structural calculations attached",
            status="pending" if has_structural else "missing",
            owner="Engineering",
            action="Drop structural calcs and stamped drawings for the construction packet.",
        ),
        ComplianceChecklistItem(
            key="power_service",
            label="Power service / inspection scheduled",
            status="pending" if has_power else "missing",
            owner="Field Operations",
            action="Coordinate with the utility to secure inspection and power turn-up dates.",
        ),
    ]

    return CompliancePanel(
        shot_clocks=shot_clocks,
        checklist=checklist,
        last_reviewed=reference_date,
    )

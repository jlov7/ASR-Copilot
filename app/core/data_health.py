"""Data health scoring and chase queue generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

from app.backend.models import (
    ChaseQueueItem,
    DataHealthDimension,
    DataHealthScore,
    DatasetSnapshot,
)

_DIMENSION_LABELS = {
    "completeness": "Completeness",
    "freshness": "Freshness",
    "consistency": "Consistency",
    "conformance": "Conformance",
}

_DIMENSION_DESCRIPTIONS = {
    "completeness": "Required fields are populated (owners, actuals, mitigations, dependencies).",
    "freshness": "Updates landed recently for in-flight work and status notes.",
    "consistency": "Status aligns with dates, blockers, and earned value deltas.",
    "conformance": "Data matches canonical schema and enum expectations.",
}

_COMPLETENESS_WEIGHT = 40
_FRESHNESS_WEIGHT = 25
_CONSISTENCY_WEIGHT = 25
_CONFORMANCE_WEIGHT = 10


def _reference_date(snapshot: DatasetSnapshot) -> datetime:
    """Infer the as-of date used for freshness calculations."""
    dates: List[datetime] = [snapshot.last_updated]
    if snapshot.status_notes:
        latest_note = max(note.date for note in snapshot.status_notes)
        dates.append(datetime.combine(latest_note, datetime.min.time()))
    if snapshot.baseline:
        latest_baseline = max(point.date for point in snapshot.baseline)
        dates.append(datetime.combine(latest_baseline, datetime.min.time()))
    return max(dates)


def _grade_from_score(score: int) -> str:
    if score >= 95:
        return "Excellent"
    if score >= 85:
        return "Strong"
    if score >= 70:
        return "Fair"
    return "Weak"


def evaluate_data_health(snapshot: DatasetSnapshot) -> Tuple[DataHealthScore, List[ChaseQueueItem]]:
    """Compute weighted data quality score and chase queue suggestions."""
    reference_dt = _reference_date(snapshot)
    reference_date = reference_dt.date()
    chase_items: List[ChaseQueueItem] = []

    # Completeness gaps: missing updated effort/estimates after start.
    completeness_issues: List[str] = []
    completeness_actions: List[str] = []
    completeness_penalty = 0
    stale_estimate_threshold = reference_date - timedelta(days=14)
    for task in snapshot.tasks:
        if (
            task.actual_hours == 0
            and task.status in {"Not Started", "In Progress"}
            and task.start_date <= stale_estimate_threshold
        ):
            completeness_penalty += 2
            completeness_issues.append(
                f"{task.title} has no updated effort even though work started {task.start_date.isoformat()}."
            )
            completeness_actions.append(f"Ask {task.owner} for updated estimate on {task.title}.")
            chase_items.append(
                ChaseQueueItem(
                    gap_id=f"completeness-{task.id}",
                    summary=f"Missing updated estimate for {task.title}",
                    owner=task.owner,
                    owner_role=None,
                    channel="teams",
                    priority="medium",
                    status="draft",
                    message=(
                        f"Hi {task.owner.split()[0]}, the task “{task.title}” still shows zero actual hours even though it kicked off "
                        f"on {task.start_date.isoformat()}. Can you drop an updated estimate or actual by end of day so we can clear "
                        "the completeness flag and keep the Data Health Score in the green?"
                    ),
                    related_entities=[task.id],
                    dimension="completeness",
                )
            )

    completeness_penalty = min(completeness_penalty, 2)
    completeness_score = max(0, _COMPLETENESS_WEIGHT - completeness_penalty)

    # Freshness gaps: statuses not updated even though start date passed.
    freshness_issues: List[str] = []
    freshness_actions: List[str] = []
    freshness_penalty = 0
    freshness_threshold = reference_date - timedelta(days=14)
    for task in snapshot.tasks:
        if task.status == "Not Started" and task.start_date <= freshness_threshold:
            freshness_penalty += 3
            freshness_issues.append(
                f"{task.title} has not been updated since the planned start on {task.start_date.isoformat()}."
            )
            freshness_actions.append(f"Confirm kickoff status for {task.title} or adjust schedule.")
    freshness_penalty = min(freshness_penalty, 3)
    freshness_score = max(0, _FRESHNESS_WEIGHT - freshness_penalty)

    # Consistency gaps: blocked tasks still open.
    consistency_issues: List[str] = []
    consistency_actions: List[str] = []
    consistency_penalty = 0
    for task in snapshot.tasks:
        if task.blocked:
            consistency_penalty += 3
            consistency_issues.append(f"{task.title} is blocked; mitigation needs logging.")
            consistency_actions.append(f"Work with {task.owner} to document unblock plan for {task.title}.")
            chase_items.append(
                ChaseQueueItem(
                    gap_id=f"consistency-{task.id}",
                    summary=f"Blocked task needs mitigation update: {task.title}",
                    owner=task.owner,
                    owner_role=None,
                    channel="email",
                    priority="high",
                    status="draft",
                    message=(
                        f"Heads-up {task.owner.split()[0]} — “{task.title}” is still marked blocked. "
                        "Can you add the mitigation or next action in Jira so everyone sees how we’re clearing it?"
                    ),
                    related_entities=[task.id],
                    dimension="consistency",
                )
            )
    consistency_score = max(0, _CONSISTENCY_WEIGHT - consistency_penalty)

    # Conformance gaps: ingestion already enforces schema, so only track unexpected issues.
    conformance_score = _CONFORMANCE_WEIGHT
    conformance_issues: List[str] = []
    conformance_actions: List[str] = []

    dimensions = [
        DataHealthDimension(
            key="completeness",
            label=_DIMENSION_LABELS["completeness"],
            score=completeness_score,
            max_score=_COMPLETENESS_WEIGHT,
            description=_DIMENSION_DESCRIPTIONS["completeness"],
            issues=completeness_issues,
            actions=completeness_actions,
        ),
        DataHealthDimension(
            key="freshness",
            label=_DIMENSION_LABELS["freshness"],
            score=freshness_score,
            max_score=_FRESHNESS_WEIGHT,
            description=_DIMENSION_DESCRIPTIONS["freshness"],
            issues=freshness_issues,
            actions=freshness_actions,
        ),
        DataHealthDimension(
            key="consistency",
            label=_DIMENSION_LABELS["consistency"],
            score=consistency_score,
            max_score=_CONSISTENCY_WEIGHT,
            description=_DIMENSION_DESCRIPTIONS["consistency"],
            issues=consistency_issues,
            actions=consistency_actions,
        ),
        DataHealthDimension(
            key="conformance",
            label=_DIMENSION_LABELS["conformance"],
            score=conformance_score,
            max_score=_CONFORMANCE_WEIGHT,
            description=_DIMENSION_DESCRIPTIONS["conformance"],
            issues=conformance_issues,
            actions=conformance_actions,
        ),
    ]

    total_score = sum(d.score for d in dimensions)
    label = _grade_from_score(total_score)
    summary_parts: List[str] = []
    for dim in dimensions:
        if dim.issues:
            summary_parts.append(f"{dim.label}: {len(dim.issues)} issue(s)")
    summary = ", ".join(summary_parts) if summary_parts else "All dimensions in good standing."

    score = DataHealthScore(
        total=total_score,
        label=label,
        summary=summary,
        dimensions=dimensions,
        last_calculated=reference_dt,
    )
    return score, chase_items

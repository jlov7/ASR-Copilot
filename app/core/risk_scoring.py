"""Risk scoring utilities."""

from __future__ import annotations

from datetime import date
from typing import Iterable, List

from app.backend.models import Risk, RiskListItem, RiskMatrixPoint, RiskSummary


def _severity(probability: float, impact: int) -> float:
    return round(probability * impact, 2)


def _status_from_severity(value: float) -> str:
    if value >= 2.5:
        return "High"
    if value >= 1.5:
        return "Medium"
    return "Low"


def summarize_risks(risks: Iterable[Risk]) -> RiskSummary:
    """Return sorted risk list and heatmap data."""
    items: List[RiskListItem] = []
    today = date.today()
    for risk in risks:
        sev = _severity(risk.probability, risk.impact)
        days_to_due = (risk.due_date - today).days
        items.append(
            RiskListItem(
                id=risk.id,
                summary=risk.summary,
                probability=risk.probability,
                impact=risk.impact,
                severity=sev,
                due_date=risk.due_date,
                owner=risk.owner,
                mitigation=risk.mitigation,
                status=_status_from_severity(sev),
                days_to_due=days_to_due,
            )
        )

    items.sort(key=lambda item: (-item.severity, item.due_date))
    heatmap = [
        RiskMatrixPoint(
            id=item.id,
            probability=item.probability,
            impact=item.impact,
            severity=item.severity,
            summary=item.summary,
        )
        for item in items
    ]

    return RiskSummary(
        top_risks=items[:5],
        heatmap=heatmap,
        watchlist_size=len(items),
    )

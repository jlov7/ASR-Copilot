from datetime import date

from app.backend.models import Risk
from app.core.risk_scoring import summarize_risks


def test_risk_summary_orders_by_severity():
    risks = [
        Risk(
            id="R1",
            summary="High severity",
            probability=0.6,
            impact=5,
            owner="A",
            due_date=date(2023, 10, 5),
            mitigation="Mitigate",
        ),
        Risk(
            id="R2",
            summary="Medium severity",
            probability=0.3,
            impact=3,
            owner="B",
            due_date=date(2023, 10, 1),
            mitigation=None,
        ),
        Risk(
            id="R3",
            summary="Another high severity",
            probability=0.55,
            impact=5,
            owner="C",
            due_date=date(2023, 10, 2),
            mitigation=None,
        ),
    ]
    summary = summarize_risks(risks)
    assert summary.watchlist_size == 3
    assert summary.top_risks[0].id == "R1"
    assert summary.top_risks[1].id == "R3"
    assert summary.top_risks[0].status == "High"
    assert summary.top_risks[1].status == "High"
    assert summary.heatmap[0].impact == 5


def test_risk_summary_labels_low_risk():
    risk = Risk(
        id="R4",
        summary="Low severity risk",
        probability=0.1,
        impact=2,
        owner="D",
        due_date=date(2023, 10, 10),
        mitigation=None,
    )
    summary = summarize_risks([risk])
    assert summary.top_risks[0].status == "Low"
    assert summary.top_risks[0].severity == 0.2

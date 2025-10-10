"""Dashboard aggregation service."""

from __future__ import annotations

from app.backend.config import Settings
from app.backend.models import (
    DashboardMeta,
    DashboardPayload,
    DatasetSnapshot,
    EvmMetrics,
)
from app.backend.services import automation, cache
from app.core import roi as roi_core
from app.core.diffs import generate_changes
from app.core.evm import calculate_metrics
from app.core.risk_scoring import summarize_risks
from app.core.summarizer import build_narrative
from app.core.data_health import evaluate_data_health
from app.core.telco_compliance import build_telco_compliance


def build_dashboard_payload(
    settings: Settings,
    snapshot: DatasetSnapshot,
) -> DashboardPayload:
    """Compose dashboard data used by frontend + exports."""
    previous_snapshot = cache.load_previous(settings)
    changes = generate_changes(previous_snapshot, snapshot)
    metrics = calculate_metrics(snapshot.tasks, snapshot.baseline)
    evm = EvmMetrics(**metrics)
    risks = summarize_risks(snapshot.risks, as_of=snapshot.last_updated.date())
    preset, modifiers, assumptions = roi_core.load_state(settings.roi_settings_path)
    roi_snapshot = roi_core.compute_roi(preset, modifiers, assumptions)
    narrative = build_narrative(evm, risks, changes)
    meta = DashboardMeta(
        dataset_hash=snapshot.dataset_hash,
        last_updated=snapshot.last_updated,
        safe_mode=settings.safe_mode,
    )
    automation_status = automation.load_status(settings)
    data_health, chase_queue = evaluate_data_health(snapshot)
    compliance = build_telco_compliance(snapshot)
    return DashboardPayload(
        evm=evm,
        risks=risks,
        changes=changes,
        roi=roi_snapshot,
        narrative=narrative,
        meta=meta,
        automation=automation_status,
        data_health=data_health,
        chase_queue=chase_queue,
        compliance=compliance,
    )

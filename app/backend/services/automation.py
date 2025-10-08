"""Automation loop state management and dry-run simulation."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.backend.config import Settings
from app.backend.models import (
    AutomationStatus,
    AutomationStepStatus,
    DashboardMeta,
    DashboardPayload,
    DatasetSnapshot,
    EvmMetrics,
)
from app.backend.services import cache
from app.backend.services.ingestion import load_sample_dataset
from app.core import roi as roi_core
from app.core.diffs import generate_changes
from app.core.evm import calculate_metrics
from app.core.risk_scoring import summarize_risks
from app.core.status_pack import generate_status_pack
from app.core.summarizer import build_narrative

AUTOMATION_STEPS: List[Tuple[str, str]] = [
    ("ingestion", "Ingestion"),
    ("analytics", "Analytics"),
    ("narrative", "Narrative"),
    ("export", "Export"),
]


def _log_path(settings: Settings) -> Path:
    return settings.log_dir / "automation_loop.json"


def _default_status() -> AutomationStatus:
    return AutomationStatus(
        steps=[
            AutomationStepStatus(
                key=key,
                title=title,
                status="pending",
                last_run=None,
                duration_ms=None,
                note=None,
            )
            for key, title in AUTOMATION_STEPS
        ],
        last_run=None,
        trigger="unknown",
    )


def load_status(settings: Settings) -> AutomationStatus:
    """Load the latest automation loop status from disk."""
    path = _log_path(settings)
    if not path.exists():
        return _default_status()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        path.unlink(missing_ok=True)
        return _default_status()

    runs: List[Dict[str, Any]] = data.get("runs") or []
    if not runs:
        return _default_status()

    latest = runs[-1]
    last_run_ts = latest.get("timestamp")
    try:
        last_run = datetime.fromisoformat(last_run_ts) if last_run_ts else None
    except ValueError:
        last_run = None
    trigger = latest.get("trigger", "unknown")
    if trigger not in {"unknown", "upload", "dry_run", "seed"}:
        trigger = "unknown"

    step_payloads: Dict[str, Dict[str, Any]] = {
        step.get("key"): step for step in latest.get("steps", [])
    }
    steps: List[AutomationStepStatus] = []
    for key, title in AUTOMATION_STEPS:
        payload = step_payloads.get(key)
        if payload:
            ts = payload.get("timestamp")
            try:
                step_time = datetime.fromisoformat(ts) if ts else last_run
            except ValueError:
                step_time = last_run
            steps.append(
                AutomationStepStatus(
                    key=key,
                    title=title,
                    status=payload.get("status", "pending"),
                    last_run=step_time,
                    duration_ms=payload.get("duration_ms"),
                    note=payload.get("note"),
                )
            )
        else:
            steps.append(
                AutomationStepStatus(
                    key=key,
                    title=title,
                    status="pending",
                    last_run=None,
                    duration_ms=None,
                    note=None,
                )
            )

    return AutomationStatus(steps=steps, last_run=last_run, trigger=trigger)


def _save_run(settings: Settings, run: Dict[str, Any]) -> None:
    path = _log_path(settings)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {"runs": []}
    else:
        data = {"runs": []}
    runs: List[Dict[str, Any]] = data.setdefault("runs", [])
    runs.append(run)
    data["runs"] = runs[-20:]  # keep last 20 runs
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_dataset_refresh(
    settings: Settings,
    snapshot: DatasetSnapshot,
    trigger: str = "upload",
    previous_snapshot: Optional[DatasetSnapshot] = None,
) -> AutomationStatus:
    """Record a dataset refresh triggered by an upload or seed."""
    now = datetime.utcnow()
    step_records: List[Dict[str, Any]] = []

    step_records.append(
        {
            "key": "ingestion",
            "title": "Ingestion",
            "status": "ok",
            "duration_ms": None,
            "note": f"{len(snapshot.tasks)} tasks, {len(snapshot.risks)} risks, {len(snapshot.status_notes)} notes ingested.",
            "timestamp": now.isoformat(),
        }
    )

    analytics_start = time.perf_counter()
    baseline_snapshot = previous_snapshot if previous_snapshot is not None else cache.load_previous(settings)
    changes = generate_changes(baseline_snapshot, snapshot)
    metrics = calculate_metrics(snapshot.tasks, snapshot.baseline)
    evm = EvmMetrics(**metrics)
    risks_summary = summarize_risks(snapshot.risks, as_of=snapshot.last_updated.date())
    analytics_duration = int((time.perf_counter() - analytics_start) * 1000)
    cpi = f"{evm.cpi:.2f}" if evm.cpi is not None else "n/a"
    spi = f"{evm.spi:.2f}" if evm.spi is not None else "n/a"
    step_records.append(
        {
            "key": "analytics",
            "title": "Analytics",
            "status": "ok",
            "duration_ms": analytics_duration,
            "note": f"CPI {cpi} / SPI {spi}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    narrative_start = time.perf_counter()
    narrative = build_narrative(evm, risks_summary, changes)
    narrative_duration = int((time.perf_counter() - narrative_start) * 1000)
    step_records.append(
        {
            "key": "narrative",
            "title": "Narrative",
            "status": "ok",
            "duration_ms": narrative_duration,
            "note": f"{len(narrative.splitlines())} narrative lines drafted.",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    step_records.append(
        {
            "key": "export",
            "title": "Export",
            "status": "pending",
            "duration_ms": None,
            "note": "Run Export Status Pack to generate Markdown + charts.",
            "timestamp": now.isoformat(),
        }
    )

    run = {
        "timestamp": now.isoformat(),
        "trigger": trigger,
        "steps": step_records,
    }
    _save_run(settings, run)
    return load_status(settings)


def simulate_dry_run(settings: Settings) -> AutomationStatus:
    """Simulate a scheduled run using bundled sample data."""
    now = datetime.utcnow()
    step_records: List[Dict[str, Any]] = []

    ingestion_start = time.perf_counter()
    snapshot = load_sample_dataset(settings)
    ingestion_duration = int((time.perf_counter() - ingestion_start) * 1000)
    step_records.append(
        {
            "key": "ingestion",
            "title": "Ingestion",
            "status": "ok",
            "duration_ms": ingestion_duration,
            "note": f"{len(snapshot.tasks)} tasks and {len(snapshot.risks)} risks parsed.",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    analytics_start = time.perf_counter()
    previous_snapshot = cache.load_current(settings)
    changes = generate_changes(previous_snapshot, snapshot)
    metrics = calculate_metrics(snapshot.tasks, snapshot.baseline)
    evm = EvmMetrics(**metrics)
    risks_summary = summarize_risks(snapshot.risks, as_of=snapshot.last_updated.date())
    analytics_duration = int((time.perf_counter() - analytics_start) * 1000)
    cpi = f"{evm.cpi:.2f}" if evm.cpi is not None else "n/a"
    spi = f"{evm.spi:.2f}" if evm.spi is not None else "n/a"
    step_records.append(
        {
            "key": "analytics",
            "title": "Analytics",
            "status": "ok",
            "duration_ms": analytics_duration,
            "note": f"CPI {cpi} / SPI {spi}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    narrative_start = time.perf_counter()
    narrative = build_narrative(evm, risks_summary, changes)
    narrative_duration = int((time.perf_counter() - narrative_start) * 1000)
    step_records.append(
        {
            "key": "narrative",
            "title": "Narrative",
            "status": "ok",
            "duration_ms": narrative_duration,
            "note": f"{len(narrative.splitlines())} lines drafted for exec summary.",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    preset, modifiers, assumptions = roi_core.load_state(settings.roi_settings_path)
    roi_snapshot = roi_core.compute_roi(preset, modifiers, assumptions)

    export_start = time.perf_counter()
    payload = DashboardPayload(
        evm=evm,
        risks=risks_summary,
        changes=changes,
        roi=roi_snapshot,
        narrative=narrative,
        meta=DashboardMeta(
            dataset_hash=snapshot.dataset_hash,
            last_updated=datetime.utcnow(),
            safe_mode=settings.safe_mode,
        ),
        automation=_default_status(),
    )
    result = generate_status_pack(payload, settings.out_dir, include_markdown=True, include_png=False)
    export_duration = int((time.perf_counter() - export_start) * 1000)
    if result.markdown_path:
        export_note = f"Markdown saved to {Path(result.markdown_path).name}."
    else:
        export_note = "Dry-run export completed."
    step_records.append(
        {
            "key": "export",
            "title": "Export",
            "status": "ok",
            "duration_ms": export_duration,
            "note": export_note,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    run = {
        "timestamp": now.isoformat(),
        "trigger": "dry_run",
        "steps": step_records,
    }
    _save_run(settings, run)
    return load_status(settings)


def record_export_result(
    settings: Settings,
    status: str,
    note: str,
    duration_ms: Optional[int] = None,
) -> AutomationStatus:
    """Update the latest automation run with export results."""
    path = _log_path(settings)
    if not path.exists():
        run = {
            "timestamp": datetime.utcnow().isoformat(),
            "trigger": "unknown",
            "steps": [],
        }
        data = {"runs": [run]}
    else:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {"runs": []}
    runs: List[Dict[str, Any]] = data.setdefault("runs", [])
    if not runs:
        runs.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "trigger": "unknown",
                "steps": [],
            }
        )
    run = runs[-1]
    run["timestamp"] = datetime.utcnow().isoformat()
    steps: List[Dict[str, Any]] = run.setdefault("steps", [])
    export_step = next((step for step in steps if step.get("key") == "export"), None)
    if export_step is None:
        export_step = {"key": "export", "title": "Export"}
        steps.append(export_step)
    export_step.update(
        {
            "title": "Export",
            "status": status,
            "duration_ms": duration_ms,
            "note": note,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    data["runs"] = runs[-20:]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return load_status(settings)

"""Build dataset snapshots from live adapters."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional, Sequence

from app.backend import adapters
from app.backend.config import Settings
from app.backend.models import DatasetSnapshot, EvmBaselinePoint, Risk, StatusNote, Task
from app.backend.services.ingestion import compute_dataset_hash


def _serialize_snapshot(snapshot: DatasetSnapshot, *, sources: dict[str, str | int]) -> tuple[str, str]:
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    payload = {
        "generated_at": timestamp,
        "dataset_hash": snapshot.dataset_hash,
        "sources": sources,
        "snapshot": snapshot.model_dump(mode="json"),
    }
    filename = f"snapshot_{snapshot.dataset_hash[:8]}_{timestamp.replace(':', '').replace('-', '')}.json"
    body = json.dumps(payload, indent=2)
    return filename, body


def _export_snapshot(settings: Settings, snapshot: DatasetSnapshot, *, sources: dict[str, str | int]) -> None:
    filename, body = _serialize_snapshot(snapshot, sources=sources)
    target = os.getenv("ASR_LIVE_EXPORT_TARGET", "disk").lower()

    if target == "disk":
        override_path = os.getenv("ASR_LIVE_EXPORT_PATH")
        base_dir = Path(override_path) if override_path else settings.out_dir / "live"
        base_dir.mkdir(parents=True, exist_ok=True)
        (base_dir / filename).write_text(body, encoding="utf-8")
        return

    if target == "s3":
        bucket = os.getenv("ASR_LIVE_EXPORT_BUCKET")
        if not bucket:
            raise LiveIngestionError("ASR_LIVE_EXPORT_BUCKET must be set for S3 live export.")
        prefix = os.getenv("ASR_LIVE_EXPORT_PREFIX", "").strip("/")
        key = "/".join(part for part in (prefix, filename) if part)
        try:
            import boto3  # type: ignore
        except ImportError as exc:  # pragma: no cover - import guard
            raise LiveIngestionError("boto3 is required for S3 live export. Install boto3 or switch ASR_LIVE_EXPORT_TARGET back to disk.") from exc
        region = os.getenv("ASR_LIVE_EXPORT_REGION")
        client_kwargs: dict[str, str] = {}
        if region:
            client_kwargs["region_name"] = region
        client = boto3.client("s3", **client_kwargs)
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body.encode("utf-8"),
            ContentType="application/json",
        )
        return

    if target == "azure":
        try:
            from azure.storage.blob import BlobClient  # type: ignore
        except ImportError as exc:  # pragma: no cover - import guard
            raise LiveIngestionError(
                "azure-storage-blob is required for Azure live export. Install azure-storage-blob or switch ASR_LIVE_EXPORT_TARGET back to disk."
            ) from exc
        account_url = os.getenv("ASR_LIVE_EXPORT_AZURE_URL")
        container = os.getenv("ASR_LIVE_EXPORT_AZURE_CONTAINER")
        credential = os.getenv("ASR_LIVE_EXPORT_AZURE_CREDENTIAL")
        if not account_url or not container:
            raise LiveIngestionError(
                "ASR_LIVE_EXPORT_AZURE_URL and ASR_LIVE_EXPORT_AZURE_CONTAINER must be set for Azure live export."
            )
        prefix = os.getenv("ASR_LIVE_EXPORT_AZURE_PREFIX", "").strip("/")
        blob_name = "/".join(part for part in (prefix, filename) if part)
        blob = BlobClient(account_url=account_url, container_name=container, blob_name=blob_name, credential=credential)
        blob.upload_blob(body.encode("utf-8"), overwrite=True, content_type="application/json")
        return

    raise LiveIngestionError(f"Unsupported live export target '{target}'.")


class LiveIngestionError(RuntimeError):
    """Raised when live ingestion cannot be completed."""


_STATUS_MAP = {
    "to do": "Not Started",
    "todo": "Not Started",
    "open": "Not Started",
    "backlog": "Not Started",
    "selected for development": "Not Started",
    "in progress": "In Progress",
    "doing": "In Progress",
    "review": "In Progress",
    "qa": "In Progress",
    "blocked": "Blocked",
    "impeded": "Blocked",
    "on hold": "Blocked",
    "done": "Complete",
    "resolved": "Complete",
    "closed": "Complete",
}


def _status_from_jira(value: Optional[str]) -> str:
    if not value:
        return "In Progress"
    normalized = value.strip().lower()
    return _STATUS_MAP.get(normalized, "In Progress")


def _parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _fallback_start(finish: date) -> date:
    return finish - timedelta(days=14)


def _task_planned_hours(raw: dict) -> float:
    planned = raw.get("planned_hours")
    if planned is None:
        return 8.0
    try:
        return max(float(planned), 0.0)
    except (TypeError, ValueError):
        return 8.0


def _task_actual_hours(raw: dict) -> float:
    actual = raw.get("actual_hours")
    if actual is None:
        return 0.0
    try:
        return max(float(actual), 0.0)
    except (TypeError, ValueError):
        return 0.0


def _normalize_tasks(raw_tasks: Sequence[dict], reference: date) -> list[Task]:
    tasks: list[Task] = []
    for item in raw_tasks:
        status = _status_from_jira(item.get("status"))
        due = _parse_iso_date(item.get("due_date")) or reference + timedelta(days=14)
        created = _parse_iso_date(item.get("created")) or _fallback_start(due)
        planned_hours = _task_planned_hours(item)
        actual_hours = _task_actual_hours(item)
        tasks.append(
            Task(
                id=str(item.get("id") or item.get("key") or item.get("issue_key") or item.get("title")),
                title=str(item.get("title") or "Untitled backlog item"),
                owner=item.get("owner") or "Unassigned",
                status=status,  # type: ignore[arg-type]
                start_date=min(created, due),
                finish_date=max(created, due),
                planned_hours=planned_hours,
                actual_hours=actual_hours,
                blocked=status == "Blocked",
                dependency_ids=[],
            )
        )
    return tasks


def _baseline_from_tasks(reference: date, tasks: Iterable[Task]) -> list[EvmBaselinePoint]:
    planned = sum(task.planned_hours for task in tasks)
    actual = sum(task.actual_hours for task in tasks)
    return [
        EvmBaselinePoint(
            date=reference,
            pv=planned,
            ev=0.0,
            ac=actual,
        )
    ]


def _safe_probability(value: Optional[str | float | int]) -> float:
    if value is None:
        return 0.3
    try:
        prob = float(value)
    except (TypeError, ValueError):
        return 0.3
    if prob > 1:
        if prob <= 100:
            prob = prob / 100.0
        else:
            prob = 1.0
    return max(0.0, min(prob, 1.0))


def _safe_impact(value: Optional[str | float | int]) -> int:
    if value is None:
        return 3
    try:
        impact = int(float(value))
    except (TypeError, ValueError):
        return 3
    return max(1, min(impact, 5))


def _due_date_from_record(record: dict, reference: date) -> date:
    for key in ("target_date", "due_date", "expected_close", "planned_end_date", "planned_end"):
        value = record.get(key)
        parsed = _parse_iso_date(value if isinstance(value, str) else None)
        if parsed is not None:
            return parsed
    return reference + timedelta(days=21)


def _owner_from_record(record: dict) -> str:
    for key in ("risk_owner", "assigned_to", "owner", "u_owner"):
        value = record.get(key)
        if isinstance(value, dict):
            display = value.get("display_value") or value.get("name") or value.get("value")
            if display:
                return str(display)
        if value:
            return str(value)
    return "Unassigned"


def _mitigation_from_record(record: dict) -> Optional[str]:
    for key in ("mitigation_plan", "mitigation", "response_plan", "notes"):
        value = record.get(key)
        if value:
            return str(value)
    return None


def _normalize_risks(records: Sequence[dict], reference: date) -> list[Risk]:
    risks: list[Risk] = []
    for item in records:
        summary = (
            item.get("short_description")
            or item.get("description")
            or item.get("risk_name")
            or item.get("name")
            or "ServiceNow risk"
        )
        probability = _safe_probability(
            item.get("probability") or item.get("probability_value") or item.get("u_probability")
        )
        impact = _safe_impact(item.get("impact") or item.get("impact_value") or item.get("u_impact"))
        severity = round(probability * impact, 2)
        if severity >= 2.0:
            status = "High"
        elif severity >= 1.0:
            status = "Medium"
        else:
            status = "Low"
        risk_id = str(
            item.get("sys_id")
            or item.get("number")
            or item.get("id")
            or item.get("risk_id")
            or summary
        )
        due_date = _due_date_from_record(item, reference)
        risks.append(
            Risk(
                id=risk_id,
                summary=str(summary),
                probability=probability,
                impact=impact,
                owner=_owner_from_record(item),
                mitigation=_mitigation_from_record(item),
                due_date=due_date,
                status=status,  # type: ignore[arg-type]
            )
        )
    return risks


def build_snapshot_from_adapters(settings: Settings) -> DatasetSnapshot:
    """Fetch data from live adapters and assemble a dataset snapshot."""
    adapter = adapters.get_jira_adapter(settings)
    if adapter is None:
        raise LiveIngestionError("Jira adapter is not configured. Set JIRA_* environment variables and enable live mode.")

    try:
        payload = adapter.fetch_backlog()
    except Exception as exc:  # noqa: BLE001
        raise LiveIngestionError(f"Jira fetch failed: {exc}") from exc
    finally:
        client = getattr(adapter, "client", None)
        if client and hasattr(client, "close"):
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass

    raw_tasks = payload.get("tasks") or []
    if not raw_tasks:
        raise LiveIngestionError("No Jira issues returned via configured JQL.")

    reference_date = datetime.utcnow().date()
    tasks = _normalize_tasks(raw_tasks, reference_date)
    baseline = _baseline_from_tasks(reference_date, tasks)

    risk_records: list[dict] = []
    sn_adapter = adapters.get_servicenow_adapter(settings)
    if sn_adapter is not None:
        try:
            risk_payload = sn_adapter.fetch_risks()
            risk_records = risk_payload.get("records") or []
        except Exception as exc:  # noqa: BLE001
            raise LiveIngestionError(f"ServiceNow fetch failed: {exc}") from exc
        finally:
            client = getattr(sn_adapter, "client", None)
            if client and hasattr(client, "close"):
                try:
                    client.close()
                except Exception:  # noqa: BLE001
                    pass

    risks = _normalize_risks(risk_records, reference_date)

    note_body = f"Synchronized {len(tasks)} Jira issues via {payload.get('jql', 'project query')} (read-only)."
    if risks:
        note_body += f" Captured {len(risks)} ServiceNow risks (read-only)."
    notes = [
        StatusNote(
            date=reference_date,
            content=note_body,
            author="ASR Copilot",
        )
    ]

    dataset_hash = compute_dataset_hash(tasks, risks, notes)
    snapshot = DatasetSnapshot(
        tasks=tasks,
        risks=risks,
        status_notes=notes,
        baseline=baseline,
        dataset_hash=dataset_hash,
        last_updated=datetime.utcnow(),
    )
    sources = {
        "jira": payload.get("jql", "project query"),
        "jira_issue_count": len(tasks),
        "servicenow_table": "pm_risk" if risk_records else "",
        "servicenow_record_count": len(risks),
    }
    _export_snapshot(settings, snapshot, sources=sources)
    return snapshot

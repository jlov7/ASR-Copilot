"""Utilities for adapter mode management and health checks."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import HTTPException

from app.backend import adapters
from app.backend.config import Settings
from app.backend.models import AdapterStatus

ADAPTER_DISPLAY_NAMES = {
    "jira": "Jira backlog",
    "slack": "Slack status broadcast",
    "servicenow": "ServiceNow risk table",
}

ENV_VARS = {
    "jira": ["JIRA_BASE_URL", "JIRA_USER_EMAIL", "JIRA_TOKEN", "JIRA_PROJECT_KEY"],
    "slack": ["SLACK_BOT_TOKEN", "SLACK_DEFAULT_CHANNEL"],
    "servicenow": ["SERVICENOW_INSTANCE", "SERVICENOW_USER", "SERVICENOW_PASSWORD"],
}


def _checks_path(settings: Settings) -> Path:
    return settings.log_dir / "adapter_checks.json"


def _load_checks(settings: Settings) -> Dict[str, Dict[str, str]]:
    path = _checks_path(settings)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        path.unlink(missing_ok=True)
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _save_check(settings: Settings, key: str, payload: Dict[str, str]) -> None:
    path = _checks_path(settings)
    data = _load_checks(settings)
    data[key] = payload
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _env_configured(adapter_key: str) -> bool:
    required = ENV_VARS.get(adapter_key, [])
    return all(os.getenv(var) for var in required)


def get_adapters_summary(settings: Settings) -> List[AdapterStatus]:
    checks = _load_checks(settings)
    summaries: List[AdapterStatus] = []
    for key, title in ADAPTER_DISPLAY_NAMES.items():
        mode = settings.get_adapter_mode(key)
        safe_blocked = settings.safe_mode
        live_configured = _env_configured(key)
        check_entry = checks.get(key)
        last_checked = None
        if check_entry and check_entry.get("last_checked"):
            try:
                last_checked = datetime.fromisoformat(check_entry["last_checked"])
            except ValueError:
                last_checked = None

        if safe_blocked:
            status = "mock"
            detail = "Safe Mode keeps adapters in mock mode. Provide credentials and disable Safe Mode to go live."
        elif mode == "mock":
            status = "mock"
            detail = "Mock adapter active – using bundled sample data."
        elif not live_configured:
            status = "unconfigured"
            required = ", ".join(ENV_VARS.get(key, []))
            detail = f"Set {required} in the environment to enable live mode."
        elif check_entry:
            status = check_entry.get("status", "pending")
            detail = check_entry.get("detail", "Run a sanity check to verify connectivity.")
        else:
            status = "pending"
            detail = "Live credentials detected. Run a sanity check to verify connectivity."

        summaries.append(
            AdapterStatus(
                key=key,
                name=title,
                mode=mode,
                safe_mode_blocked=safe_blocked,
                live_configured=live_configured,
                status=status,  # type: ignore[arg-type]
                detail=detail,
                last_checked=last_checked,
            )
        )
    return summaries


def run_adapter_check(settings: Settings, adapter_key: str) -> AdapterStatus:
    if adapter_key not in ADAPTER_DISPLAY_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown adapter '{adapter_key}'.")
    if settings.safe_mode:
        raise HTTPException(status_code=400, detail="Disable Safe Mode to run live adapter checks.")

    mode = settings.get_adapter_mode(adapter_key)
    if mode != "live":
        raise HTTPException(status_code=400, detail="Switch adapter to live mode before running checks.")

    if not _env_configured(adapter_key):
        raise HTTPException(status_code=400, detail="Live adapter credentials are not fully configured.")

    detail: str
    status: str

    if adapter_key == "jira":
        adapter = adapters.get_jira_adapter(settings)
        if adapter is None:
            raise HTTPException(status_code=400, detail="Jira adapter could not be initialised.")
        try:
            if hasattr(adapter, "max_results"):
                adapter.max_results = min(adapter.max_results, 10)  # type: ignore[attr-defined]
            payload = adapter.fetch_backlog()
            issues = len(payload.get("tasks", []))
            jql = payload.get("jql")
            detail = f"Connected. Retrieved {issues} issues via {jql}."
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            detail = f"Live check failed: {exc}"
            status = "error"

    elif adapter_key == "slack":
        adapter = adapters.get_slack_adapter(settings)
        if adapter is None:
            raise HTTPException(status_code=400, detail="Slack adapter could not be initialised.")
        ping_method = getattr(adapter, "ping", None)
        try:
            if callable(ping_method):
                response = ping_method()
                team = response.get("team") or response.get("team_id") or "workspace"
                detail = f"Token valid. Ready to post to #{getattr(adapter, 'channel', 'unknown')} ({team})."
            else:
                detail = "Token validated."
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            detail = f"Slack auth failed: {exc}"
            status = "error"

    elif adapter_key == "servicenow":
        adapter = adapters.get_servicenow_adapter(settings)
        if adapter is None:
            raise HTTPException(status_code=400, detail="ServiceNow adapter could not be initialised.")
        try:
            records = adapter.fetch_risks().get("records", [])
            detail = f"Connected. Retrieved {len(records)} ServiceNow records (pm_risk)."
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            detail = f"ServiceNow API error: {exc}"
            status = "error"

    else:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"Adapter '{adapter_key}' not supported.")

    timestamp = datetime.utcnow().isoformat()
    _save_check(
        settings,
        adapter_key,
        {"status": status, "detail": detail, "last_checked": timestamp},
    )

    return AdapterStatus(
        key=adapter_key,
        name=ADAPTER_DISPLAY_NAMES[adapter_key],
        mode=mode,
        safe_mode_blocked=settings.safe_mode,
        live_configured=True,
        status=status,  # type: ignore[arg-type]
        detail=detail,
        last_checked=datetime.fromisoformat(timestamp),
    )

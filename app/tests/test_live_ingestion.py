from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from app.backend.config import Settings
from app.backend.services.live_ingestion import LiveIngestionError, build_snapshot_from_adapters


class StubJiraAdapter:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        self.closed = False

    def fetch_backlog(self) -> dict[str, Any]:
        return self._payload

    @property
    def client(self):  # pragma: no cover - simple stub
        class _Client:
            def __init__(self, outer: StubJiraAdapter) -> None:
                self.outer = outer

            def close(self) -> None:
                self.outer.closed = True

        return _Client(self)


class StubServiceNowAdapter:
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records
        self.closed = False

    def fetch_risks(self, table: str = "pm_risk") -> dict[str, list[dict[str, Any]]]:
        return {"table": table, "records": self._records}

    @property
    def client(self):  # pragma: no cover - simple stub
        class _Client:
            def __init__(self, outer: StubServiceNowAdapter) -> None:
                self.outer = outer

            def close(self) -> None:
                self.outer.closed = True

        return _Client(self)


@pytest.fixture()
def settings(tmp_path, monkeypatch):
    cfg = Settings(
        safe_mode=False,
        cache_dir=tmp_path / "cache",
        out_dir=tmp_path / "out",
        log_dir=tmp_path / "logs",
    )
    cfg.ensure_directories()
    cfg.persist_adapter_mode("jira", "live")
    cfg.persist_adapter_mode("servicenow", "live")
    override_dir = tmp_path / "override-live"
    monkeypatch.setenv("ASR_LIVE_EXPORT_TARGET", "disk")
    monkeypatch.setenv("ASR_LIVE_EXPORT_PATH", str(override_dir))
    return cfg


def test_build_snapshot_from_adapters(monkeypatch, settings):
    adapter = StubJiraAdapter(
        {
            "project": "TEST",
            "jql": "project = TEST ORDER BY updated DESC",
            "tasks": [
                {
                    "id": "TEST-1",
                    "title": "Set up core network",
                    "status": "In Progress",
                    "owner": "Taylor Ops",
                    "due_date": "2024-03-29",
                    "created": "2024-03-11T10:15:00Z",
                    "planned_hours": 24,
                    "actual_hours": 12,
                },
                {
                    "id": "TEST-2",
                    "title": "Vendor sign-off",
                    "status": "Blocked",
                    "owner": "Regine PM",
                    "due_date": None,
                    "created": None,
                    "planned_hours": None,
                    "actual_hours": 0,
                },
            ],
        }
    )
    monkeypatch.setattr("app.backend.services.live_ingestion.adapters.get_jira_adapter", lambda _settings: adapter)
    sn_adapter = StubServiceNowAdapter(
        [
            {
                "sys_id": "risk-1",
                "short_description": "Permit escalation",
                "probability": "0.6",
                "impact": "4",
                "risk_owner": {"display_value": "Avery Risk"},
                "due_date": "2024-04-15",
                "mitigation_plan": "Prep variance hearing",
            },
            {
                "number": "RISK-002",
                "description": "Utility outage delays integration",
                "probability_value": 75,
                "impact_value": 3,
                "assigned_to": "Ops Lead",
            },
        ]
    )
    monkeypatch.setattr("app.backend.services.live_ingestion.adapters.get_servicenow_adapter", lambda _settings: sn_adapter)

    snapshot = build_snapshot_from_adapters(settings)

    assert len(snapshot.tasks) == 2
    assert snapshot.tasks[0].status == "In Progress"
    assert snapshot.tasks[1].status == "Blocked"
    assert snapshot.tasks[1].blocked is True
    assert snapshot.baseline[0].pv >= 24
    assert snapshot.status_notes[0].content.startswith("Synchronized 2 Jira issues")
    assert "Captured 2 ServiceNow risks" in snapshot.status_notes[0].content
    assert len(snapshot.risks) == 2
    assert snapshot.risks[0].owner == "Avery Risk"
    assert snapshot.risks[0].probability == 0.6
    assert snapshot.risks[1].impact == 3
    assert snapshot.dataset_hash
    assert adapter.closed is True
    assert sn_adapter.closed is True

    live_dir = Path(os.environ["ASR_LIVE_EXPORT_PATH"])
    artifacts = list(live_dir.glob("snapshot_*.json"))
    assert len(artifacts) == 1
    payload = json.loads(artifacts[0].read_text(encoding="utf-8"))
    assert payload["sources"]["servicenow_record_count"] == 2
    assert payload["snapshot"]["dataset_hash"] == snapshot.dataset_hash


def test_build_snapshot_requires_config(monkeypatch, settings):
    monkeypatch.setattr("app.backend.services.live_ingestion.adapters.get_jira_adapter", lambda _: None)
    monkeypatch.setattr("app.backend.services.live_ingestion.adapters.get_servicenow_adapter", lambda _: None)

    with pytest.raises(LiveIngestionError):
        build_snapshot_from_adapters(settings)

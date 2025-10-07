"""Adapter interfaces for external systems."""

from __future__ import annotations

from typing import Protocol


class JiraAdapterProtocol(Protocol):
    """Protocol for Jira adapters."""

    def fetch_backlog(self, project_key: str | None = None) -> dict:  # pragma: no cover - protocol definition
        ...


class SlackAdapterProtocol(Protocol):
    """Protocol for Slack adapters."""

    def post_status_pack(self, text: str, files: list[str]) -> bool:  # pragma: no cover - protocol
        ...


class ServiceNowAdapterProtocol(Protocol):
    """Protocol for ServiceNow adapters."""

    def fetch_risks(self, table: str) -> dict:  # pragma: no cover - protocol definition
        ...

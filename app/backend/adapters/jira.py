"""Live Jira adapter (read-only)."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class JiraAdapter:
    """Fetch backlog data from Jira Cloud using JQL filters (read-only)."""

    def __init__(
        self,
        base_url: str,
        email: str,
        token: str,
        project_key: str,
        jql_filter: Optional[str] = None,
        max_results: int = 100,
    ) -> None:
        if not all([base_url, email, token, project_key]):
            raise ValueError("Jira adapter requires base_url, email, token, and project_key.")
        self.base_url = base_url.rstrip("/")
        self.project_key = project_key
        self.jql_filter = jql_filter
        self.max_results = max(1, min(max_results, 500))
        self.client = httpx.Client(auth=(email, token), timeout=10)

    def _build_jql(self) -> str:
        base = f"project = {self.project_key}"
        if self.jql_filter:
            base = f"{base} AND {self.jql_filter}"
        return f"{base} ORDER BY updated DESC"

    def fetch_backlog(self) -> Dict[str, List[dict]]:
        url = f"{self.base_url}/rest/api/3/search"
        response = self.client.get(
            url,
            params={
                "jql": self._build_jql(),
                "maxResults": self.max_results,
                "fields": "summary,status,assignee,duedate,timeoriginalestimate,timespent"
            },
        )
        response.raise_for_status()
        data = response.json()
        tasks: List[dict] = []
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})
            planned_seconds = fields.get("timeoriginalestimate") or 0
            actual_seconds = fields.get("timespent") or 0
            tasks.append(
                {
                    "id": issue.get("key"),
                    "title": fields.get("summary"),
                    "status": fields.get("status", {}).get("name"),
                    "owner": (fields.get("assignee") or {}).get("displayName"),
                    "due_date": fields.get("duedate"),
                    "planned_hours": round(planned_seconds / 3600, 2) if planned_seconds else None,
                    "actual_hours": round(actual_seconds / 3600, 2) if actual_seconds else None,
                }
            )
        logger.info("Fetched %s Jira issues for %s", len(tasks), self.project_key)
        return {"project": self.project_key, "tasks": tasks, "jql": self._build_jql()}

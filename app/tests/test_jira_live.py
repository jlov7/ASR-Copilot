from __future__ import annotations

import os

import pytest

from app.backend.adapters.jira import JiraAdapter

pytestmark = pytest.mark.live


REQUIRED_ENV = [
    "JIRA_BASE_URL",
    "JIRA_USER_EMAIL",
    "JIRA_TOKEN",
    "JIRA_PROJECT_KEY",
]


def _env_or_skip() -> None:
    missing = [var for var in REQUIRED_ENV if not os.getenv(var)]
    if missing:
        pytest.skip(f"Jira live test skipped; missing env vars: {', '.join(missing)}")


def test_jira_fetch_backlog_live():
    _env_or_skip()
    base_url = os.environ["JIRA_BASE_URL"]
    email = os.environ["JIRA_USER_EMAIL"]
    token = os.environ["JIRA_TOKEN"]
    project = os.environ["JIRA_PROJECT_KEY"]
    jql_filter = os.getenv("JIRA_JQL_FILTER")
    max_results = int(os.getenv("JIRA_MAX_RESULTS", "10") or 10)

    adapter = JiraAdapter(
        base_url=base_url,
        email=email,
        token=token,
        project_key=project,
        jql_filter=jql_filter,
        max_results=max_results,
    )

    result = adapter.fetch_backlog()
    assert result["project"] == project
    assert "tasks" in result
    assert isinstance(result["tasks"], list)
    assert result["jql"].startswith("project =")

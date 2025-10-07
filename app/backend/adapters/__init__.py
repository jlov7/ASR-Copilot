"""Adapter registry handling mock/live selection."""

from __future__ import annotations

import os
from typing import Optional

from app.backend.config import Settings

from .jira import JiraAdapter
from .mock_jira import MockJiraAdapter
from .mock_servicenow import MockServiceNowAdapter
from .mock_slack import MockSlackAdapter
from .servicenow import ServiceNowAdapter
from .slack import SlackAdapter


def get_slack_adapter(settings: Settings):
    if settings.safe_mode or settings.adapter_mode == "mock":
        return MockSlackAdapter()
    token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_DEFAULT_CHANNEL")
    if not token or not channel:
        return None
    return SlackAdapter(token=token, channel=channel)


def get_jira_adapter(settings: Settings):
    if settings.safe_mode or settings.adapter_mode == "mock":
        return MockJiraAdapter(settings.data_dir)
    base_url = os.getenv("JIRA_BASE_URL")
    user = os.getenv("JIRA_USER_EMAIL")
    token = os.getenv("JIRA_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY")
    jql_filter = os.getenv("JIRA_JQL_FILTER")
    max_results_raw = os.getenv("JIRA_MAX_RESULTS")
    max_results = 100
    if max_results_raw and max_results_raw.isdigit():
        max_results = int(max_results_raw)
    if not all([base_url, user, token, project_key]):
        return None
    return JiraAdapter(
        base_url=base_url,
        email=user,
        token=token,
        project_key=project_key,
        jql_filter=jql_filter,
        max_results=max_results,
    )


def get_servicenow_adapter(settings: Settings):
    if settings.safe_mode or settings.adapter_mode == "mock":
        return MockServiceNowAdapter(settings.data_dir)
    instance = os.getenv("SERVICENOW_INSTANCE")
    user = os.getenv("SERVICENOW_USER")
    password = os.getenv("SERVICENOW_PASSWORD")
    if not all([instance, user, password]):
        return None
    return ServiceNowAdapter(instance=instance, user=user, password=password)

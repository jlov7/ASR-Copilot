"""Mock Jira adapter reading local sample data."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

from app.backend.services.ingestion import parse_tasks

logger = logging.getLogger(__name__)


class MockJiraAdapter:
    """Serve backlog data from bundled CSV."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def fetch_backlog(self, project_key: str | None = None) -> Dict[str, List[dict]]:
        tasks_path = self.data_dir / "tasks.csv"
        if not tasks_path.exists():
            logger.warning("Mock Jira dataset not found at %s", tasks_path)
            return {"project": project_key or "SAMPLE", "tasks": []}
        tasks = parse_tasks(tasks_path.read_bytes())
        return {
            "project": project_key or "SAMPLE",
            "tasks": [task.dict() for task in tasks],
        }

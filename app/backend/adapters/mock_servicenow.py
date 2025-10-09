"""Mock ServiceNow adapter reading local sample data."""

from __future__ import annotations

import logging
from pathlib import Path

from app.backend.services.ingestion import parse_risks

logger = logging.getLogger(__name__)


class MockServiceNowAdapter:
    """Serve risk data from bundled CSV."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def fetch_risks(self, table: str = "pm_risk") -> dict[str, list[dict]]:
        risks_path = self.data_dir / "risks.csv"
        if not risks_path.exists():
            logger.warning("Mock ServiceNow dataset not found at %s", risks_path)
            return {"table": table, "records": []}
        risks = parse_risks(risks_path.read_bytes())
        return {"table": table, "records": [risk.model_dump() for risk in risks]}

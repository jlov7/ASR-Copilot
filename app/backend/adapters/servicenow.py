"""ServiceNow adapter (read-only incidents/risks)."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ServiceNowAdapter:
    """Fetch risk/incidents from ServiceNow table API."""

    def __init__(self, instance: str, user: str, password: str) -> None:
        if not all([instance, user, password]):
            raise ValueError("ServiceNow adapter requires instance, user, and password.")
        base_url = instance.rstrip("/")
        if not base_url.startswith("https://"):
            base_url = f"https://{base_url}"
        self.client = httpx.Client(
            base_url=f"{base_url}/api/now",
            auth=(user, password),
            timeout=10,
        )

    def fetch_risks(self, table: str = "pm_risk") -> Dict[str, List[dict]]:
        response = self.client.get(f"/table/{table}", params={"sysparm_limit": 100})
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("ServiceNow API error: %s", exc)
            return {"table": table, "records": []}
        data = response.json()
        return {"table": table, "records": data.get("result", [])}

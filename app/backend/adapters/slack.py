"""Slack adapter supporting chat.postMessage (read-only)."""

from __future__ import annotations

import logging
from typing import List

import httpx

logger = logging.getLogger(__name__)


class SlackAdapter:
    """Post status updates to Slack channel."""

    def __init__(self, token: str, channel: str) -> None:
        if not token or not channel:
            raise ValueError("Slack token and channel are required.")
        self.channel = channel
        self.client = httpx.Client(
            base_url="https://slack.com/api",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )

    def post_status_pack(self, text: str, files: List[str]) -> bool:
        """Post message to Slack; attachments are referenced but not uploaded in mock mode."""
        payload = {"channel": self.channel, "text": text}
        response = self.client.post("/chat.postMessage", json=payload)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Slack message failed: %s", exc)
            return False
        body = response.json()
        if not body.get("ok"):
            logger.error("Slack API error: %s", body)
            return False
        if files:
            logger.info("Files generated for manual sharing: %s", files)
        return True

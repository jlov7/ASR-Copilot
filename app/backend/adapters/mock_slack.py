"""Mock Slack adapter that logs outgoing messages."""

from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger(__name__)


class MockSlackAdapter:
    """Simulate Slack posting without network calls."""

    def __init__(self, channel: str = "#asr-demo") -> None:
        self.channel = channel

    def post_status_pack(self, text: str, files: List[str]) -> bool:
        logger.info("Mock Slack message to %s: %s", self.channel, text)
        if files:
            logger.info("Mock Slack attachments: %s", files)
        return True

    def ping(self) -> dict:
        """Return a canned response for credential checks."""
        logger.info("Mock Slack ping for channel %s", self.channel)
        return {"ok": True, "team": "Mock Workspace", "channel": self.channel}

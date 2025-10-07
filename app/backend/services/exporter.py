"""Status pack export orchestrator."""

from __future__ import annotations

import logging
from typing import Optional

from app.backend.config import Settings
from app.backend.models import DashboardPayload, StatusPackRequest, StatusPackResult
from app.core.status_pack import generate_status_pack

logger = logging.getLogger(__name__)


class SlackAdapterProtocol:
    """Structural typing for slack adapter."""

    def post_status_pack(self, text: str, files: list[str]) -> bool:  # pragma: no cover - protocol
        raise NotImplementedError


def export_status_pack(
    settings: Settings,
    payload: DashboardPayload,
    request: StatusPackRequest,
    slack_adapter: Optional[SlackAdapterProtocol] = None,
) -> StatusPackResult:
    """Generate status pack assets and optionally post to Slack."""
    result = generate_status_pack(
        payload,
        settings.out_dir,
        include_markdown=request.include_markdown,
        include_png=request.include_png,
    )
    posted = False
    if slack_adapter is not None and not settings.safe_mode:
        files: list[str] = []
        if result.markdown_path:
            files.append(result.markdown_path)
        files.extend(result.chart_paths)
        try:
            posted = slack_adapter.post_status_pack(
                text=payload.narrative,
                files=files,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to post status pack to Slack: %s", exc)
            posted = False
    elif slack_adapter is not None and settings.safe_mode:
        logger.info("Safe Mode active – skipping Slack export.")

    return StatusPackResult(
        markdown_path=result.markdown_path,
        chart_paths=result.chart_paths,
        posted_to_slack=posted,
        dataset_hash=result.dataset_hash,
    )

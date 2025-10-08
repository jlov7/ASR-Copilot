"""Status pack export orchestrator."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from app.backend.config import Settings
from app.backend.models import DashboardPayload, StatusPackRequest, StatusPackResult
from app.backend.services import automation
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
    export_start = time.perf_counter()
    result = generate_status_pack(
        payload,
        settings.out_dir,
        include_markdown=request.include_markdown,
        include_png=request.include_png,
    )
    duration_ms = int((time.perf_counter() - export_start) * 1000)

    posted = False
    slack_note = "Slack not configured."
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
            slack_note = "Posted to Slack." if posted else "Slack post returned failure response."
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to post status pack to Slack: %s", exc)
            posted = False
            slack_note = f"Slack error: {exc}"
    elif slack_adapter is not None and settings.safe_mode:
        logger.info("Safe Mode active – skipping Slack export.")
        slack_note = "Skipped Slack (Safe Mode)."

    parts: list[str] = []
    if result.markdown_path:
        parts.append(f"Markdown {Path(result.markdown_path).name}")
    if result.chart_paths:
        chart_names = ", ".join(Path(path).name for path in result.chart_paths)
        parts.append(f"Charts {chart_names}")
    parts.append(slack_note)

    automation.record_export_result(
        settings,
        status="ok",
        note="; ".join(parts),
        duration_ms=duration_ms,
    )

    return StatusPackResult(
        markdown_path=result.markdown_path,
        chart_paths=result.chart_paths,
        posted_to_slack=posted,
        dataset_hash=result.dataset_hash,
    )

"""Export endpoints."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.backend import adapters
from app.backend.config import Settings, get_settings
from app.backend.models import StatusPackRequest, StatusPackResult
from app.backend.services import cache
from app.backend.services.exporter import export_status_pack
from app.backend.services.status import build_dashboard_payload

router = APIRouter(prefix="/api", tags=["export"])


class ExportPathPayload(BaseModel):
    path: str


def _resolve_export_path(path: str, settings: Settings, *, must_exist: bool = True) -> Path:
    """Resolve user-supplied export path while enforcing sandbox boundaries."""
    candidate = Path(path)
    out_root = settings.out_dir.resolve()

    if candidate.is_absolute():
        resolved = candidate.resolve(strict=False)
    else:
        parts = candidate.parts
        relative = Path(*parts[1:]) if parts and parts[0] == out_root.name else candidate
        resolved = (out_root / relative).resolve(strict=False)

    if resolved != out_root and out_root not in resolved.parents:
        raise HTTPException(status_code=400, detail="Path must remain within the export directory.")

    if must_exist and not resolved.exists():
        raise HTTPException(status_code=404, detail="Export artifact not found.")

    return resolved


@router.post("/export/status-pack", response_model=StatusPackResult)
async def create_status_pack(
    request: StatusPackRequest,
    settings: Settings = Depends(get_settings),
) -> StatusPackResult:
    snapshot = cache.load_current(settings)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No dataset available to export.")
    payload = build_dashboard_payload(settings, snapshot)
    slack_adapter = adapters.get_slack_adapter(settings)
    result = export_status_pack(settings, payload, request, slack_adapter=slack_adapter)
    return result


@router.post("/export/markdown")
async def get_export_markdown(
    payload: ExportPathPayload,
    settings: Settings = Depends(get_settings),
) -> dict:
    target = _resolve_export_path(payload.path, settings, must_exist=True)
    if target.suffix.lower() != ".md":
        raise HTTPException(status_code=400, detail="Only Markdown exports can be copied.")
    content = target.read_text(encoding="utf-8")
    return {"content": content}


@router.post("/export/reveal")
async def reveal_export_location(
    payload: ExportPathPayload,
    settings: Settings = Depends(get_settings),
) -> dict:
    resolved = _resolve_export_path(payload.path, settings, must_exist=False)
    target_dir = resolved if resolved.is_dir() else resolved.parent
    if not target_dir.exists():
        raise HTTPException(status_code=404, detail="Export directory not found.")

    try:
        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(target_dir)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("win"):
            os.startfile(str(target_dir))  # type: ignore[attr-defined]  # noqa: PTH123
        else:
            subprocess.Popen(["xdg-open", str(target_dir)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Unable to open export directory: {exc}") from exc

    return {"success": True}

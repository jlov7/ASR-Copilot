"""Export endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.backend import adapters
from app.backend.config import Settings, get_settings
from app.backend.models import StatusPackRequest, StatusPackResult
from app.backend.services import cache
from app.backend.services.exporter import export_status_pack
from app.backend.services.status import build_dashboard_payload

router = APIRouter(prefix="/api", tags=["export"])


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

"""Analytics endpoints for dashboard + ROI."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.backend.config import Settings, get_settings
from app.backend.models import DashboardPayload, RoiSnapshot, RoiUpdateRequest
from app.backend.services import cache
from app.backend.services.status import build_dashboard_payload
from app.core import roi as roi_core

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardPayload)
async def get_dashboard(
    settings: Settings = Depends(get_settings),
) -> DashboardPayload:
    snapshot = cache.load_current(settings)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No dataset ingested yet.")
    return build_dashboard_payload(settings, snapshot)


@router.get("/roi", response_model=RoiSnapshot)
async def get_roi(settings: Settings = Depends(get_settings)) -> RoiSnapshot:
    preset, modifiers, assumptions = roi_core.load_state(settings.roi_settings_path)
    return roi_core.compute_roi(preset, modifiers, assumptions)


@router.post("/roi", response_model=RoiSnapshot)
async def update_roi(
    payload: RoiUpdateRequest,
    settings: Settings = Depends(get_settings),
) -> RoiSnapshot:
    roi_core.save_state(
        settings.roi_settings_path,
        preset=payload.preset,
        modifiers=payload.modifiers,
        assumptions=payload.assumptions,
    )
    return roi_core.compute_roi(payload.preset, payload.modifiers, payload.assumptions)

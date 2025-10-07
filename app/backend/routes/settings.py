"""Settings endpoints for Safe Mode and adapter configuration."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.backend.config import Settings, get_settings

router = APIRouter(prefix="/api", tags=["settings"])


class SafeModeUpdate(BaseModel):
    safe_mode: bool


@router.get("/settings")
async def get_settings_state(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "safe_mode": settings.safe_mode,
        "adapter_mode": settings.adapter_mode,
    }


@router.post("/settings/safe-mode")
async def update_safe_mode(
    payload: SafeModeUpdate,
    settings: Settings = Depends(get_settings),
) -> dict:
    settings.persist_safe_mode(payload.safe_mode)
    return {"safe_mode": settings.safe_mode}

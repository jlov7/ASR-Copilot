"""Settings endpoints for Safe Mode and adapter configuration."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.backend.config import Settings, get_settings
from app.backend.models import AdapterStatus
from app.backend.services import adapter_status

router = APIRouter(prefix="/api", tags=["settings"])


class SafeModeUpdate(BaseModel):
    safe_mode: bool


class AdapterModeUpdate(BaseModel):
    adapter: Literal["jira", "slack", "servicenow"]
    mode: Literal["mock", "live"]


class AdapterCheckRequest(BaseModel):
    adapter: Literal["jira", "slack", "servicenow"]


@router.get("/settings")
async def get_settings_state(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "safe_mode": settings.safe_mode,
        "adapter_mode": settings.adapter_mode,
        "adapter_modes": settings.adapter_modes,
        "adapters": adapter_status.get_adapters_summary(settings),
    }


@router.post("/settings/safe-mode")
async def update_safe_mode(
    payload: SafeModeUpdate,
    settings: Settings = Depends(get_settings),
) -> dict:
    settings.persist_safe_mode(payload.safe_mode)
    return {
        "safe_mode": settings.safe_mode,
        "adapter_mode": settings.adapter_mode,
        "adapter_modes": settings.adapter_modes,
        "adapters": adapter_status.get_adapters_summary(settings),
    }


@router.post("/settings/adapter-mode")
async def update_adapter_mode(
    payload: AdapterModeUpdate,
    settings: Settings = Depends(get_settings),
) -> dict:
    if payload.mode == "live" and settings.safe_mode:
        raise HTTPException(status_code=400, detail="Disable Safe Mode before enabling live adapters.")
    settings.persist_adapter_mode(payload.adapter, payload.mode)
    return {
        "adapter_mode": settings.adapter_mode,
        "adapter_modes": settings.adapter_modes,
        "adapters": adapter_status.get_adapters_summary(settings),
    }


@router.post("/settings/adapter-check", response_model=AdapterStatus)
async def run_adapter_check(
    payload: AdapterCheckRequest,
    settings: Settings = Depends(get_settings),
) -> AdapterStatus:
    return adapter_status.run_adapter_check(settings, payload.adapter)

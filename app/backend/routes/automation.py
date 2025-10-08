"""Automation loop endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.backend.config import Settings, get_settings
from app.backend.models import AutomationStatus
from app.backend.services import automation

router = APIRouter(prefix="/api", tags=["automation"])


@router.get("/automation", response_model=AutomationStatus)
async def get_automation_status(settings: Settings = Depends(get_settings)) -> AutomationStatus:
    return automation.load_status(settings)


@router.post("/automation/dry-run", response_model=AutomationStatus)
async def run_automation_dry_run(settings: Settings = Depends(get_settings)) -> AutomationStatus:
    return automation.simulate_dry_run(settings)

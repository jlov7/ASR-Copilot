"""Ingestion endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.backend.config import Settings, get_settings
from app.backend.models import UploadResponse
from app.backend.services import automation, cache
from app.backend.services.ingestion import ingest_payload, load_sample_dataset, to_upload_response
from app.backend.services.live_ingestion import LiveIngestionError, build_snapshot_from_adapters
from app.backend.services.samples import load_guided_dataset

router = APIRouter(prefix="/api", tags=["ingestion"])


class DemoLoadRequest(BaseModel):
    """Optional scenario payload for demo dataset loading."""

    scenario: str | None = Field(
        default=None,
        description="Guided scenario identifier (e.g., '5g', 'cloud', 'cpe').",
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        description="Optional deterministic seed to vary scenario timestamps.",
    )


@router.post("/ingest", response_model=UploadResponse)
async def ingest_data(
    tasks: UploadFile = File(...),
    risks: UploadFile = File(...),
    status_notes: UploadFile = File(...),
    evm_baseline: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    """Upload CSV/Markdown artifacts and refresh dataset."""
    snapshot = ingest_payload(tasks, risks, status_notes, evm_baseline)
    cache.save_snapshot(settings, snapshot)
    automation.record_dataset_refresh(settings, snapshot, trigger="upload")
    return to_upload_response(snapshot)


@router.post("/ingest/live", response_model=UploadResponse)
async def ingest_live_data(settings: Settings = Depends(get_settings)) -> UploadResponse:
    """Synchronize dataset using live adapters (Jira read-only)."""
    if settings.safe_mode:
        raise HTTPException(status_code=400, detail="Disable Safe Mode to ingest from live adapters.")
    if settings.get_adapter_mode("jira") != "live":
        raise HTTPException(status_code=400, detail="Enable Jira live mode before running live ingestion.")
    try:
        snapshot = build_snapshot_from_adapters(settings)
    except LiveIngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    cache.save_snapshot(settings, snapshot)
    automation.record_dataset_refresh(
        settings,
        snapshot,
        trigger="live",
        previous_snapshot=cache.load_previous(settings),
    )
    return to_upload_response(snapshot)


@router.post("/demo/load", response_model=UploadResponse)
async def load_demo_dataset(
    payload: DemoLoadRequest | None = None,
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    """Load bundled sample data or a guided scenario."""
    scenario = payload.scenario if payload else None
    seed = payload.seed if payload else None
    if scenario:
        snapshot = load_guided_dataset(settings, scenario, seed=seed)
        trigger = "seed"
    else:
        snapshot = load_sample_dataset(settings)
        trigger = "upload"
    cache.save_snapshot(settings, snapshot)
    automation.record_dataset_refresh(
        settings,
        snapshot,
        trigger=trigger,
        previous_snapshot=cache.load_previous(settings),
    )
    return to_upload_response(snapshot)


@router.post("/ingest/purge")
async def purge_cache(settings: Settings = Depends(get_settings)) -> dict:
    """Remove cached snapshots."""
    cache.purge(settings)
    return {"status": "ok"}

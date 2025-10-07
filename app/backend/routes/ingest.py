"""Ingestion endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from app.backend.config import Settings, get_settings
from app.backend.models import UploadResponse
from app.backend.services import cache
from app.backend.services.ingestion import (
    ingest_payload,
    load_sample_dataset,
    to_upload_response,
)

router = APIRouter(prefix="/api", tags=["ingestion"])


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
    return to_upload_response(snapshot)


@router.post("/demo/load", response_model=UploadResponse)
async def load_demo_dataset(
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    """Load bundled sample data."""
    snapshot = load_sample_dataset(settings)
    cache.save_snapshot(settings, snapshot)
    return to_upload_response(snapshot)


@router.post("/ingest/purge")
async def purge_cache(settings: Settings = Depends(get_settings)) -> dict:
    """Remove cached snapshots."""
    cache.purge(settings)
    return {"status": "ok"}

"""FastAPI application factory."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.backend.config import get_settings
from app.backend.logging_config import configure_logging
from app.backend.routes import analytics, automation, export, ingest, settings


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="ASR Copilot API",
        version="0.1.0",
        description="Local-first analytics for Autonomy–Status–Risk management.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        start = time.time()
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        logger = logging.getLogger("asr.request")
        logger.info("Request %s %s %s", request_id, request.method, request.url.path)
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = f"{duration_ms:.2f}"
        logger.info("Completed %s in %.2fms", request_id, duration_ms)
        return response

    app.include_router(ingest.router)
    app.include_router(analytics.router)
    app.include_router(export.router)
    app.include_router(automation.router)
    app.include_router(settings.router)

    @app.get("/healthz")
    async def healthcheck() -> dict:
        settings_obj = get_settings()
        return {
            "status": "ok",
            "safe_mode": settings_obj.safe_mode,
            "adapter_mode": settings_obj.adapter_mode,
        }

    return app


app = create_app()

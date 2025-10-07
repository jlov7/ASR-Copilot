"""Application configuration and path utilities."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    safe_mode: bool = Field(default=True, env="ASR_SAFE_MODE")
    adapter_mode: Literal["mock", "live"] = Field(default="mock", env="ADAPTER_MODE")
    dataset_name: str = Field(default="autonomy_program")
    data_dir: Path = Field(default=Path("data/samples"))
    cache_dir: Path = Field(default=Path(".cache"))
    out_dir: Path = Field(default=Path("out"))
    log_dir: Path = Field(default=Path("logs"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_directories(self) -> None:
        """Create directories required for runtime artifacts."""
        for path in (self.cache_dir, self.out_dir, self.log_dir):
            path.mkdir(parents=True, exist_ok=True)
        override_path = self.cache_dir / "safe_mode.json"
        if override_path.exists():
            try:
                value = json.loads(override_path.read_text(encoding="utf-8"))
                self.safe_mode = bool(value.get("safe_mode", True))
            except json.JSONDecodeError:
                override_path.unlink(missing_ok=True)

    @property
    def current_snapshot_path(self) -> Path:
        return self.cache_dir / f"{self.dataset_name}_current.json"

    @property
    def previous_snapshot_path(self) -> Path:
        return self.cache_dir / f"{self.dataset_name}_previous.json"

    @property
    def roi_settings_path(self) -> Path:
        return self.cache_dir / "roi_settings.json"

    @property
    def log_file_path(self) -> Path:
        return self.log_dir / "app.log"

    @property
    def safe_mode_path(self) -> Path:
        return self.cache_dir / "safe_mode.json"

    def persist_safe_mode(self, value: bool) -> None:
        self.safe_mode = value
        self.safe_mode_path.write_text(
            json.dumps({"safe_mode": value}, indent=2), encoding="utf-8"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings

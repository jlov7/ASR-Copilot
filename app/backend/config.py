"""Application configuration and path utilities."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    safe_mode: bool = Field(default=True, validation_alias=AliasChoices("ASR_SAFE_MODE"))
    adapter_mode: Literal["mock", "live"] = Field(default="mock", validation_alias=AliasChoices("ADAPTER_MODE"))
    dataset_name: str = Field(default="autonomy_program")
    data_dir: Path = Field(default=Path("data/samples"))
    cache_dir: Path = Field(default=Path(".cache"))
    out_dir: Path = Field(default=Path("out"))
    log_dir: Path = Field(default=Path("logs"))
    _adapter_modes: dict[str, Literal["mock", "live"]] = PrivateAttr(default_factory=dict)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

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
        self._adapter_modes.clear()
        self._load_adapter_modes()

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
        self._sync_adapter_mode()

    @property
    def adapter_config_path(self) -> Path:
        return self.cache_dir / "adapter_modes.json"

    def _load_adapter_modes(self) -> None:
        default_mode = getattr(self, "adapter_mode", "mock")
        path = self.adapter_config_path
        modes: dict[str, Literal["mock", "live"]] = {}
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                for key in ("jira", "slack", "servicenow"):
                    raw = payload.get(key, default_mode)
                    modes[key] = "live" if raw == "live" else "mock"
            except json.JSONDecodeError:
                path.unlink(missing_ok=True)
                modes = {}
        if not modes:
            modes = {key: default_mode for key in ("jira", "slack", "servicenow")}
            path.write_text(json.dumps(modes, indent=2), encoding="utf-8")
        self._adapter_modes = modes
        self._sync_adapter_mode()

    def _sync_adapter_mode(self) -> None:
        aggregate = "live" if any(mode == "live" for mode in self._adapter_modes.values()) else "mock"
        object.__setattr__(self, "adapter_mode", aggregate)

    def get_adapter_mode(self, key: str) -> Literal["mock", "live"]:
        return self._adapter_modes.get(key, "mock")

    def persist_adapter_mode(self, key: str, mode: Literal["mock", "live"]) -> None:
        if key not in ("jira", "slack", "servicenow"):
            raise ValueError(f"Unknown adapter key: {key}")
        self._adapter_modes[key] = mode
        self.adapter_config_path.write_text(json.dumps(self._adapter_modes, indent=2), encoding="utf-8")
        self._sync_adapter_mode()

    @property
    def adapter_modes(self) -> dict[str, Literal["mock", "live"]]:
        return dict(self._adapter_modes)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings

from pathlib import Path

from app.backend.config import Settings


def test_adapter_mode_persistence(tmp_path):
    settings = Settings(
        cache_dir=tmp_path / ".cache",
        out_dir=tmp_path / "out",
        log_dir=tmp_path / "logs",
    )
    settings.ensure_directories()

    assert settings.adapter_modes["jira"] == "mock"
    assert settings.adapter_mode == "mock"

    settings.persist_adapter_mode("jira", "live")
    assert settings.adapter_modes["jira"] == "live"
    assert settings.adapter_mode == "live"

    settings.persist_safe_mode(True)
    # Safe Mode does not override stored preference but keeps aggregate in sync
    assert settings.adapter_modes["jira"] == "live"
    assert settings.adapter_mode == "live"

    settings.persist_adapter_mode("slack", "live")
    assert settings.adapter_mode == "live"

    reloaded = Settings(
        cache_dir=settings.cache_dir,
        out_dir=settings.out_dir,
        log_dir=settings.log_dir,
    )
    reloaded.ensure_directories()
    assert reloaded.adapter_modes["jira"] == "live"
    assert reloaded.adapter_modes["slack"] == "live"

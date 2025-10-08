"""CLI helper to load sample dataset into cache."""

from __future__ import annotations

from app.backend.config import get_settings
from app.backend.services import automation, cache
from app.backend.services.ingestion import load_sample_dataset


def main() -> None:
    settings = get_settings()
    snapshot = load_sample_dataset(settings)
    cache.save_snapshot(settings, snapshot)
    automation.record_dataset_refresh(settings, snapshot, trigger="seed")
    print(
        f"Loaded sample dataset with {len(snapshot.tasks)} tasks and {len(snapshot.risks)} risks."
    )


if __name__ == "__main__":
    main()

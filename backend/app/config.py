import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _dt(name: str, default: str) -> datetime:
    return datetime.fromisoformat(os.getenv(name, default)).replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class Settings:
    elexon_base_url: str = field(default_factory=lambda: os.getenv(
        "ELEXON_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1/datasets"))
    elexon_api_key: str | None = field(default_factory=lambda: os.getenv("ELEXON_API_KEY") or None)
    # Delivery periods in scope: January 2026
    target_start: datetime = field(default_factory=lambda: _dt("TARGET_START", "2026-01-01"))
    target_end: datetime = field(default_factory=lambda: _dt("TARGET_END", "2026-02-01"))
    # Forecasts for early-January targets are published in late December
    forecast_publish_from: datetime = field(default_factory=lambda: _dt("FORECAST_PUBLISH_FROM", "2025-12-20"))
    cache_file: Path = field(default_factory=lambda: Path(os.getenv("CACHE_FILE", "data/elexon_cache.json")))
    cors_origins: tuple = field(default_factory=lambda: tuple(os.getenv("CORS_ORIGINS", "*").split(",")))
    # Day-ahead decision cutoff (UTC hour on D-1)
    default_cutoff_hour_utc: int = field(default_factory=lambda: int(os.getenv("DEFAULT_CUTOFF_HOUR_UTC", "9")))


settings = Settings()

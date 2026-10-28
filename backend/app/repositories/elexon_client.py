from datetime import datetime, timedelta

import httpx

from app.config import Settings
from app.models.domain import Actual, Forecast


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


class ElexonClient:
    """Thin gateway over the Elexon BMRS stream endpoints."""

    def __init__(self, settings: Settings, http: httpx.Client | None = None):
        self._s = settings
        self._http = http or httpx.Client(timeout=120)

    def _get(self, dataset: str, params: dict) -> list[dict]:
        if self._s.elexon_api_key:
            params = {**params, "APIKey": self._s.elexon_api_key}
        r = self._http.get(f"{self._s.elexon_base_url}/{dataset}/stream", params=params)
        r.raise_for_status()
        return r.json()

    def fetch_actuals(self) -> list[Actual]:
        rows = self._get("FUELHH", {
            "settlementDateFrom": self._s.target_start.date().isoformat(),
            "settlementDateTo": (self._s.target_end - timedelta(days=1)).date().isoformat(),
            "fuelType": "WIND",
        })
        return [Actual(_parse(r["startTime"]), float(r["generation"]))
                for r in rows if r.get("fuelType") == "WIND"]

    def fetch_forecasts(self) -> list[Forecast]:
        rows = self._get("WINDFOR", {
            "publishDateTimeFrom": self._s.forecast_publish_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "publishDateTimeTo": self._s.target_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        return [Forecast(_parse(r["startTime"]), _parse(r["publishTime"]), float(r["generation"]))
                for r in rows if r.get("generation") is not None]

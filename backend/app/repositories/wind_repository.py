import json
import threading
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime

from app.config import Settings
from app.models.domain import Actual, Forecast
from app.repositories.elexon_client import ElexonClient


class WindDataRepository:
    """Holds actuals/forecasts in memory, backed by a JSON file cache."""

    def __init__(self, settings: Settings, client: ElexonClient):
        self._s = settings
        self._client = client
        self._lock = threading.Lock()
        self._actuals: dict[datetime, Actual] = {}
        self._forecasts: dict[datetime, list[Forecast]] = {}  # by target, sorted by publish
        self._loaded = False

    def _ensure_loaded(self) -> None:
        with self._lock:
            if self._loaded:
                return
            path = self._s.cache_file
            if path.exists():
                raw = json.loads(path.read_text())
                actuals = [Actual(datetime.fromisoformat(a["t"]), a["g"]) for a in raw["actuals"]]
                forecasts = [Forecast(datetime.fromisoformat(f["t"]), datetime.fromisoformat(f["p"]), f["g"])
                             for f in raw["forecasts"]]
            else:
                actuals = self._client.fetch_actuals()
                forecasts = self._client.fetch_forecasts()
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({
                    "actuals": [{"t": a.start_time.isoformat(), "g": a.generation} for a in actuals],
                    "forecasts": [{"t": f.start_time.isoformat(), "p": f.publish_time.isoformat(), "g": f.generation}
                                  for f in forecasts],
                }))
            self._index(actuals, forecasts)
            self._loaded = True

    def _index(self, actuals: list[Actual], forecasts: list[Forecast]) -> None:
        self._actuals = {a.start_time: a for a in actuals}
        grouped: dict[datetime, list[Forecast]] = defaultdict(list)
        for f in forecasts:
            grouped[f.start_time].append(f)
        self._forecasts = {k: sorted(v, key=lambda f: f.publish_time) for k, v in grouped.items()}

    def actual_at(self, t: datetime) -> Actual | None:
        self._ensure_loaded()
        return self._actuals.get(t)

    def actual_times(self) -> list[datetime]:
        self._ensure_loaded()
        return sorted(self._actuals)

    def forecast_times(self) -> list[datetime]:
        self._ensure_loaded()
        return sorted(self._forecasts)

    def forecasts_for(self, t: datetime) -> list[Forecast]:
        self._ensure_loaded()
        return self._forecasts.get(t, [])

    def latest_published_by(self, t: datetime, publish_deadline: datetime) -> Forecast | None:
        """Latest forecast for target `t` published at or before `publish_deadline`."""
        fs = self.forecasts_for(t)
        i = bisect_right([f.publish_time for f in fs], publish_deadline)
        return fs[i - 1] if i else None

    def all_forecasts(self) -> list[Forecast]:
        self._ensure_loaded()
        return [f for fs in self._forecasts.values() for f in fs]

from datetime import datetime, timedelta, timezone

from app.config import Settings
from app.models.domain import Actual, Forecast
from app.repositories.wind_repository import WindDataRepository
from app.services.analysis_service import AnalysisService
from app.services.metrics import compute_metrics
from app.services.selection import DayAheadCutoffStrategy, HorizonStrategy

UTC = timezone.utc
T = datetime(2026, 1, 10, 12, tzinfo=UTC)


class FakeClient:
    def fetch_actuals(self):
        return [Actual(T, 100.0)]

    def fetch_forecasts(self):
        return [Forecast(T, T - timedelta(hours=h), g) for h, g in [(60, 90.0), (30, 110.0), (20, 130.0), (2, 100.0)]]


def make(tmp_path):
    s = Settings(cache_file=tmp_path / "c.json")
    return AnalysisService(WindDataRepository(s, FakeClient()), s), s


def test_metrics():
    m = compute_metrics([110, 90], [100, 100])
    assert m["mae"] == 10 and m["bias"] == 0 and m["rmse"] == 10


def test_horizon_picks_latest_before_deadline(tmp_path):
    svc, _ = make(tmp_path)
    p = svc.pairs(HorizonStrategy(24))[0]
    assert p.forecast.generation == 110.0 and p.forecast.horizon_hours == 30


def test_cutoff_day_ahead(tmp_path):
    svc, _ = make(tmp_path)
    # deadline = Jan 9 09:00 -> 27h before target -> forecast at 30h ahead
    p = svc.pairs(DayAheadCutoffStrategy(9))[0]
    assert p.forecast.generation == 110.0


def test_no_forecast_available(tmp_path):
    svc, _ = make(tmp_path)
    assert svc.pairs(HorizonStrategy(100))[0].forecast is None


def test_cache_roundtrip(tmp_path):
    svc, s = make(tmp_path)
    svc.pairs(HorizonStrategy(0))
    repo2 = WindDataRepository(s, None)  # must load from cache, no client
    assert repo2.actual_at(T).generation == 100.0

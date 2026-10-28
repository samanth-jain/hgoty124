from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.config import Settings
from app.models.domain import Pair
from app.repositories.wind_repository import WindDataRepository
from app.services.metrics import compute_metrics
from app.services.selection import (DayAheadCutoffStrategy, ForecastSelectionStrategy,
                                    HorizonStrategy)


class AnalysisService:
    def __init__(self, repo: WindDataRepository, settings: Settings):
        self._repo = repo
        self._s = settings

    def _targets(self, start: datetime | None, end: datetime | None) -> list[datetime]:
        lo = max(start, self._s.target_start) if start else self._s.target_start
        hi = min(end, self._s.target_end) if end else self._s.target_end
        times = set(self._repo.actual_times()) | set(self._repo.forecast_times())
        return sorted(t for t in times if lo <= t < hi)

    def pairs(self, strategy: ForecastSelectionStrategy, start=None, end=None) -> list[Pair]:
        return [Pair(t, strategy.select(self._repo, t), self._repo.actual_at(t))
                for t in self._targets(start, end)]

    def series(self, strategy, start=None, end=None) -> list[Pair]:
        return self.pairs(strategy, start, end)

    @staticmethod
    def metrics_for(pairs: list[Pair]) -> dict | None:
        both = [p for p in pairs if p.forecast and p.actual]
        return compute_metrics([p.forecast.generation for p in both], [p.actual.generation for p in both])

    def metrics(self, strategy, start=None, end=None) -> dict | None:
        return self.metrics_for(self.pairs(strategy, start, end))

    def metrics_by_hour_of_day(self, strategy, start=None, end=None) -> list[dict]:
        buckets = defaultdict(list)
        for p in self.pairs(strategy, start, end):
            if p.forecast and p.actual:
                buckets[p.start_time.hour].append(p)
        return [{"hour": h, **self.metrics_for(buckets[h])} for h in sorted(buckets)]

    def metrics_by_day(self, strategy, start=None, end=None) -> list[dict]:
        buckets = defaultdict(list)
        for p in self.pairs(strategy, start, end):
            if p.forecast and p.actual:
                buckets[p.start_time.date().isoformat()].append(p)
        return [{"date": d, **self.metrics_for(buckets[d])} for d in sorted(buckets)]

    def metrics_by_horizon(self, bin_hours: int = 4, max_hours: int = 48) -> list[dict]:
        """Error across all published forecasts, grouped by lead time (target - publish)."""
        buckets = defaultdict(lambda: ([], []))
        for f in self._repo.all_forecasts():
            if not (self._s.target_start <= f.start_time < self._s.target_end):
                continue
            a = self._repo.actual_at(f.start_time)
            h = f.horizon_hours
            if a is None or h < 0 or h >= max_hours:
                continue
            b = int(h // bin_hours) * bin_hours
            buckets[b][0].append(f.generation)
            buckets[b][1].append(a.generation)
        return [{"horizon_from": b, "horizon_to": b + bin_hours, **compute_metrics(*buckets[b])}
                for b in sorted(buckets)]

    def strategy_for(self, horizon_hours: float | None, cutoff_hour_utc: int | None) -> ForecastSelectionStrategy:
        if horizon_hours is not None:
            return HorizonStrategy(horizon_hours)
        return DayAheadCutoffStrategy(self._s.default_cutoff_hour_utc if cutoff_hour_utc is None else cutoff_hour_utc)

    def decision_day(self, delivery_date: datetime, cutoff_hour_utc: int | None) -> dict:
        """What the trader sees on D-1: latest forecast available at the cutoff, plus error context."""
        cutoff = self._s.default_cutoff_hour_utc if cutoff_hour_utc is None else cutoff_hour_utc
        strategy = DayAheadCutoffStrategy(cutoff)
        day = delivery_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        pairs = self.pairs(strategy, day, day + timedelta(days=1))
        # Historic error excluding the delivery day itself = what was knowable at decision time
        history = self.pairs(strategy, self._s.target_start, day)
        return {
            "delivery_date": day.date().isoformat(),
            "decision_deadline": (day - timedelta(days=1) + timedelta(hours=cutoff)),
            "pairs": pairs,
            "realised_metrics": self.metrics_for(pairs),
            "trailing_metrics": self.metrics_for(history),
        }

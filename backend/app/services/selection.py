from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from app.models.domain import Forecast
from app.repositories.wind_repository import WindDataRepository


class ForecastSelectionStrategy(ABC):
    """Decides which published forecast is 'the' forecast for a target period."""

    @abstractmethod
    def select(self, repo: WindDataRepository, target: datetime) -> Forecast | None: ...


class HorizonStrategy(ForecastSelectionStrategy):
    """Latest forecast published at least `hours` before the target start."""

    def __init__(self, hours: float):
        self.hours = hours

    def select(self, repo, target):
        return repo.latest_published_by(target, target - timedelta(hours=self.hours))


class DayAheadCutoffStrategy(ForecastSelectionStrategy):
    """Latest forecast published by `cutoff_hour_utc` on the day before the target's delivery day."""

    def __init__(self, cutoff_hour_utc: int):
        self.cutoff_hour_utc = cutoff_hour_utc

    def select(self, repo, target):
        day = target.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        deadline = day - timedelta(days=1) + timedelta(hours=self.cutoff_hour_utc)
        return repo.latest_published_by(target, deadline)

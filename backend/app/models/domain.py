from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Actual:
    start_time: datetime
    generation: float


@dataclass(frozen=True)
class Forecast:
    start_time: datetime
    publish_time: datetime
    generation: float

    @property
    def horizon_hours(self) -> float:
        return (self.start_time - self.publish_time).total_seconds() / 3600


@dataclass(frozen=True)
class Pair:
    """A target period with the selected forecast and (optional) actual."""
    start_time: datetime
    forecast: Forecast | None
    actual: Actual | None

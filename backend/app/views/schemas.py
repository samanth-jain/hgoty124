from datetime import datetime

from pydantic import BaseModel


class PointView(BaseModel):
    start_time: datetime
    forecast: float | None
    actual: float | None
    publish_time: datetime | None
    horizon_hours: float | None
    error: float | None


class MetricsView(BaseModel):
    n: int
    mae: float
    rmse: float
    bias: float
    mape: float | None
    nmae: float | None
    p50_abs_error: float
    p90_abs_error: float
    p99_abs_error: float
    max_abs_error: float


class SeriesResponse(BaseModel):
    points: list[PointView]
    metrics: MetricsView | None


class HourMetrics(MetricsView):
    hour: int


class DayMetrics(MetricsView):
    date: str


class HorizonMetrics(MetricsView):
    horizon_from: int
    horizon_to: int


class MetricsResponse(BaseModel):
    overall: MetricsView | None
    by_hour: list[HourMetrics]
    by_day: list[DayMetrics]


class DecisionResponse(BaseModel):
    delivery_date: str
    decision_deadline: datetime
    points: list[PointView]
    realised_metrics: MetricsView | None
    trailing_metrics: MetricsView | None


def point_view(p) -> PointView:
    f, a = p.forecast, p.actual
    return PointView(
        start_time=p.start_time,
        forecast=f.generation if f else None,
        actual=a.generation if a else None,
        publish_time=f.publish_time if f else None,
        horizon_hours=f.horizon_hours if f else None,
        error=(f.generation - a.generation) if f and a else None,
    )

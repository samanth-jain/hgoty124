from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_service
from app.services.analysis_service import AnalysisService
from app.views.schemas import (DecisionResponse, HorizonMetrics, MetricsResponse,
                               SeriesResponse, point_view)

router = APIRouter(prefix="/api")

Horizon = Query(None, ge=0, le=168, description="Min hours between publish and target. If omitted, day-ahead cutoff is used.")
Cutoff = Query(None, ge=0, le=23, description="UTC hour on D-1 (day-ahead cutoff)")


def _utc(d: datetime | None) -> datetime | None:
    if d is None:
        return None
    return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/series", response_model=SeriesResponse)
def series(start: datetime | None = None, end: datetime | None = None,
           horizon_hours: float | None = Horizon, cutoff_hour_utc: int | None = Cutoff,
           svc: AnalysisService = Depends(get_service)):
    strategy = svc.strategy_for(horizon_hours, cutoff_hour_utc)
    pairs = svc.series(strategy, _utc(start), _utc(end))
    return SeriesResponse(points=[point_view(p) for p in pairs], metrics=svc.metrics_for(pairs))


@router.get("/metrics", response_model=MetricsResponse)
def metrics(start: datetime | None = None, end: datetime | None = None,
            horizon_hours: float | None = Horizon, cutoff_hour_utc: int | None = Cutoff,
            svc: AnalysisService = Depends(get_service)):
    s, a, b = svc.strategy_for(horizon_hours, cutoff_hour_utc), _utc(start), _utc(end)
    return MetricsResponse(overall=svc.metrics(s, a, b),
                           by_hour=svc.metrics_by_hour_of_day(s, a, b),
                           by_day=svc.metrics_by_day(s, a, b))


@router.get("/metrics/by-horizon", response_model=list[HorizonMetrics])
def metrics_by_horizon(bin_hours: int = Query(4, ge=1, le=24), svc: AnalysisService = Depends(get_service)):
    return svc.metrics_by_horizon(bin_hours)


@router.get("/decision", response_model=DecisionResponse)
def decision(delivery_date: date, cutoff_hour_utc: int | None = Cutoff,
             svc: AnalysisService = Depends(get_service)):
    r = svc.decision_day(datetime(delivery_date.year, delivery_date.month, delivery_date.day), cutoff_hour_utc)
    return DecisionResponse(points=[point_view(p) for p in r.pop("pairs")], **r)

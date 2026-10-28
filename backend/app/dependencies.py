from functools import lru_cache

from app.config import settings
from app.repositories.elexon_client import ElexonClient
from app.repositories.wind_repository import WindDataRepository
from app.services.analysis_service import AnalysisService


@lru_cache
def get_service() -> AnalysisService:
    repo = WindDataRepository(settings, ElexonClient(settings))
    return AnalysisService(repo, settings)

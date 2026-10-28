# Wind Forecast Monitor

Web app for a UK day-ahead power buying team: shows the latest wind generation forecast available at decision time
and quantifies forecast accuracy (Elexon FUELHH actuals vs WINDFOR forecasts, January 2026, national level).

> AI tools (GitHub Copilot) were used to assist in building this application.
## Deployment
Link: [https://hgoty124-frontend.vercel.app/](https://hgoty124-frontend.vercel.app/)

## Structure
- `backend/` – Python (FastAPI), MVC:
  - `app/models` – domain dataclasses (Actual, Forecast, Pair)
  - `app/repositories` – `ElexonClient` (API gateway) and `WindDataRepository` (in-memory index + JSON file cache)
  - `app/services` – `AnalysisService`, error `metrics`, forecast `selection` strategies (Strategy pattern)
  - `app/views` – Pydantic response schemas
  - `app/controllers` – FastAPI routes; `dependencies.py` wires dependencies
  - `tests/` – pytest
- `frontend/` – React (Vite + Recharts): Day-ahead decision view and Forecast accuracy view
- `docker-compose.yml` – runs both

## Domain choices
- Error = forecast − actual (positive = over-forecast). Metrics: MAE, RMSE, bias, MAPE, P50/P90/P99 absolute error.
- "Forecast available at decision time": latest forecast published at/before a day-ahead cutoff on D-1
  (default 09:00 UTC, configurable), or generically, latest forecast published at least N hours before the target.
- WINDFOR is hourly; only target times present in both datasets are compared.

## Configuration
Copy `backend/.env.example` to `backend/.env` (and `frontend/.env.example` to `frontend/.env` if needed).
`.env` files are git-ignored. Defaults apply if no file exists; the Elexon API needs no key (`ELEXON_API_KEY` is optional).

## Run
Docker: `docker compose up --build` → http://localhost:8080

Local:
```
cd backend; pip install -r requirements.txt; uvicorn app.main:app --reload   # :8000
cd frontend; npm install; npm run dev                                        # :5173 (proxies /api)
cd backend; python -m pytest
```
First API call downloads January 2026 data from Elexon and caches it in `backend/data/`.

## API
`GET /api/series`, `/api/metrics`, `/api/metrics/by-horizon`, `/api/decision?delivery_date=2026-01-15`, `/api/health`



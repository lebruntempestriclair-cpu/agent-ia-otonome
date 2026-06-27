## 2027-06-26 - [FastAPI Route Optimization]
**Learning:** Pre-rendering static or semi-static FastAPI responses into a module-level constant (e.g., `HEALTH_RESPONSE_JSON`) and returning it via a `fastapi.Response` object bypasses internal Pydantic validation and JSON serialization on every request. This yielded a ~34% reduction in average latency and ~55% reduction in P95 latency for the `/health` endpoint in this application.
**Action:** Identify semi-static high-frequency endpoints (health, version, basic config) and pre-render their responses during application startup or as module-level constants.

## 2027-06-26 - [PR Hygiene]
**Learning:** Compiling and running tests in the local environment generates platform-specific artifacts like `__pycache__` that must be purged before submission to avoid repository bloat and potential runtime conflicts.
**Action:** Always run a cleanup command (e.g., `find . -name "__pycache__" -type d -exec rm -rf {} +`) as part of the pre-commit process.

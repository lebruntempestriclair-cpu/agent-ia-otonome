## 2025-06-19 - Pre-rendered JSON for static endpoints
**Learning:** Returning a raw `fastapi.Response` with pre-rendered JSON content (via `json.dumps`) bypasses FastAPI's internal Pydantic validation and serialization pipeline. This significantly improves performance for high-frequency, static endpoints like `/health`.
**Action:** Use `HEALTH_RESPONSE_JSON = json.dumps(...)` and `Response(content=HEALTH_RESPONSE_JSON, media_type="application/json")` for high-traffic status or health endpoints.

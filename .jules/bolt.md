# Bolt Journal - Critical Performance Learnings

## 2026-06-16 - FastAPI Endpoint Optimization
**Learning:** Returning a pre-rendered `Response` object and bypassing `response_model` validation/serialization in FastAPI significantly reduces latency for high-frequency, static-response endpoints like `/health`.
**Action:** Use `fastapi.Response` with pre-serialized JSON for static or semi-static health check endpoints.

## 2026-06-16 - Benchmarking Methodology
**Learning:** Reusing the same `TestClient` instance across benchmark iterations is crucial for stable and accurate measurements, as it avoids repeated app initialization overhead.
**Action:** Always instantiate `TestClient` once outside the benchmark loop.

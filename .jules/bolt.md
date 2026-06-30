## 2026-06-30 - Health Check Optimization via Pre-rendered JSON
**Learning:** Returning a raw `fastapi.Response` with pre-rendered JSON (serialized once at module level) bypasses Pydantic validation and serialization logic, which is a measurable performance win for high-traffic static-like endpoints.
**Action:** Identify static or semi-static metadata endpoints (health, version, config) and pre-render their JSON payload to reduce per-request CPU overhead.

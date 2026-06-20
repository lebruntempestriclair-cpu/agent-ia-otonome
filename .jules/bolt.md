## 2026-06-20 - Health Endpoint Optimization
**Learning:** Returning a pre-rendered JSON string via `fastapi.Response` bypasses Pydantic's internal validation and serialization, providing a measurable performance boost for high-frequency static endpoints like `/health`.
**Action:** Use pre-rendered JSON responses for static or semi-static metadata endpoints to minimize request latency.

## 2026-06-20 - Lazy Logging vs f-strings
**Learning:** f-strings in logging calls are evaluated even if the log level is disabled, leading to unnecessary overhead. Lazy string interpolation (`logger.info("msg %s", arg)`) avoids this by only formatting the string if the log level is active.
**Action:** Always use lazy string interpolation in logging calls, especially in performance-critical paths or high-volume handlers.

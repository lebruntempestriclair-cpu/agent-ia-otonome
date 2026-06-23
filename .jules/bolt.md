## 2026-06-23 - [Optimization: Pre-rendered JSON and Lazy Logging]
**Learning:** Returning a raw `fastapi.Response` with pre-rendered JSON bypasses Pydantic validation/serialization, significantly reducing tail latency (P95) even for small payloads. Also, benchmarking with `uvicorn --reload` enabled introduces significant noise; always disable it for accurate performance measurement.
**Action:** Use `Response(content=JSON_CONST, media_type="application/json")` for static/semi-static high-frequency endpoints. Always use lazy string interpolation in logging to avoid overhead in production.

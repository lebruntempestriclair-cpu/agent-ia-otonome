## 2026-06-21 - [FastAPI Health Endpoint Optimization]
**Learning:** Returning a pre-rendered JSON string via a `fastapi.Response` object bypasses Pydantic validation and internal FastAPI serialization, which can significantly reduce latency and CPU usage for high-traffic static endpoints like /health.
**Action:** Use `json.dumps()` at the module level for static responses and return them using `Response(content=PRE_RENDERED_JSON, media_type="application/json")`.

## 2026-06-21 - [Logging Performance]
**Learning:** Lazy string interpolation in logging (`logger.info("msg %s", arg)`) is more efficient than f-strings because the string formatting only occurs if the log level is enabled.
**Action:** Always prefer `%s` placeholders over f-strings in logging calls to minimize overhead in hot paths.

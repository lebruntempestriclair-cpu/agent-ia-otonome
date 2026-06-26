## 2026-06-26 - Pre-rendering JSON for static endpoints
**Learning:** Returning a raw `fastapi.Response` with pre-rendered JSON bypasses Pydantic validation and `jsonable_encoder` overhead, providing a measurable performance boost (up to 12% in P95 latency) for endpoints that return static or semi-static data.
**Action:** Use this pattern for health checks and other read-only endpoints with static responses. Always use the `responses` parameter in the route decorator to preserve OpenAPI documentation.

## 2026-06-26 - Lazy Logging for Performance
**Learning:** Lazy string interpolation in logging (`logger.info("msg %s", arg)`) is preferred over f-strings as it avoids string formatting if the log level is disabled.
**Action:** Consistently use lazy interpolation in high-frequency code paths.

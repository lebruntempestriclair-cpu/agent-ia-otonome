## 2026-06-25 - Pre-rendering FastAPI responses
**Learning:** Returning a pre-rendered JSON string via a `fastapi.Response` object bypasses Pydantic validation and serialization overhead, which is beneficial for static or semi-static high-traffic endpoints like `/health`. In this codebase, it reduced average latency by approximately 3%.
**Action:** Identify static endpoints and consider pre-rendering their responses into module-level constants. Use `response_model` in the decorator to maintain documentation even when returning a raw `Response`.

## 2026-06-25 - Python Logging Efficiency
**Learning:** Using f-strings in logging calls (`logger.info(f"...")`) performs string formatting even if the log level is not enabled. Lazy string interpolation (`logger.info("...", arg)`) is more efficient as the formatting only happens if the message is actually logged.
**Action:** Use lazy interpolation for all logging calls, especially in hot paths.

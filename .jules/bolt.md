# Bolt's Performance Journal

## 2026-06-14 - Initial Assessment
**Learning:** The application is a minimal FastAPI app. Most time in benchmarks is spent in the TestClient/Starlette overhead. Pydantic instantiation is ~11x slower than raw dict creation. f-strings in log calls are evaluated even if the log level is higher.
**Action:** Focus on reducing Pydantic overhead in high-frequency endpoints and optimize logging calls.

## 2026-06-14 - Optimized Route Responses and Logging
**Learning:** Returning Pydantic model instances in FastAPI routes triggers redundant validation if response_model is also set. Returning raw dictionaries and using the responses parameter for documentation bypasses this overhead. Lazy string interpolation in logger calls is more efficient than f-strings when the log message might not be emitted.
**Action:** Always return raw dictionaries in high-frequency routes and use the responses parameter in decorators for OpenAPI documentation. Use logger.info("msg %s", arg) instead of logger.info(f"msg {arg}").

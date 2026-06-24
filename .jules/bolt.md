## 2026-06-24 - Pre-rendering FastAPI health response
**Learning:** Returning a pre-rendered JSON string via a `fastapi.Response` object bypasses Pydantic's serialization and validation overhead, resulting in measurable latency reduction for high-frequency endpoints like `/health`.
**Action:** Use pre-rendered responses for static or semi-static monitoring endpoints where performance is critical.

## 2026-06-24 - Constant-time comparison for secrets
**Learning:** Using `secrets.compare_digest` is essential for validating API keys to prevent timing attacks, even if it adds negligible constant-time overhead.
**Action:** Always use `secrets.compare_digest` when comparing user-provided secrets with stored values.

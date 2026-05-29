## 2026-05-29 - [FastAPI High-Frequency Endpoint Optimization]
**Learning:** Returning raw dictionaries instead of Pydantic models in FastAPI bypasses validation and serialization overhead. This is significantly faster for high-frequency, static responses like `/health` where data structure is guaranteed.
**Action:** Use `responses={200: {"model": Model}}` to maintain OpenAPI documentation while returning a raw dict for performance-critical static endpoints.

## 2026-05-29 - [Environment Variable Caching]
**Learning:** Repetitive calls to `os.getenv` in request handlers introduce avoidable syscall overhead. Caching these in a singleton `Settings` class at startup improves performance and provides a central place for robust parsing and fallbacks.
**Action:** Implement a `Settings` singleton to load and validate all environment variables once at application startup.

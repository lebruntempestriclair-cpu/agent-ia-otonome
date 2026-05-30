## 2026-05-30 - [Config Cache and Health Endpoint Optimization]
**Learning:** High-frequency endpoints like `/health` in FastAPI can be significantly optimized by bypassing Pydantic model instantiation for simple responses, as the overhead of validation/serialization is often unnecessary for static data.
**Action:** Prefer returning raw dictionaries for simple, static responses while using the `responses` decorator parameter to maintain API documentation. Use a singleton `Settings` class to eliminate redundant `os.getenv` syscalls.

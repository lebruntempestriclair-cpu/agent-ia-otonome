## 2026-06-07 - [Optimization of /health and Settings Access]
**Learning:** Returning raw dictionaries instead of Pydantic models in FastAPI bypasses validation/serialization overhead, significantly improving performance for high-frequency static endpoints. Additionally, caching environment variables in a singleton Settings class avoids repeated `os.getenv` system calls.
**Action:** Always prefer raw dictionaries for high-frequency static endpoints and use a singleton pattern for application settings.

## 2025-05-22 - [Environment Variable Caching & Pydantic Bypass]
**Learning:** High-frequency endpoints like `/health` benefit significantly from bypassing Pydantic validation/serialization and caching environment variables. Repeated `os.getenv` calls and Pydantic model instantiation add measurable overhead in hot paths.
**Action:** Always cache configuration in a singleton at startup and use raw dictionaries for static or high-throughput metadata endpoints.

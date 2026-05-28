## 2025-05-22 - API Security and Information Leakage
**Vulnerability:** API endpoints were public and exposed raw exception details in error responses, potentially leaking sensitive system information.
**Learning:** Default FastAPI configurations often lack authentication, and naive `try-except` blocks that return `str(e)` in `HTTPException` can leak database schemas, internal paths, or logic details.
**Prevention:** Always use a centralized `Settings` class for configuration, implement API Key or similar authentication for all non-public endpoints, and use generic error messages for end-users while logging full details internally.

## 2025-05-22 - Information Leakage and CORS Security
**Vulnerability:** API endpoints were returning raw exception messages to clients, and CORS was configured with a wildcard while allowing credentials.
**Learning:** Returning `str(e)` in `HTTPException` detail can leak sensitive internal state (e.g., connection strings). In FastAPI/Starlette, `allow_origins=["*"]` is incompatible with `allow_credentials=True` and will cause a crash or security bypass.
**Prevention:** Always return generic error messages to clients while logging full details internally with `exc_info=True`. Use a centralized `Settings` class to validate and sanitize CORS origins, ensuring wildcards are never used with credentials.

## 2026-05-31 - [API Security Hardening]
**Vulnerability:** Information leakage through exception messages and lack of authentication on task endpoints.
**Learning:** Returning `str(e)` in `HTTPException` can leak sensitive internal details (stack traces, connection strings). Wildcard CORS `*` is too permissive for production.
**Prevention:** Always use generic error messages for 500 status codes in production. Cache settings at startup to avoid `os.getenv` overhead and ensure consistency. Use an authentication layer (like API Keys) for all non-public endpoints.

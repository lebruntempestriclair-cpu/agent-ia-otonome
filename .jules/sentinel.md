## 2026-06-10 - Timing Attack Protection & CORS Hardening
**Vulnerability:** Use of direct string comparison for API key validation and insecure CORS configuration with credentials enabled for wildcard origins.
**Learning:** FastAPI's default example code often uses simple string comparison for API keys, which is vulnerable to timing attacks. Also, enabling credentials for a wildcard origin is a security risk and causes issues with modern browser security policies.
**Prevention:** Always use `secrets.compare_digest` for comparing sensitive tokens and ensure `allow_credentials=False` when using wildcard origins in CORS middleware.

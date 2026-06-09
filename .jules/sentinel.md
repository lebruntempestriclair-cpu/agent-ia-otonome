## 2025-05-22 - [Security Hardening]
**Vulnerability:** Information leakage through verbose error messages and lack of authentication on task management endpoints.
**Learning:** API keys should be compared using constant-time comparison (like `secrets.compare_digest`) to prevent timing attacks.
**Prevention:** Always use `secrets.compare_digest` for secrets, implement a generic error response for production while logging details internally, and use a centralized `Settings` class for environment-based configuration.

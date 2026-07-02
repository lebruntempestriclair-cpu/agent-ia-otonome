## 2026-07-02 - API Key Security Hardening
**Vulnerability:** Timing attacks on API key validation and use of default secrets in production.
**Learning:** Standard string comparison (`==`) is vulnerable to timing attacks because it returns `False` as soon as a mismatch is found. Additionally, default configuration values often persist into production, creating a significant security gap.
**Prevention:** Use `secrets.compare_digest()` for constant-time comparison of sensitive tokens. Implement environment-aware safeguards that prevent the application from starting in `production` if critical secrets are still set to their default insecure values.

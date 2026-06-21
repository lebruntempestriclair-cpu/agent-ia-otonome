## 2025-05-14 - Initial Security Audit
**Vulnerability:** Timing attack vulnerability in API key validation.
**Learning:** Simple string comparison (`==`) in Python is not constant-time and can leak information about the secret key.
**Prevention:** Always use `secrets.compare_digest` for comparing sensitive values like API keys or tokens.

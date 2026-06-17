## 2024-06-17 - API Key Timing Attack Protection
**Vulnerability:** Standard string equality (==) for API key validation is vulnerable to timing attacks.
**Learning:** Python's `==` operator short-circuits, allowing an attacker to guess the key character by character by measuring response times.
**Prevention:** Always use `secrets.compare_digest()` for comparing secrets or API keys.

## 2024-06-17 - Strict CSP and FastAPI Docs
**Vulnerability:** Overly restrictive Content Security Policy (CSP).
**Learning:** `default-src 'self'` prevents Swagger UI (used by FastAPI's `/docs`) from loading necessary inline styles and scripts.
**Prevention:** If API documentation is required in production, CSP must be tuned to allow 'unsafe-inline' for the documentation endpoints or use a more granular policy.

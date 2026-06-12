## 2025-05-22 - Constant-time API Key Comparison
**Vulnerability:** Timing attacks on API key validation.
**Learning:** Standard string comparison (`==`) short-circuits, allowing attackers to guess secrets character by character based on response time.
**Prevention:** Always use `secrets.compare_digest` for validating sensitive tokens and keys.

## 2025-05-22 - CORS Wildcard with Credentials
**Vulnerability:** Runtime error or security risk when combining `allow_origins=["*"]` with `allow_credentials=True`.
**Learning:** Starlette/FastAPI raises a RuntimeError if both are enabled, as it is an insecure configuration.
**Prevention:** Dynamically set `allow_credentials=False` if a wildcard is detected in allowed origins, or enforce specific origin lists.

## 2025-05-22 - Secure Failure on Missing Configuration
**Vulnerability:** Application falling back to insecure defaults when configuration is missing.
**Learning:** Hardcoded default secrets in code are easy to overlook and can lead to production vulnerabilities.
**Prevention:** Remove default values for sensitive configuration and implement a "fail-secure" mechanism that prevents operation if required secrets are missing.

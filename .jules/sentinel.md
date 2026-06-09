## 2025-05-15 - Timing-Safe API Key Validation
**Vulnerability:** Timing attack vulnerability in API key validation.
**Learning:** Standard string comparison (`==`) in Python is short-circuiting, meaning it returns as soon as a character mismatch is found. This can be exploited by an attacker to guess a secret one character at a time by measuring the response time.
**Prevention:** Always use `secrets.compare_digest` for comparing secrets or tokens.

## 2025-05-15 - Insecure CORS Wildcard with Credentials
**Vulnerability:** Starlette's `CORSMiddleware` (used by FastAPI) raises a `RuntimeError` if `allow_credentials=True` and `allow_origins` includes a wildcard '*'.
**Learning:** Browsers also block credentialed requests to wildcard origins for security.
**Prevention:** Enforce `allow_credentials=False` if a wildcard is present in `allow_origins`, or better yet, require a explicit list of allowed origins.

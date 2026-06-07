# Sentinel's Journal - Critical Security Learnings

## 2026-06-07 - CORS Wildcard and Credentials Conflict
**Vulnerability:** Application crash or insecure CORS configuration.
**Learning:** Starlette's `CORSMiddleware` (used by FastAPI) raises a `RuntimeError` if `allow_credentials=True` and `allow_origins` contains `"*"`. This is because browsers do not allow this combination for security reasons.
**Prevention:** Always ensure `allow_credentials` is set to `False` if `allow_origins` includes a wildcard, or explicitly list allowed origins instead of using a wildcard.

## 2026-06-07 - Information Leakage in Error Responses
**Vulnerability:** Implementation detail leakage via stack traces or detailed error messages.
**Learning:** Returning `str(e)` in `HTTPException` can expose sensitive information about the backend (database structure, library versions, etc.).
**Prevention:** Log detailed errors internally with `exc_info=True` and return generic error messages (e.g., "Internal server error") to the client.

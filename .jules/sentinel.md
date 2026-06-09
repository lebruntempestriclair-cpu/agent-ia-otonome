## 2025-05-22 - Information Leakage in Error Responses
**Vulnerability:** API endpoints were returning raw exception strings in 500 error responses, potentially exposing stack traces and internal system details.
**Learning:** Defaulting `detail=str(e)` in `HTTPException` is dangerous for production as it leaks internal implementation details.
**Prevention:** Always use generic error messages for 500 errors in production while logging the full exception internally.

## 2025-05-22 - Insecure CORS with Credentials
**Vulnerability:** The application allowed wildcard origins (`"*"`) while also allowing credentials, which is insecure and blocked by modern browsers.
**Learning:** Browser security standards forbid `Access-Control-Allow-Origin: *` when `Access-Control-Allow-Credentials` is `true`.
**Prevention:** In production, either list specific allowed origins or disable `allow_credentials` when using wildcards.

## 2025-05-22 - Missing Authentication on Sensitive Endpoints
**Vulnerability:** Task creation and execution endpoints were public, allowing anyone to trigger agent actions.
**Learning:** High-risk endpoints must be protected by authentication from the start, even in development.
**Prevention:** Implement a standard API key authentication dependency for all sensitive routes.

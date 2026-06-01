## 2025-05-22 - Information Leakage in Error Responses
**Vulnerability:** API endpoints were returning raw exception messages directly to the client via `HTTPException(status_code=500, detail=str(e))`.
**Learning:** Returning raw exception messages can expose sensitive internal details (stack traces, database schemas, file paths, etc.) to attackers.
**Prevention:** Always catch exceptions, log the detailed error internally, and return a generic, non-informative error message (e.g., "Internal server error") to the client.

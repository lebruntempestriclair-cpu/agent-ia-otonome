## 2025-05-22 - Logging Secrets in Unauthorized Access Attempts
**Vulnerability:** Logging the actual value of an API key provided in an `X-API-Key` header during failed authentication attempts.
**Learning:** Even failed authentication attempts can contain sensitive data (typos of real keys, other credentials) that should never be persisted in logs.
**Prevention:** Always log generic messages for authentication failures and avoid including any part of the credentials in the log output.

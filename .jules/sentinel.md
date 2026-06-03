## 2025-05-15 - Hardening API Security and Error Handling
**Vulnerability:** Lack of authentication on task endpoints and potential information leakage via stack traces in error responses.
**Learning:** The application was in early development and prioritized functionality over security, leaving endpoints exposed and error handlers returning raw exception strings.
**Prevention:** Always implement a security dependency for sensitive endpoints early in development. Use a global error handling pattern that logs details internally but returns generic messages to clients.

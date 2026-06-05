## 2025-05-22 - API Security Hardening
**Vulnerability:** Information leakage via unhandled exceptions and missing/insecure authentication and CORS.
**Learning:** Default FastAPI exception handling can leak internal details (like IP addresses or DB structure) in `detail` field of 500 errors. CORS with `allow_credentials=True` cannot use wildcard origins.
**Prevention:** Always use generic error messages for production clients while logging full details internally. Implement explicit API Key checks for sensitive endpoints and restrict CORS origins to a whitelist.

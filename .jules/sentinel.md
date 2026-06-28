## 2025-05-15 - Timing Attack Prevention & CORS Security
**Vulnerability:** Insecure API key comparison and CORS wildcard with credentials.
**Learning:** Using `==` for secrets is vulnerable to timing attacks. CORS with `allow_origins=["*"]` and `allow_credentials=True` is insecure and often blocked by browsers.
**Prevention:** Always use `secrets.compare_digest` for constant-time secret comparison and disable credentials when using wildcard CORS origins.

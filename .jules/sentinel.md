## 2025-07-08 - Hardening API Authentication and CORS Security
**Vulnerability:** Timing attack on API key validation and insecure CORS wildcard configuration.
**Learning:** Standard string equality `==` is susceptible to timing attacks. `CORSMiddleware` with `allow_origins=["*"]` and `allow_credentials=True` is an insecure configuration rejected by modern browsers and potential CSRF risk.
**Prevention:** Always use `secrets.compare_digest` for secret comparisons. Ensure `allow_credentials=False` when using wildcard origins in CORS. Add environment-aware safeguards to prevent production deployments with default secrets.

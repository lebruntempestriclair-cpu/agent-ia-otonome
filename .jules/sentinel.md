## 2025-05-15 - Timing Attack and Insecure CORS in FastAPI

**Vulnerability:**
1. API key verification used standard string equality, which is susceptible to timing attacks.
2. `CORSMiddleware` was configured with `allow_origins=["*"]` and `allow_credentials=True`, which is insecure and causes a runtime error in FastAPI/Starlette.
3. The application could start in production with a hardcoded default API key even when authentication was required.

**Learning:**
- FastAPI/Starlette explicitly forbids `allow_credentials=True` when `allow_origins=["*"]` for security reasons (it would allow any site to make credentialed requests to the API).
- Using `secrets.compare_digest` is a critical requirement for any secret comparison to prevent information leakage through timing side-channels.
- Production environments must fail-fast if critical security configuration (like a non-default API key) is missing.

**Prevention:**
- Always use `secrets.compare_digest` for validating API keys or tokens.
- Ensure CORS policy follows the "least privilege" principle; never use `allow_credentials=True` with wildcard origins.
- Implement bootstrap checks in the configuration layer to validate that secrets are set when running in production.

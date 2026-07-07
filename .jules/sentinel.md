# Sentinel Security Journal

## 2025-05-22 - [Timing Attacks and CORS Misconfiguration]
**Vulnerability:** Use of standard equality operator (`==`) for API key validation and permissive CORS with credentials.
**Learning:** Standard string comparison in Python is not constant-time, allowing for timing attacks that can leak the API key. Permissive CORS (`allow_origins=["*"]`) combined with `allow_credentials=True` is an insecure pattern and often rejected by modern browsers for security reasons.
**Prevention:** Always use `secrets.compare_digest` for security-sensitive comparisons. When using wildcard origins in CORS, set `allow_credentials=False` unless specifically required and justified by other security layers.

## Security Principles for this Repository
- **Constant-time Auth:** Use `secrets.compare_digest` for all token/key validations.
- **Fail Fast & Explicitly:** Do not mask `HTTPException` in generic `try-except` blocks.
- **Production Safety:** Never use default secrets in production environments.
- **Least Privilege CORS:** Avoid wildcard origins with credentials.

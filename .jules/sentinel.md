## 2025-05-22 - Secure Error Handling and Timing Attack Protection
**Vulnerability:** Information leakage via unmasked exception details in API responses and potential timing attacks in API Key validation.
**Learning:** Directly returning `str(e)` in `HTTPException` can expose sensitive configuration details (e.g., credentials in connection strings) to end-users. Additionally, standard string comparison (`==`) for secrets is susceptible to timing attacks.
**Prevention:** Mask all internal exceptions with generic error messages in public API responses while logging full details internally. Use `secrets.compare_digest` for all cryptographic or security-sensitive string comparisons.

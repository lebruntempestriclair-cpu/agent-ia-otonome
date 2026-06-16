## 2026-06-16 - Timing Attack Vulnerability in API Key Validation
**Vulnerability:** The API key validation used standard string comparison (`==`), which is vulnerable to timing attacks.
**Learning:** Python's standard string comparison short-circuits on the first character mismatch, allowing an attacker to deduce the correct API key character by character by measuring response times.
**Prevention:** Always use `secrets.compare_digest` for comparing secrets, tokens, or API keys to ensure constant-time comparison.

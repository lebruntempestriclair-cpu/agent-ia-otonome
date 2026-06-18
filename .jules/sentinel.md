## 2025-05-15 - Timing Attack Vulnerability in API Key Verification
**Vulnerability:** The API key verification used standard string equality (`==`), which is susceptible to timing attacks. An attacker could potentially use timing differences to brute-force the API key.
**Learning:** Standard string comparison short-circuits as soon as a mismatch is found, leading to variable execution time based on the prefix match length.
**Prevention:** Always use constant-time comparison functions like `secrets.compare_digest()` for sensitive data such as API keys, tokens, and passwords.

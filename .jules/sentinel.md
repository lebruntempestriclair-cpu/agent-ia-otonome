## 2026-06-29 - Timing Attack Vulnerability in API Key Verification

**Vulnerability:** The API key verification logic used standard string equality (`==`), which is susceptible to timing attacks.

**Learning:** Standard string comparison in Python short-circuits as soon as a mismatch is found, meaning the time taken to compare two strings depends on how many characters match from the beginning. An attacker can exploit this to guess the API key character by character.

**Prevention:** Always use `secrets.compare_digest` for comparing secrets, API keys, and passwords. It performs a constant-time comparison, mitigating timing attacks.

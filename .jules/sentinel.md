## 2025-05-15 - Timing Attack Vulnerability in API Key Validation
**Vulnerability:** Standard string equality operators (==) were used for API key validation, which are susceptible to timing attacks as they short-circuit on the first mismatched character.
**Learning:** Even though the application uses FastAPI, manual validation of secrets must use constant-time comparison to prevent attackers from guessing the key character by character through latency measurements.
**Prevention:** Always use `secrets.compare_digest()` for comparing secrets, tokens, or API keys.

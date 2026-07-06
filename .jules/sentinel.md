# Sentinel Security Journal

## 2026-07-06 - [Timing Attack Prevention]
**Vulnerability:** API key verification was using standard equality comparison (`==`), which is susceptible to timing attacks.
**Learning:** Standard string comparison returns early as soon as it finds a mismatch, allowing an attacker to deduce the correct key byte-by-byte by measuring response times.
**Prevention:** Always use `secrets.compare_digest` for comparing security-sensitive strings like API keys, tokens, or passwords to ensure constant-time comparison.

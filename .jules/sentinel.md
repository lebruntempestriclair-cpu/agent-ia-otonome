## 2026-06-11 - Timing-attack vulnerability in API Key verification
**Vulnerability:** Insecure string comparison (`!=`) for API key validation.
**Learning:** Standard equality operators in Python are short-circuiting, meaning they return early as soon as a mismatch is found. This allows attackers to infer the secret character by character by measuring response times.
**Prevention:** Always use `secrets.compare_digest()` for comparing sensitive secrets like API keys, tokens, or passwords to ensure constant-time comparison.

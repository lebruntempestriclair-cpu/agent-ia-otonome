## 2026-06-20 - [Timing Attack Prevention]
**Vulnerability:** Standard string equality operators (==, !=) in Python short-circuit, returning early when a mismatch is found. This behavior is vulnerable to timing attacks during secret validation.
**Learning:** Constant-time comparison is necessary for security-sensitive checks like API keys or tokens.
**Prevention:** Use `secrets.compare_digest` for constant-time comparisons.

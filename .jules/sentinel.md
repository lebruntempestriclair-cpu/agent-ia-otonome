# Sentinel Security Journal

This journal contains critical security learnings for the Agent IA Autonome project.

## 2025-05-14 - Fix timing attack in API key validation
**Vulnerability:** The API key validation used standard string equality (`==`), which is susceptible to timing attacks.
**Learning:** Timing attacks can allow an attacker to guess the API key by measuring the time it takes for the server to respond to different inputs.
**Prevention:** Always use constant-time comparison functions like `secrets.compare_digest` for security-sensitive comparisons.

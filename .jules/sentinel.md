## 2026-06-13 - Timing Attack and Hardcoded Secret Fix
**Vulnerability:** Timing attack vulnerability in API key validation and hardcoded default secret.
**Learning:** Standard string comparison (`==`) short-circuits, allowing attackers to guess the key character by character by measuring response times. Providing a default secret in the code can lead to insecure deployments.
**Prevention:** Always use `secrets.compare_digest` for validating sensitive credentials and never provide default values for secrets in the codebase. Fail securely if required configuration is missing.

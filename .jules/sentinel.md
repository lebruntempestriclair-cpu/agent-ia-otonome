## 2026-06-14 - API Key Timing Attack Protection

**Vulnerability:**
1. Hardcoded API Key default ("default_secret_key") in `Settings`.
2. Timing attack vulnerability in API key validation due to standard string equality comparison.

**Learning:**
Standard string comparison in Python (`==` or `!=`) short-circuits, which can leak information about the secret being compared via timing differences. Defaulting sensitive configurations to hardcoded strings increases the risk of accidental exposure.

**Prevention:**
Use `secrets.compare_digest()` for all constant-time secret comparisons. Ensure sensitive configuration like API keys do not have default values in the code, forcing them to be provided via environment variables.

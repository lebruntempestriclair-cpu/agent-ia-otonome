# Sentinel Security Journal

## 2025-05-15 - API Key Timing Attack Protection
**Vulnerability:** API key comparison was using a standard equality operator (`==`), which is susceptible to timing attacks.
**Learning:** Even simple authentication mechanisms can have subtle vulnerabilities if not implemented with constant-time comparison.
**Prevention:** Always use `secrets.compare_digest` for comparing security-sensitive strings like API keys or tokens.

## 2025-05-15 - Production API Key Safeguard
**Vulnerability:** The application could be deployed to production with a default, hardcoded API key if not properly configured.
**Learning:** Default configurations often prioritize ease of use over security, leading to "insecure by default" deployments.
**Prevention:** Implement explicit checks in the application startup logic to prevent execution in production environments with default credentials.

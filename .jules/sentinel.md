## 2024-05-24 - API Key Security & Production Safeguards

**Vulnerability:** Timing attacks on API key verification and risk of insecure default configuration in production.
**Learning:** Standard equality operators (==) are susceptible to timing attacks. Also, applications often accidentally deploy with default credentials if not explicitly prevented in code.
**Prevention:** Use `secrets.compare_digest` for all security-sensitive string comparisons. Implement a "fail-fast" check in the configuration/settings layer that prevents the application from starting in production if default secrets are detected.

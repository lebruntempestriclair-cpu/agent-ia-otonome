# Sentinel Security Journal

## 2025-05-15 - [API Key Production Safeguard]
**Vulnerability:** Default API keys in production.
**Learning:** Developers often forget to change default values when deploying to production, especially if they are defined in the code or a template .env file.
**Prevention:** Implement a hard check in the application's configuration or startup logic that raises an error if the environment is 'production' and a default/known insecure value is detected for sensitive settings like API keys.

## 2025-05-15 - [Timing Attack in API Key Validation]
**Vulnerability:** Use of standard string comparison (`==` or `!=`) for secret validation.
**Learning:** Standard string comparison returns as soon as it finds a mismatch, allowing attackers to measure response times to guess the secret character by character.
**Prevention:** Always use constant-time comparison functions like `secrets.compare_digest` when validating secrets or tokens.

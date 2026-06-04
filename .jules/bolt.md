# Bolt Performance Journal

## 2025-06-04 - Initial Optimization Strategy
**Learning:** Pydantic model instantiation and repeated `os.getenv` calls in request handlers can introduce measurable overhead for high-frequency endpoints like `/health`.
**Action:** Use cached settings and return raw dictionaries in high-frequency static endpoints to bypass validation overhead when possible.

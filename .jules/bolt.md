## 2026-06-05 - Optimize environment variable access and health check
**Learning:** Repeated `os.getenv` calls and redundant Pydantic model instantiation in high-frequency endpoints like `/health` add measurable overhead (~10-14% in this environment). Caching settings in a singleton at startup and returning raw dictionaries for static responses provides a simple but effective boost.
**Action:** Use a `Settings` singleton for application configuration and prefer raw dictionaries for high-traffic static endpoints, while keeping `response_model` in the decorator for OpenAPI documentation.

## 2025-06-13 - [FastAPI Response Optimization]
**Learning:** Bypassing Pydantic's `response_model` in FastAPI by returning raw dictionaries and using the `responses` parameter for OpenAPI documentation significantly reduces CPU overhead on high-frequency "hot" paths (like health checks) by avoiding redundant validation and serialization cycles.
**Action:** Always consider using raw dictionaries for simple, stable, or high-frequency responses while maintaining documentation via the `responses={200: {"model": ...}}` decorator parameter.

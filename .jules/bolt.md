## 2025-06-01 - [FastAPI Serialization & Env Access Optimization]
**Learning:** Pydantic model instantiation for simple responses is significantly slower (~19x) than raw dictionary creation. Additionally, repeated `os.getenv` calls are ~34x slower than accessing cached values in a singleton class.
**Action:** Use a `Settings` singleton for environment variables and return raw dictionaries for high-frequency, simple endpoints while using the `responses` parameter in the route decorator to preserve OpenAPI schema documentation.

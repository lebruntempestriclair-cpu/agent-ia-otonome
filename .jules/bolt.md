## 2026-06-02 - Pydantic Model vs Raw Dict in FastAPI Responses
**Learning:** Returning a Pydantic model instance from a FastAPI route is significantly slower than returning a raw dictionary because FastAPI re-validates and serializes the model instance. Using the `responses` parameter in the route decorator allows maintaining OpenAPI documentation while bypassing this overhead.
**Action:** For high-frequency or static endpoints, return raw dictionaries and specify the model in the `responses` decorator parameter.

## 2026-06-02 - Environmental Variable Caching
**Learning:** Repeatedly calling `os.getenv` in request handlers or tight loops introduces measurable overhead (found to be ~18x slower than attribute access in this environment).
**Action:** Implement a singleton `Settings` class to cache environment variables at application startup.

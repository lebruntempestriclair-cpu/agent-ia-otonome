## 2026-06-15 - FastPath: Bypassing Pydantic validation for static responses

**Learning:** In FastAPI, using `response_model` in the decorator forces Pydantic validation/serialization even if the route returns a raw dictionary. For high-frequency static endpoints like `/health`, this adds unnecessary overhead. Moving the model to the `responses` parameter maintains OpenAPI docs while allowing the framework to return the dictionary directly.

**Action:** Use `responses={200: {"model": Model}}` and return a raw dict for high-frequency or static endpoints where validation is redundant.

## 2026-06-15 - Redundant Pydantic Instantiation

**Learning:** Manually instantiating a Pydantic model before returning it from a FastAPI route (e.g., `return MyModel(...)`) is redundant when a `response_model` is already specified in the decorator. FastAPI will perform its own validation/serialization, effectively doing the work twice.

**Action:** Return raw dictionaries from routes and let FastAPI handle the single validation pass against the `response_model`.

## 2026-06-15 - Lazy Logging vs F-Strings

**Learning:** Using f-strings in logging (e.g., `logger.info(f"{var}")`) evaluates the string even if the log level is disabled. Lazy interpolation (e.g., `logger.info("%s", var)`) defers formatting to the logging framework, which skips it entirely if the level is not active.

**Action:** Always use lazy string interpolation in logging calls to minimize overhead in hot paths.

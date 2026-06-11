## 2024-06-11 - Pydantic Double Validation Overhead
**Learning:** Returning a Pydantic model instance in a FastAPI route that also has a `response_model` parameter causes double validation/serialization, which significantly increases latency (approx 15-20% in benchmarks).
**Action:** For high-performance endpoints, return a raw dictionary instead of a Pydantic model instance, and use the `responses` parameter in the decorator for OpenAPI documentation instead of `response_model` if validation is already handled or if the performance gain outweighs the benefit of automatic validation.

## 2024-06-11 - Secure API Key Comparison
**Learning:** Standard string comparison (`==`) is vulnerable to timing attacks. While not a direct "speed" optimization in the traditional sense, `secrets.compare_digest` provides constant-time comparison which is essential for security.
**Action:** Always use `secrets.compare_digest` for sensitive credential comparison.

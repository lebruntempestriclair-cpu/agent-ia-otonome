## 2026-06-06 - [FastAPI response_model overhead]
**Learning:** Even if a handler returns a raw dictionary, FastAPI still performs full Pydantic validation and serialization if `response_model` is present in the route decorator. This adds significant overhead (~20x based on micro-benchmarks) for high-frequency static endpoints.
**Action:** Remove `response_model` from the decorator and use the `responses` parameter to maintain OpenAPI documentation while maximizing performance for high-frequency/static endpoints.

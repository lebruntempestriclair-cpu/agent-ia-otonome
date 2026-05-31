## 2025-05-15 - [Optimization of high-frequency endpoints]
**Learning:** Returning raw dictionaries instead of Pydantic models in FastAPI bypasses validation/serialization overhead, resulting in ~14x speedup for simple response bodies while maintaining documentation via the `responses` parameter.
**Action:** Use raw dictionaries for high-frequency, simple endpoints like `/health` when Pydantic validation is redundant.

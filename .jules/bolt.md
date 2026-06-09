## 2026-06-09 - [Optimizing FastAPI health check]
**Learning:** In FastAPI, using `response_model` on high-frequency endpoints like `/health` introduces Pydantic validation/serialization overhead (~12-20% in this environment).
**Action:** Use `responses={200: {"model": Model}}` instead of `response_model=Model` to maintain OpenAPI docs while bypassing runtime overhead when returning raw dictionaries.

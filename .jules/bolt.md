## 2026-06-12 - [Pydantic overhead in high-frequency endpoints]
**Learning:** Returning Pydantic model instances in FastAPI routes adds significant overhead (instantiation + validation + serialization). Bypassing 'response_model' and returning raw dictionaries can yield measurable gains for simple endpoints.
**Action:** Use the 'responses' decorator argument for documentation while returning raw dictionaries in hot paths like /health or high-frequency telemetry endpoints.

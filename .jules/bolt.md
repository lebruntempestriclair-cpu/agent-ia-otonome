## 2026-07-04 - Production-accurate Benchmarking
**Learning:** Benchmarking with `uvicorn`'s `reload=True` (default in development) introduces significant overhead and latency jitter. Additionally, FastAPI's Pydantic serialization adds measurable latency even for simple dictionary responses.
**Action:** Always disable reloader by setting `DEPLOYMENT_ENV=production` before running performance benchmarks. For high-traffic static endpoints, bypass Pydantic by returning a pre-rendered JSON string in a raw `fastapi.Response` object.

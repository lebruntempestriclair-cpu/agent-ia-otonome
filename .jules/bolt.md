## 2026-07-08 - Pre-rendered health check response
**Learning:** Pre-rendering JSON responses for static or semi-static metadata endpoints (like /health) and returning a raw FastAPI Response object significantly reduces latency by bypassing Pydantic validation and serialization cycles.
**Action:** Identify other high-frequency static endpoints and apply pre-rendering to reduce CPU overhead and response times.

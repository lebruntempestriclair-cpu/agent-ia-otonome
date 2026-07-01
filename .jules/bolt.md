# Bolt's Performance Journal - Agent IA Autonome

## 2026-07-01 - Optimizing the Health Endpoint
**Learning:** Returning a raw `fastapi.Response` with pre-rendered JSON can significantly reduce latency for high-traffic, semi-static endpoints by bypassing Pydantic serialization and validation.
**Action:** Use `responses={200: {"model": ResponseModel}}` in the APIRoute decorator to maintain documentation while returning raw responses.

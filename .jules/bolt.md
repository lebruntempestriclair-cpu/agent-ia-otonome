# Bolt's Journal - Critical Learnings

## 2026-06-22 - Initial Performance Audit
**Learning:** FastAPI's `response_model` and Pydantic validation add measurable overhead for simple static responses like `/health`. Returning a pre-rendered JSON string via `Response` object is significantly faster.
**Action:** Optimize `/health` and other static/semi-static endpoints by bypassing Pydantic when possible.

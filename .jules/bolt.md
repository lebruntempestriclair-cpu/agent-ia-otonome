# Bolt's Journal - Agent IA Autonome

## 2025-05-22 - Initial Performance Audit
**Learning:** The current `main.py` uses deprecated `@app.on_event` handlers and performs `os.getenv` calls inside request handlers. High-frequency endpoints like `/health` use Pydantic models for response serialization which adds unnecessary overhead for static data.
**Action:** Replace `@app.on_event` with `lifespan` context manager, implement a cached `Settings` class, and optimize `/health` to return a raw dictionary.

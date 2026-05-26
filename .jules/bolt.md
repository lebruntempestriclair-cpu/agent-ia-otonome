## 2025-05-15 - [Configuration & Lifecycle Optimization]
**Learning:** `os.getenv` calls in FastAPI request handlers (like `/health`) introduce unnecessary syscall overhead. While small per-call, it adds up in high-throughput endpoints. Additionally, using deprecated `on_event` handlers is less efficient than the newer `lifespan` context manager which handles startup/shutdown more cleanly.
**Action:** Implement a singleton `Settings` class to cache environment variables and migrate to `lifespan` handlers.

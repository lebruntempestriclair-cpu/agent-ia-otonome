## 2026-05-25 - [Enhancement] API Key Authentication
**Vulnerability:** Sensitive endpoints (/task/create, /tasks, /execute) were publicly accessible without any authentication.
**Learning:** The application was missing a security layer for its REST API, which is critical for an autonomous agent.
**Prevention:** Implemented an optional API Key authentication mechanism using FastAPI dependencies, allowing secure access via the X-API-Key header.

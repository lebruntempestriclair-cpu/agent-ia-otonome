# Bolt's Performance Journal

## 2026-07-02 - Uvicorn Reload Overhead in Benchmarking
**Learning:** Benchmarking the FastAPI application with uvicorn's `reload=True` (default in development) introduced a massive overhead, increasing mean latency from ~2ms to ~44ms. This overhead masks the actual performance characteristics of the endpoint and makes micro-optimizations difficult to measure accurately.
**Action:** Always disable uvicorn's auto-reload feature when performing performance benchmarks. In this codebase, this is achieved by setting `DEPLOYMENT_ENV=production`.

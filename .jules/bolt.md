## 2026-07-06 - Repo Hygiene & Focus
**Learning:** Python __pycache__ and binary artifacts can easily leak into git staging if .gitignore is missing them. Always verify git status and ignore patterns before submission. Bundling security or config changes with performance optimizations violates the "one optimization" constraint and can complicate reviews.
**Action:** Always check .gitignore for common Python exclusions and strictly adhere to the "ONE small improvement" rule per session.

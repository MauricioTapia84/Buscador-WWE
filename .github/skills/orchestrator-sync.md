# ⚖️ Global Alignment & Sync Skill

The primary tool for the `@orchestrator-agent` to keep the project coherent.

## 🎯 Purpose
Ensure changes in one domain (DB) are reflected in others (Backend, Docs, Diagrams).

## 🛠️ Actions
1. **Cross-Check**: If a table changes, trigger `@database-agent`, `@backend-agent`, and `@frontend-agent` instructions update to ensure API interfaces and Typescript/Zod schemas remain consistent.
2. **Docs Snyc**: Run `@documentation-agent` to update [CHANGELOG.md](Documentación/md-fuente/legacy/CHANGELOG.md).
3. **Knowledge Base Update**: Execute `extract_docs.py` (via `@study-orchestrator` or `@content-reader`) after massive changes to regenerate the `.txt` technical context.
4. **Diagram Update**: Prompt `@diagram-agent` to refresh `.drawio` files.
5. **Status Update**: Modify [AGENTS.md](.github/AGENTS.md) completion percentages.

## ⚠️ Constraints
- NEVER mark a feature as completed without documentation.
- Check for breaking changes before merging any `feature/*` to `develop`. This MUST be validated by `@dependency-pipeline-agent` and passing the `Jenkinsfile` CI pipeline.

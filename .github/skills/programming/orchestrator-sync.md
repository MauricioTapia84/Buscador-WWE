# ⚖️ Global Alignment & Sync Skill

The primary tool for the `@orchestrator-agent` to keep the project coherent.

## 🎯 Purpose
Ensure changes in one domain (DB) are reflected in others (Backend, Docs, Diagrams).

## 🛠️ Actions
1. **Cross-Check**: If a table changes, trigger `@database-agent` and `@backend-agent` instructions update.
2. **Docs Snyc**: Run `@documentation-agent` to update [CHANGELOG.md](Documentación/md-fuente/legacy/CHANGELOG.md).
3. **Diagram Update**: Prompt `@diagram-agent` to refresh `.drawio` files.
4. **Status Update**: Modify [AGENTS.md](.github/AGENTS.md) completion percentages.

## ⚠️ Constraints
- NEVER mark a feature as completed without documentation.
- Check for breaking changes before merging any `feature/*` to `develop`.

# 🗄️ SQL Migration Skill

Facilitates safe and versioned database schema updates for the `@database-agent`.

## 🎯 Purpose
Ensure all database changes are documented, follow 3NF, and include rollbacks.

## 🛠️ Actions
1. **Analyze Schema**: Read [BD_Diseño_3NF.txt](Documentación/Documentos/BD_Diseño_3NF.txt) first.
2. **Generate Migration**: Create a new `.sql` file in `Documentación/Documentos/` with `UP` and `DOWN` scripts.
3. **Verify Integrity**: Check for foreign key constraints and naming conventions (`PascalCase` for tables).
4. **Update Docs**: Automatically update [DATABASE_CONSOLIDADO.md](Documentación/md-fuente/DATABASE_CONSOLIDADO.md).

## ⚠️ Constraints
- Never use `DROP TABLE` without a `DOWN` script.
- All new columns must have a description comment.
- Use `IF NOT EXISTS` for table/index creation.

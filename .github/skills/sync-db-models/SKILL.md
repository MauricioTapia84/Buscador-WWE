# 🔄 Skill: Sincronización DB-Models

## 📌 Propósito
Sincronizar las entidades del Backend (Hexagonal) y los modelos de datos del Frontend (React) con el esquema oficial de la base de datos Azure SQL.

## 🛠️ Cuándo usar esta Skill
- Al detectar una discrepancia entre el `id` retornado por la API y el esperado por el Frontend.
- Después de una migración de base de datos (`.sql` en `Documentación/Documentos/Migrations/`).
- Al implementar nuevas features que involucren persistencia.

## 📋 Pasos de Ejecución
1. **Inspección de Esquema:**
   - Usar `mssql_run_query` sobre `INFORMATION_SCHEMA.COLUMNS` para la tabla objetivo.
2. **Validación de Infraestructura (Backend):**
   - Revisar `entities/`, `models/` y validaciones `Zod` en el backend.
3. **Validación de UI (Frontend):**
   - Revisar interfaces TypeScript e hooks de React Query.
4. **Corrección:**
   - Aplicar `replace_string_in_file` para unificar nombres de campos.
   - Asegurar que `camelCase` se use en código y coincida con el mapeo de `knex` (si aplica).

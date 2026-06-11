# 🚨 Error Mapping & Database Resilience Skill

Handles MSSQL and Knex specific errors.

## 🎯 Purpose
Convert low-level database errors into user-friendly and actionable API responses.

## 🛠️ Actions
1. **Error Catcher**: Map SQL error codes (e.g., 2627 for Unique Constraint) to HTTP 409.
2. **FK Validation**: Detect missing parent records before DB throws Foreign Key errors.
3. **Zod Integration**: Ensure DB constraints (length, type) are mirrored in Zod schemas.
4. **Audit Trail**: Ensure every error is logged in the `AuditoriaSeguridad` table if it indicates a potential attack.

## ⚠️ Constraints
- Don't leak raw SQL queries in API responses.
- Always use `try/catch` in Infrastructure layer repositories.

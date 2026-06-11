# 📭 Instrucción: Validación de Estados Vacíos (SSOT)

## 📌 Contexto
Debido a la **Ley del Proyecto #2 (SSOT)**, está prohibido el uso de archivos de "fallback" (ej: `tiendasFallback.ts`). Esto significa que si la base de datos no retorna datos, el usuario debe ver un estado vacío informativo en lugar de datos simulados.

## 🛠️ Reglas de Aplicación
1. **Detección de Hardcoding:**
   - Si encuentras importaciones de archivos terminaos en `*Fallback.ts` o `mockData.ts` en componentes de negocio, elimínalos.
2. **Implementación de Empty States:**
   - Todo componente que consuma datos de la API (vía React Query) debe manejar el caso `data.length === 0`.
   - El visual debe ser amigable: "No se encontraron barberías disponibles en este momento", siguiendo el diseño de Tailwind.
3. **Manejo de Errores:**
   - No fallar silenciosamente. Informar si es un error de conexión o simplemente falta de datos.

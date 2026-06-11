# ⚖️ Skill: Merge Mastery (Resolución de Conflictos)

**Propósito:** Proveer guías tácticas para resolver conflictos de Git en la arquitectura específica de FadeBooker, asegurando que la lógica de negocio y la estructura hexagonal no se rompan durante la integración.

## 🏛️ Prioridades por Capa

### 1. Backend (Arquitectura Hexagonal)
En caso de conflicto en estas carpetas, priorizar según:
- **`domain/entities`**: Mantener la definición más completa del modelo. Si dos miembros agregaron campos, **combinarlos**.
- **`interfaces/http/routes`**: Asegurar que todos los `operationId` sean únicos y que el orden de las rutas no cause sombras (ej. `/perfil` antes de `/:id`).
- **`infrastructure/adapters`**: Priorizar la versión que implemente mejor el manejo de errores global.

### 2. Frontend (Feature-Based)
- **`App.tsx` (Routing)**: **NUNCA** eliminar rutas de otros compañeros a menos que el usuario lo pida. Los conflictos aquí suelen ser incrementales; combinar los bloques de `Route`.
- **`features/[name]/ui`**: Si hay conflictos en componentes visuales, preferir la implementación que use **Tailwind CSS** sobre Bootstrap 5 si ambas están presentes.

### 3. Swagger / OpenAPI
- Siempre priorizar el archivo `openapi.yaml` (SSOT).
- Después de resolver conflictos en el YAML, ejecutar obligatoriamente `node fix_swagger.js` para regenerar los JSONs sincronizados.

## 🚨 Reglas de Oro
1. **Borrado de Marcadores:** Es innegociable eliminar todas las líneas `<<<<<<<`, `=======`, `>>>>>>>`.
2. **Verificación Sintáctica:** Tras resolver, ejecutar un chequeo de sintaxis rápido (o `npm run lint` si está disponible) para evitar `Unexpected token`.
3. **No Duplicar:** Verificar que al combinar bloques no se hayan duplicado importaciones o definiciones de variables al final del archivo.

## 💬 Comunicación
Si un conflicto afecta lógica nuclear de precios o citas, **detenerse y preguntar al usuario** proporcionando el contexto de ambas versiones.

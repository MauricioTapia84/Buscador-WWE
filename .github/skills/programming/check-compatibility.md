# 🛠️ Skill: Check Compatibility

**Propósito:** Garantizar que el entorno de ejecución del agente y el espacio de trabajo local sean coherentes con los requisitos del proyecto FadeBooker para evitar errores de compilación o fallos de conexión silenciosos.

## 📋 Cuándo usar
- Al iniciar una nueva sesión de codificación.
- Después de descargar cambios (`git pull`) de otros compañeros.
- Si se encuentran errores inesperados de "módulo no encontrado" o fallos de conexión a BD.

## 🔍 Protocolo de Verificación

### 1. Versiones de Software
- **Node.js:** Debe ser `^20.0.0` (Backend usa `node:20-alpine` en Docker).
- **Herramientas:** Verificar disponibilidad de `npm` y `git`.

### 2. Dependencias (`node_modules`)
- Si hay cambios en `package.json`, ejecutar la instalación correspondiente en la carpeta raíz del módulo:
  - Backend: `Producto/back-fadebooker/`
  - Frontend: `Producto/front-fadebooker/`

### 3. Variables de Entorno (`.env`)
- Comparar `.env` con `.env.example` en ambos módulos.
- **Backend:** Verificar `DB_PASSWORD`, `DB_SERVER`, `MP_ACCESS_TOKEN`, `CLOUDINARY_*`.
- **Frontend:** Verificar `VITE_API_URL`.

### 4. Puerto y Conectividad
- Backend: Puerto default `3000`.
- Frontend: Puerto default `5173`.
- Validar conexión a Azure SQL si se realizarán tareas de base de datos.

## � Resolución de Errores Comunes

### Error: `MODULE_NOT_FOUND`
Si al ejecutar `npm start` aparece un error de módulo no encontrado (ej. `dotenv`, `agent-base`):
1. **Limpieza Profunda:** Eliminar la carpeta `node_modules` y el archivo `package-lock.json`.
2. **Reinstalación:** Ejecutar `npm install` desde la raíz del módulo afectado (`Producto/back-fadebooker` o `Producto/front-fadebooker`).
3. **Persistencia del Error:** Si el error persiste (especialmente con `agent-base`), verificar la versión de Node.js instalada. Algunos módulos tienen comportamientos erráticos en versiones muy recientes (como Node v24). Se recomienda usar la versión LTS (Node 20).

## 🚀 Acciones Automatizadas Sugeridas
1. `node -v`
2. `npm install` (si notas discrepancias en `package-lock.json`)
3. `ls -la .env`

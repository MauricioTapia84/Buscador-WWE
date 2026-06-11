# 🛠️ Skill: Backend Setup Automation (Quick Fix)

**Propósito:** Proporcionar un mecanismo de "un solo comando" para reparar entornos de backend dañados, asegurando que la limpieza de caché y dependencias sea exhaustiva.

## 📋 Cuándo usar
- Inmediatamente después de un `git pull` con grandes cambios en el backend.
- Cuando `npm start` falla con errores de módulos internos de Node.
- Si hay inconsistencias entre el `package-lock.json` local y el remoto.

## 🛠️ Script de Reparación Rápida (`fix-env.sh`)

Se recomienda sugerir al usuario la creación o ejecución de este script en `Producto/back-fadebooker/`:

```bash
#!/bin/bash
echo "🧹 Iniciando limpieza profunda de dependencias..."

# Eliminar carpetas y archivos de bloqueo
rm -rf node_modules
rm -f package-lock.json

# Limpiar caché de npm (forzado)
npm cache clean --force

# Reinstalación limpia
echo "📦 Reinstalando dependencias..."
npm install

echo "🚀 Verificando inicio de backend..."
npm start
```

## 🔍 Validaciones Posteriores
Tras la ejecución, el agente debe:
1. Verificar que `node_modules` exista.
2. Confirmar que `npm start` ya no lance errores de `MODULE_NOT_FOUND`.
3. Validar que el archivo `.env` contenga las claves de Cloudinary corregidas (con mayúsculas).

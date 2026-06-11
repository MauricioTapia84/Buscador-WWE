# 🛠️ Skill: Node Version Manager (NVM/FNM)

**Propósito:** Asegurar que el desarrollador y el agente utilicen la versión de Node.js recomendada para el proyecto (`Node v20.x`) para evitar comportamientos inestables en módulos nativos y dependencias críticas.

## 📋 Cuándo usar
- Al detectar versiones de Node.js muy recientes (ej. v24+) o muy antiguas (ej. <v18).
- Si aparecen errores extraños de compilación en módulos como `tedious`, `bcryptjs` o `sharp`.
- Al configurar un nuevo entorno de desarrollo.

## 🔍 Protocolo de Cambio de Versión

### 1. Con NVM (Node Version Manager)
Si el usuario tiene NVM instalado:
```bash
# Instalar la versión LTS recomendada
nvm install 20
# Cambiar a la versión 20
nvm use 20
# Hacerla predeterminada para el proyecto
echo "20" > .nvmrc
```

### 2. Con FNM (Fast Node Manager)
Si el usuario prefiere FNM:
```bash
fnm install 20
fnm use 20
```

### 3. Sin Gestor de Versiones
Si el comando `node -v` muestra una versión incompatible y no hay gestor:
1. Recomendar al usuario instalar **NVM** (Linux/Mac) o **nvm-windows**.
2. Advertir que el uso de `sudo apt install nodejs` suele instalar versiones desactualizadas de los repositorios de sistema.

## 🚨 Advertencia sobre Node v24+
Se ha detectado que Node v24 puede causar problemas con el cargador de módulos CommonJS (`loader:1479`), disparando errores de `MODULE_NOT_FOUND` aunque las dependencias estén presentes. Siempre intentar bajar a la v20 si esto ocurre.

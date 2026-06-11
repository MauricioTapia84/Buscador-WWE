# 📋 Rúbrica de Arquitectura y Patrones - FadeBooker

**Versión:** 1.0.0

## 1. Arquitectura Hexagonal (Ports & Adapters)
- [ ] **Independencia del Dominio:** ¿La carpeta `src/domain` contiene CERO importaciones de `infrastructure` o `interfaces`?
- [ ] **Puertos Definidos:** ¿Existen interfaces/clases base en `domain/repositories` y `domain/services`?
- [ ] **Adaptadores:** ¿Los controladores (`interfaces/http`) y repositorios concretos (`infrastructure/database`) implementan los puertos?

## 2. Repository Pattern
- [ ] **Abstracción de Datos:** ¿Toda consulta a la base de datos se realiza a través de un repositorio?
- [ ] **Cero fugas de Knex/SQL:** ¿El servicio de aplicación recibe entidades de dominio y no objetos de base de datos?

## 3. Inyección de Dependencias
- [ ] **Sin Hardcoding:** ¿Los controladores instancian sus servicios pasándoles las dependencias en el constructor (o vía fábrica)?
- [ ] **Configuración Centralizada:** ¿La resolución de dependencias ocurre en un punto de entrada controlado?

## 4. Estándares de Código y Nomenclatura
- [ ] **Archivos:** `camelCase.js`
- [ ] **Carpetas:** `lowercase-with-hyphens`
- [ ] **Clases:** `PascalCase`
- [ ] **Anti-Duplicación:** ¿Se ha verificado que el final del archivo no contenga bloques de código fantasma?

## 5. Separación del Entregable
- [ ] **Raíz Limpia:** ¿La raíz de `/Producto/back-fadebooker` contiene solo los archivos necesarios para el runtime (Dockerfile, openapi, package.json)?
- [ ] **Contexto Externo:** ¿Todos los archivos de planificación, informes de progreso y guías de agentes residen en `.github/contexto_operativo/`?

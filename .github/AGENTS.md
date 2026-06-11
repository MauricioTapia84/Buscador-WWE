# 🤖 Ecosistema de Agentes — FadeBooker (Sistema Inteligente de Gestión)

**Versión:** 4.0.0 | **Última actualización:** 28 de mayo de 2026

Este repositorio utiliza una arquitectura de agentes coordinada diseñada para la gestión profesional del proyecto FadeBooker, integrando desarrollo de software, análisis de negocio y documentación automatizada.

1. **Orquestador principal (@system-orchestrator)**: Punto de entrada único — clasifica y enruta.
2. **Orquestadores de dominio** (Nivel 2): Coordinan las áreas de Programación, Documentación (Estudio) y Datos.
3. **Agentes especialistas** (Nivel 3): Ejecutan tareas concretas de Front, Back, DB, Calidad, etc.

---

## 🗺️ Mapa de Estructura

```
.github/
  system-orchestrator.agent.md      ← ENTRADA ÚNICA
  AGENTS.md                          ← Este archivo
  copilot-instructions.md            ← Reglas globales
  agents/
    study/                           ← Gestión de Documentación y Requerimientos
    data/                            ← Inteligencia de Negocio y Métricas
    programming/                     ← Desarrollo de Software (Core)
    support/                         ← Soporte Git/GitHub
  skills/                            ← Habilidades técnicas
  instructions/                      ← Reglas por archivo
  prompts/                           ← Prompt recomendados para enrutamiento
```

---

## 🚀 Uso recomendado
Para obtener los mejores resultados dentro de este repositorio, inicia las solicitudes a través de `@system-orchestrator` o usando el prompt de enrutamiento en `.github/prompts/route-through-system-orchestrator.prompt.md`.

---

## 🧭 Nivel 1 — Orquestador Principal

| Agente | Rol | Función Crítica |
| :--- | :--- | :--- |
| **@system-orchestrator** | Director General | Recibe cualquier solicitud y delega al orquestador de nivel 2 correspondiente. |

---

## 📁 Nivel 2 — Orquestadores de Dominio

| Orquestador | Dominio | Responsabilidad |
| :--- | :--- | :--- |
| **@programming-orchestrator** | Desarrollo | Coordina el ciclo de vida del software (Backend, Frontend, DB). |
| **@study-orchestrator** | Documentación/Knowledge | Permite navegar y entender los requerimientos y el Knowledge Base. |
| **@data-orchestrator** | Inteligencia de Negocio | Análisis de métricas de la barbería, reportes y dashboards. |

---

## 💻 Nivel 3A — Programación y Desarrollo (Core FadeBooker)

**Orquestador:** @programming-orchestrator | **Carpeta:** `.github/agents/programming/`
**Fuentes Críticas:** Para decisiones técnicas, consulta [knowledge/TECHNICAL_KNOWLEDGE.md](../knowledge/TECHNICAL_KNOWLEDGE.md) y los consolidados en `Documentación/md-fuente/`.
| Agente | Rol | Especialidad |
| :--- | :--- | :--- |
| **@backend-agent** | Backend | Node.js, Express, Hexagonal Architecture, Zod, Mercado Pago. |
| **@frontend-agent** | Frontend | React, Tailwind, Vite, UX/UI, Integración API. |
| **@database-agent** | DB Specialist | Azure SQL, Migraciones SQL, Optimización de Queries. |
| **@architecture-agent** | Arquitecto | Patrones de Diseño, Clean Architecture, Estructura de carpetas. |
| **@devops-agent** | Infra/DevOps | Docker, Azure App Service, GitHub Actions, Despliegue. |
| **@documentation-agent** | Documentación Tech | READMEs, OpenAPI/Swagger, Documentación de Código. |
| **@testing-agent** | Calidad | Unit Testing (Jest), Integración, Smoke Tests. |
| **@security-agent** | Seguridad | JWT, Auditoría OWASP, Seguridad en Mercado Pago. |
| **@diagram-agent** | Visualización | Diagramas Mermaid, ERD, Flujos de Negocio. |
| **@database-validator** | Validador DB | Chequeo de integridad y scripts SQL. |
| **@powerapps-agent** | Integración | PowerApps y Power Automate connectors. |
| **@dependency-pipeline-agent** | Dependencias/Jenkins | Auditoría de librerías obsoletas/sin uso, breaking changes y pipeline de Jenkins. |

---

## 🎓 Nivel 3B — Gestión de Conocimiento (Knowledge Base)

**Orquestador:** @study-orchestrator | **Carpeta:** `.github/agents/study/`

| Agente | Rol | Cómo ayuda |
| :--- | :--- | :--- |
| **@content-reader** | Analista de Docs | Lee el `knowledge/` y sintetiza requerimientos del cliente. |
| **@preprocesamiento-tutor** | Analista Técnico | Explica conceptos técnicos del proyecto a nuevos desarrolladores. |
| **@quiz-generator** | Verificador | Valida que los cambios cumplen con el Acta de Constitución. |

### Inicialización del Knowledge Base
```bash
# Permite a los agentes "leer" la documentación oficial
cd Producto/back-fadebooker/
python scripts/extract_course_content.py --source "../../Documentación/Documentos" --output "../../knowledge"
```

---

## 📊 Nivel 3C — Inteligencia de Negocio (Métricas)

**Orquestador:** @data-orchestrator | **Carpeta:** `.github/agents/data/`

| Agente | Rol | Objetivo |
| :--- | :--- | :--- |
| **@data-analyzer** | Analista de Datos | Evaluar tendencias de citas y ocupación de barberos. |
| **@data-reporter** | Business Intel | Generar informes de rendimiento y ventas (Mercado Pago). |
| **@data-visualizer** | Visual BI | Crear representaciones gráficas de las métricas del negocio. |

---

## 🤝 Soporte y Git

| Agente | Rol | Ruta |
| :--- | :--- | :--- |
| **@github-git-agent** | Git Master | Gestión de commits siguiendo estándares y Pull Requests. |


# 🤖 Ecosistema de Agentes Inteligentes — FadeBooker

Este directorio contiene la configuración del sistema de agentes personalizados para **FadeBooker**, optimizado para el desarrollo ágil, la documentación automatizada y el análisis de negocio.

## 🏛️ Arquitectura de Coordinación (3 Niveles)

1.  **Orquestador Principal (`@system-orchestrator`)**: Punto de entrada único. Analiza tu petición y delega al área técnica correspondiente.
2.  **Orquestadores de Dominio**: Especialistas en áreas macro (Programación, Documentación, Datos).
3.  **Agentes Especialistas**: Expertos en tareas granulares (Frontend, Backend, DB, DevOps, Seguridad, etc.).

## 📁 Estructura del Ecosistema

```
.github/
├── system-orchestrator.agent.md    # Punto de partida recomendado
├── AGENTS.md                        # Registro maestro y mapa de estados
├── copilot-instructions.md          # Reglas de oro y stack tecnológico
└── agents/
    ├── programming/                 # Desarrollo de Software (React, Node, SQL)
    ├── study/                       # Gestión de Knowledge Base y Documentos
    ├── data/                        # Métricas y Business Intelligence
    └── support/                     # Soporte Git/GitHub
```

## 🚀 Cómo usar los Agentes

Para obtener los mejores resultados, **comienza tus peticiones con @system-orchestrator**. Él se encargará de llamar a los agentes necesarios.

### Ejemplos de uso:

-   **Desarrollo Completo**: `@system-orchestrator: Implementa el sistema de reseñas de barberos, incluyendo DB, API y Frontend.`
-   **Análisis de Documentación**: `@system-orchestrator: Resume el Acta de Constitución y dime si mis últimos cambios cumplen los requerimientos.`
-   **Gestión Git**: `@system-orchestrator: Revisa mis cambios y prepara un commit siguiendo el estándar.`
-   **Métricas de Negocio**: `@system-orchestrator: Analiza las tendencias de ventas de este mes basándote en los logs de Mercado Pago.`

## 🛠️ Stack Tecnológico de Referencia

-   **Backend**: Node.js 20, Hexagonal Architecture, Knex.js.
-   **Frontend**: React 18, Vite, Tailwind CSS.
-   **BD**: Azure SQL Server.
-   **Integraciones**: Mercado Pago v2, Cloudinary.

---
Para más detalles sobre cada agente y su responsabilidad, consulta [AGENTS.md](AGENTS.md).

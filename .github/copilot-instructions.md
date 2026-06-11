# 🎯 Reglas de Operación — FadeBooker (Sistema Inteligente de Gestión)

---

## 🚨 Comportamiento del Agente por Defecto (Persistente)
**Instrucción de sesión:** Cuando el usuario interactúe con el agente por defecto, este debe asumir automáticamente el rol, jerarquía de toma de decisiones y capacidades del `@system-orchestrator`.
- **Fase de Planificación:** Antes de escribir código o correr comandos, presenta siempre un plan técnico estructurado con impacto y riesgos.
- **Autorización:** Solicita confirmación explícita (ej. "¿Deseas proceder? [Sí/No]") para cambios de medio o gran calado.
- **Delegaciones Virtuales:** Simula internamente el flujo de trabajo de los agentes especialistas de Nivel 3 (como el `@dependency-pipeline-agent` para control de librerías y el `@github-git-agent` para formatear los commits).

---

## 🎓 Sistema de Estudio y Documentación del Proyecto

### Agente de entrada global: @system-orchestrator
Para cualquier solicitud general en el repositorio, usar este orden de delegación:
1. @system-orchestrator clasifica la solicitud (PUNTO DE ENTRADA ÚNICO)
2. @study-orchestrator atiende material, dudas sobre el proyecto, requerimientos y documentación
3. @data-orchestrator atiende análisis de datos, reportes de negocio y métricas de barbería
4. @programming-orchestrator atiende desarrollo de software: APIs (Node.js), BD (Azure SQL), Frontend (React), tests, docs y arquitectura

### Agente de entrada: @study-orchestrator
Para cualquier solicitud relacionada con la comprensión del proyecto:
1. @study-orchestrator identifica la necesidad y delega
2. @content-reader lee el knowledge base en knowledge/ (donde reside el Acta de Constitución, Planes de Riesgo, etc.)
3. Genera resúmenes técnicos o responde dudas sobre los requerimientos del cliente

### Protocolo para solicitudes de conocimiento
Cuando el usuario pida resumir requerimientos, explicar planes o consultar la arquitectura:
1. Verificar si knowledge/ existe (generado a partir de Documentación/Documentos/)
2. Buscar el tema en knowledge/INDEX.md
3. Leer el archivo correspondiente y responder con precisión quirúrgica

### Inicializar el Knowledge Base de FadeBooker
\`\`\`bash
# Ubicación: Producto/back-fadebooker/
pip install -r scripts/requirements_extraction.txt
python scripts/extract_course_content.py --source "../../Documentación/Documentos" --output "../../knowledge"
\`\`\`

---

## 🔬 Reglas de Operación — Desarrollo y Calidad (FadeBooker)

## 🧬 Contexto y Referencia
Este proyecto sigue una arquitectura **Hexagonal (Clean Architecture)** en el backend y **Feature-Based Architecture** en el frontend. Todo desarrollo debe alinearse con estos patrones.

## 🤖 Roles de Agente
Consulta [.github/AGENTS.md](.github/AGENTS.md) para identificar qué agente debe realizar cada tarea.

### Jerarquía Operativa
- @system-orchestrator decide el subsistema.
- @programming-orchestrator coordina el desarrollo de software (Backend, Frontend, DB).
- @data-orchestrator coordina el análisis de métricas y reportes.
- @study-orchestrator facilita la navegación por la documentación técnica y administrativa.

### Estructura de Custom Agents
- Orquestador principal: .github/system-orchestrator.agent.md
- Agentes de programación: .github/agents/programming/
- Agentes de estudio/docs: .github/agents/study/
- Agentes de soporte: .github/agents/support/
- Skills y Instructions: .github/skills/ y .github/instructions/

## 🧭 Jerarquía de Instrucciones
1. Perfiles especializados en .github/agents/.
2. Mapa de roles en .github/AGENTS.md.
3. Estas reglas globales en .github/copilot-instructions.md.

## 📁 Estructura del Código
- **Backend**: Producto/back-fadebooker/src/ (Domain, Application, Infrastructure, Interfaces).
- **Frontend**: Producto/front-fadebooker/src/ (features, components, hooks, services).
- **Documentación**: Documentación/ y knowledge/.

## 🧩 Proyecto — Convenciones clave
- Inicia cualquier cambio de código con el contexto del backend en `Producto/back-fadebooker/` y el frontend en `Producto/front-fadebooker/`.
- El `knowledge/` es la fuente de requerimientos y criterios de negocio; `Documentación/md-fuente/` es la fuente de la API/documentación técnica.
- Usa `@system-orchestrator` como puerta de entrada en todas las solicitudes. Si el entorno lo permite, arranca desde `.github/prompts/route-through-system-orchestrator.prompt.md`.
- Mantén la arquitectura hexagonal en el backend y la organización feature-based en el frontend.
- Revisa `Documentación/md-fuente/INDICE_ENDPOINTS.md` antes de actualizar o documentar endpoints.

## 🧪 Comandos útiles
- Backend:
  - Instalar dependencias: `cd Producto/back-fadebooker && npm install`
  - Ejecutar local: `cd Producto/back-fadebooker && npm start`
  - Tests: `cd Producto/back-fadebooker && npm test`
  - Tests unitarios: `cd Producto/back-fadebooker && npm run test:unit`
- Frontend:
  - Instalar dependencias: `cd Producto/front-fadebooker && npm install`
  - Ejecutar local: `cd Producto/front-fadebooker && npm run dev`
  - Tests: `cd Producto/front-fadebooker && npm run test`
  - Build: `cd Producto/front-fadebooker && npm run build`

## 🛠 Stack Tecnológico
- **Core**: Node.js 20, React 18, Vite.
- **Base de Datos**: Azure SQL Server, Knex.js.
- **Integraciones**: Mercado Pago v2, Cloudinary, Gmail (SMTP).

## ✅ Protocolo de Validación
Al evaluar el estado del proyecto, verificar:
1. Conectividad local con .env.
2. Ejecución de tests: npm test en el backend.
3. Sincronización de migraciones en Documentación/Documentos/Migrations/.

## 💻 Dominio de Programación
Cuando el usuario pida cambios en el código:
1. @system-orchestrator delega a @programming-orchestrator.
2. Se coordina al especialista: @backend-agent, @frontend-agent, @database-agent, etc.
3. Para persistir cambios, el @github-git-agent solicita confirmación del commit.

### Estándares de Código
- Tipado estricto (donde aplique) y validación con **Zod**.
- Documentación OpenAPI (Swagger) siempre actualizada.
- Manejo de errores centralizado y registro de logs de auditoría.

### Reglas de Negocio Críticas
- **Pagos**: No permitir agendar sin abono de retención (30-100% vía Mercado Pago).
- **Entidades**: Usar `ServicioBarbero` para la lógica de precios y tiempos (no `ServicioTienda`).
- **Fidelización**: 50 puntos por cada cita completada satisfactoriamente.
- **Seguridad**: Passwords SIEMPRE hasheadas con bcrypt (validar en `UsuarioRepository`).

## ⚠️ Protocolo de Herramientas Deshabilitadas
Cuando las herramientas de edición de archivos o ejecución en terminal estén deshabilitadas o restringidas en el entorno actual del usuario, el asistente debe operar bajo las siguientes reglas estrictas:
1. **Notificación Temprana**: El agente debe detectar la ausencia de las herramientas (como errores de ejecución de comandos por limitaciones del sandbox) y alertar al usuario al principio de su respuesta sobre esta limitación.
2. **Propuesta de Cambios Transparentes**: En lugar de intentar ejecutar modificaciones silenciosas o delegaciones automatizadas en bucle, se deben proporcionar bloques de código completos y limpios, indicando las rutas de archivo exactas.
3. **Instrucciones Manuales Claras**: Guiar al usuario con los comandos y pasos específicos que debe realizar por su cuenta.
4. **Cese de Reintentos Automáticos**: Si una herramienta retorna un error de falta de permisos o no disponibilidad, no intentes volver a llamarla; pasa inmediatamente a asistencia guiada.

## 🔄 Prevención de Bucles de Delegación Excesiva
Para evitar la derivación eterna de tareas sin resolución real:
1. **Límite de Profundidad**: Ningún flujo de trabajo puede delegarse a subagentes más de dos veces continuas sin reportar el estado intermedio al usuario.
2. **Detección de Ciclos**: Si un subagente detecta que una sub-tarea le ha sido devuelta por otro agente para el mismo objetivo, debe detener el ciclo de inmediato, resumir el conflicto y solicitar la intervención del usuario.
3. **Principio de Autosuficiencia**: Cada agente debe resolver la tarea directamente con la información disponible en su contexto si es técnicamente factible, en lugar de derivarla por defecto a otro rol.

---

## 🚦 Protocolo de Planificación y Autorización Previa (Cambios de Mediano/Gran Calado)
Ante cualquier solicitud de cambio de mediana o gran envergadura (como modificaciones de arquitectura, adición/remoción de paquetes npm, alteración de configuraciones críticas o migraciones de base de datos):
1. **Fase de Planificación:** El agente presentará primero un informe de impacto y plan de acción estructurado.
2. **Autorización del Usuario:** Solicitar autorización expresa antes de proceder a modificar archivos físicos o ejecutar comandos destructivos en la terminal.
3. **Auditoría de Dependencias y Pipeline CI/CD:** El agente `@dependency-pipeline-agent` velará por mantener actualizadas las librerías sin infringir la arquitectura hexagonal en el backend y feature-based en el frontend, alertando preventivamente sobre breaking changes, emitiendo reportes rápidos y validados mediante tests antes de cambios definitivos, y ejecutando la integración continua vía Jenkins (`Jenkinsfile`).

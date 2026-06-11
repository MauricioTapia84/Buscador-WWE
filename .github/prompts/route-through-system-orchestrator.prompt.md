---
description: "Ruta de entrada por defecto para el editor. Clasifica cualquier solicitud y delega primero al orquestador principal, que decide si corresponde al sistema educativo o al pipeline EDA-ACV."
---

# Ruta por defecto al orquestador principal

Usa este prompt como punto de entrada cuando el usuario quiera trabajar desde el editor sin decidir manualmente a qué sistema pertenece la solicitud.

## Objetivo

1. Leer la solicitud del usuario.
2. Clasificarla en una de estas rutas:
   - `@study-orchestrator` para estudio, resúmenes, dudas, quizzes y material de clase.
   - `@data-orchestrator` para limpieza, modelado, evaluación y artefactos del pipeline EDA-ACV.
3. Si la solicitud es mixta, coordinar ambos subsistemas en orden.
4. Responder con una sola salida coherente, dejando trazabilidad de qué orquestador interno se usó.

## Regla principal

El usuario no debe elegir el orquestador interno. Primero se consulta a `@system-orchestrator` y luego ese orquestador deriva el trabajo.

## Ejemplo de uso

- "Resume el tema de escalamiento" → `@system-orchestrator` → `@study-orchestrator`
- "Revisa el estado del pipeline ACV" → `@system-orchestrator` → `@data-orchestrator`
- "Explica y luego genera un quiz" → `@system-orchestrator` → `@study-orchestrator`

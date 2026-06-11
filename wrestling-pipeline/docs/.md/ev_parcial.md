 # Evaluación Parcial N°3 — Instrucciones y Pauta

 ## Resumen general

 - Asignatura: SCY1101 — Programación para la Ciencia de Datos
 - Tiempo asignado: 4 semanas (encargo) y 15 minutos (presentación)
 - Ponderación total: 40% (Encargo 10% grupal, Presentación 30% individual)

 ## Instrucciones generales

 Esta evaluación busca que los estudiantes desarrollen y desplieguen un proyecto end-to-end que integre al menos tres fuentes de datos (CSV/Excel, API REST, base de datos SQL/NoSQL), construyan un pipeline ETL automatizado, visualicen resultados en dashboards interactivos y gestionen el ciclo de vida con buenas prácticas (Git) y despliegue en Docker.

 Cada estudiante defenderá individualmente la solución, la arquitectura y las decisiones técnicas.

 ## Requerimientos entregable

 - Pipeline ETL completo (scripts y notebooks) integrando al menos 3 fuentes, con validación de esquemas y manejo avanzado de errores.
 - Documentación técnica: README, diagramas de arquitectura, documentación de APIs, manual de usuario y guía de despliegue.
 - Dashboard interactivo (Plotly Dash o Streamlit) con visualizaciones por audiencia.
 - Evidencia de trabajo colaborativo en Git (ramas, PRs, revisiones, issues).
 - Containerización con Docker: Dockerfiles, docker-compose, variables de entorno y scripts de despliegue.

 ## Estructura de carpetas recomendada

 ```
 /etl/
 /dashboards/
 /docs/
 /api/
 /docker/
 /tests/
 /data/
 /repo/
 ```

 ## Aspectos formales a evaluar

 - Código limpio y documentado (docstrings).
 - Testing automatizado e informes.
 - Configuración por variables de entorno y logging profesional.
 - Documentación actualizada y exhaustiva.
 - Optimización para ejecución reproducible y eficiente.

 ## Pauta de evaluación (resumen por indicadores)

 1) Pipeline ETL robusto — 20%
 - Integra múltiples fuentes, validación robusta, manejo avanzado de errores y optimización.

 2) Documentación técnica completa — 20%

 3) Dashboard interactivo — 25%

 4) Uso profesional de Git — 15%

 5) Docker y despliegue — 20%

 Dimensión Presentación (varios ítems, suma 100% del bloque de presentación): demo end-to-end, dashboards, proceso colaborativo y metodologías.

 ## Observaciones clave para la implementación

 - Mínimo 3 fuentes de datos distintas.
 - Pruebas, validación de esquemas y manejo de errores son requisitos explícitos para obtener puntaje alto.
 - Evidencia de colaboración (PRs, issues) requerida.
 - Preferencia por demo en Docker y orquestación vía `docker-compose`.

 ---

 Archivo generado automáticamente a partir de las páginas del enunciado (OCR/entrada). Revisa y dime si quieres que lo amplíe o cambie la estructura.

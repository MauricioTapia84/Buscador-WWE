# Evaluación Final Transversal - SCY1101 (Programación para la Ciencia de Datos)

## 1. Instrucciones Generales
- **Ponderación:** 40% de la nota de la asignatura.
- **Tiempos:** 3 semanas para el encargo (taller) y 15 minutos para la presentación.
- **Distribución:**
  - Encargo (30%) - Grupal.
  - Presentación (70%) - Individual.
- **Objetivo:** Diseñar, implementar y presentar una solución completa de ciencia de datos, abarcando desde la gestión avanzada (ETL) hasta la entrega de valor con ML, APIs, dashboards interactivos y despliegue profesional (Git, Docker, CI/CD).

## 2. Entregables del Encargo

### A. Solución Técnica Completa
1. **Arquitectura profesional:** Organización modular y buenas prácticas.
2. **Pipeline ETL:** Integración de múltiples fuentes (CSV/Excel, API REST, BBDD), validación avanzada y manejo robusto de errores.
3. **Modelos ML:** Implementación de algoritmos supervisados/no supervisados, tuning de hiperparámetros (Scikit-learn) y análisis de métricas de negocio.
4. **API REST y Dashboard:** Servicios funcionales, endpoints documentados y dashboards interactivos orientados al usuario final.
5. **Containerización y CI/CD:** Dockerfiles, `docker-compose`, scripts y workflows de integración continua.

### B. Informe Técnico Ejecutivo
1. **Executive summary:** Para directivos (problema, enfoque, resultados, valor).
2. **Metodología y justificación:** Justificación técnica de enfoques y modelos.
3. **Análisis de resultados:** Métricas y KPIs de negocio.
4. **Documentación:** Exhaustiva sobre APIs, deployment y troubleshooting.
5. **Anexos:** Código, diagramas y evidencias de pruebas.

### C. Estructura de Proyecto Recomendada
- `/etl/` (scripts y notebooks)
- `/models/`
- `/api/`
- `/dashboards/`
- `/docker/`
- `/docs/`
- `/tests/`
- `/repo/` (evidencias de Git)
- `/data/`
- `README.md`, archivos de configuración, scripts de automatización.

### D. Aspectos Formales
- Código modular y documentado con `docstrings`.
- Testing automatizado.
- Uso de variables de entorno y `logging` profesional.
- Documentación clara y actualizada.

## 3. Consideraciones para la Presentación
- **Business context:** Problema de negocio y valor generado.
- **Technical solution:** Arquitectura, pipelines, modelos, APIs y despliegue.
- **Live demo:** Demostración del funcionamiento real end-to-end.
- **Results & impact:** Visualizaciones de métricas y reflexión.
- **Colaboración:** Defensa del aporte individual en el grupo.

## 4. Pauta de Evaluación (Rúbrica)

### Dimensión: Encargo (30%) - Evaluado Grupal
*Para obtener el 100% en cada indicador:*
1. **IEE 1.1.1 (20%): Operaciones Pandas:** Utiliza filtros avanzados, agrupaciones múltiples y joins complejos optimizados, sin errores.
2. **IEE 1.2.1 (20%): Transformaciones a Gran Escala:** Aplica broadcasting, pivot, reshape, chunking y vectorización para optimizar memoria.
3. **IEE 1.3.1 (20%): Flujos de Limpieza:** Flujo completo y documentado, múltiples técnicas de imputación/limpieza, justificación técnica sólida y validada.
4. **IEE 2.1.1 (20%): Múltiples Modelos Scikit-learn:** Implementa y configura múltiples modelos de clasificación/regresión con pipelines, justificando cada decisión técnica.
5. **IEE 3.1.1 (20%): Pipeline ETL Robusto:** Integra múltiples fuentes, validación robusta, manejo avanzado de errores y óptimo para grandes volúmenes.

### Dimensión: Presentación (70%) - Evaluado Individual
*Para obtener el 100% en cada indicador:*
6. **IEP 1.1.3 (20%): Explicación Pandas:** Explica operaciones con argumentos técnicos, justifica decisiones con ejemplos y terminología.
7. **IEP 1.2.2 (15%): Comprensión Transformaciones:** Domina y explica el impacto de las transformaciones en rendimiento y memoria.
8. **IEP 1.3.2 (15%): Justificación Limpieza:** Justificación clara, cuantifica el impacto y propone mejoras.
9. **IEP 2.1.3 (15%): Explicación Modelos ML:** Explica y justifica decisiones de algoritmos supervisados según la naturaleza del problema.
10. **IEP 2.2.2 (15%): Interpreta Métricas:** Interpreta métricas relevantes, compara modelos y explica trade-offs con apoyo visual.
11. **IEP 3.1.1 (20%): Demo Pipeline End-to-End:** Demo fluida, explicación detallada de arquitectura técnica.
12. **IEP 3.3.1 (15%): Proceso Colaborativo:** Explica metodologías de gestión de proyecto, uso de herramientas, analiza el trabajo grupal y propone mejoras.
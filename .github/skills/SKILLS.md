# Custom Skills — Ciencia de Datos

---

## 🎓 Skills de Estudio (Sistema Educativo)

## Skill: summarize-topic
- **Description:** Resume un tema específico de cualquier asignatura usando el knowledge base extraído en `knowledge/`. Ideal para repasar antes de una clase o evaluación.
- **Prompt:** "Lee el archivo Markdown correspondiente al tema solicitado dentro de `knowledge/[asignatura]/`. Si el knowledge base no existe, lee el notebook o PDF original en `Semestre 1 mención/`. Produce: (1) lista de conceptos clave con definición breve, (2) síntesis del tema en 200-300 palabras, (3) 3 puntos más importantes para recordar, (4) un ejemplo de código si aplica. Indica siempre la fuente exacta del material usado."

## Skill: generate-quiz
- **Description:** Genera evaluaciones de práctica (opción múltiple, V/F, desarrollo o código) basadas en el material real del curso. El `@study-orchestrator` debe confirmar asignatura, tema y tipo antes de invocarla.
- **Prompt:** "Usando el archivo del knowledge base del tema indicado, genera una evaluación con: (1) 5 preguntas de opción múltiple con 4 alternativas cada una, (2) 3 preguntas de verdadero/falso con justificación, (3) 2 preguntas de desarrollo corto. Al final incluye las respuestas correctas con explicación. Las preguntas deben estar directamente basadas en el contenido del archivo leído, no en conocimiento general."

## Skill: explain-concept
- **Description:** Explica un concepto específico del curso en tres niveles: definición simple, explicación técnica y ejemplo de código. Referencia siempre el material del curso.
- **Prompt:** "Para el concepto solicitado: (1) da una definición simple en 1-2 oraciones como si explicaras a alguien sin conocimiento técnico, (2) explica técnicamente el concepto con sus componentes y fórmulas si aplica, (3) muestra un ejemplo de código en Python con pandas/scikit-learn comentado línea a línea, (4) indica en qué archivo del knowledge base o del curso original encontrar más información sobre este concepto."

## Skill: help-with-project
- **Description:** Guía la estructura y desarrollo de proyectos académicos y evaluaciones prácticas. Revisa notebooks, sugiere mejoras y ayuda a organizar el flujo de trabajo.
- **Prompt:** "Analiza el archivo o notebook indicado por el usuario. Proporciona: (1) evaluación de la estructura general del código (organización, claridad, reproducibilidad), (2) identificación de problemas o errores técnicos, (3) sugerencias de mejora ordenadas por prioridad, (4) verificación de que el flujo sigue las buenas prácticas del curso (preprocesamiento → modelado → evaluación → reporte). Si el usuario tiene una rúbrica de evaluación, úsala como referencia principal para las sugerencias."

## Skill: build-study-plan
- **Description:** Crea un plan de estudio personalizado para una evaluación o unidad, priorizando temas según el material disponible y el tiempo del estudiante.
- **Prompt:** "Dado el tema o unidad y el tiempo disponible indicado por el usuario, lee el INDEX.md del knowledge base y los archivos relevantes. Genera un plan de estudio con: (1) lista de temas ordenados por importancia, (2) estimación de tiempo sugerido por tema, (3) orden de lectura recomendado de los archivos del knowledge base, (4) qué ejercicios o notebooks practicar, (5) preguntas clave que el estudiante debe poder responder al terminar el estudio."

## Skill: extract-knowledge-base
- **Description:** Verifica y ejecuta el proceso de extracción del knowledge base desde los archivos originales del curso.
- **Prompt:** "Verifica si la carpeta `knowledge/` existe y tiene contenido revisando con list_dir. Si está vacía o no existe, informa al usuario que debe ejecutar: `pip install -r scripts/requirements_extraction.txt && python scripts/extract_course_content.py`. Si ya existe, muestra el contenido de `knowledge/INDEX.md` para que el usuario sepa qué material está disponible para consulta."

---

## 🔬 Skills de Pipeline de Datos (Proyecto EDA-ACV)

## Skill: audit-architecture
- **Description:** Compara la estructura actual de carpetas de `mi_proyecto/` con las exigencias de `AGENTS.md`.
- **Prompt:** Toma como referencia de éxito la organización en `contexto_profesor/` y genera un checklist en Markdown indicando qué carpetas o archivos faltan crear o reubicar.

## Skill: check-data-leakage
- **Description:** Examina los cuadernos y scripts de modelado para asegurar que no hay contaminación de datos en la validación cruzada o en el remuestreo con SMOTE.
- **Prompt:** "Revisa los archivos de modelado en `mi_proyecto/notebooks/` y `mi_proyecto/src/`. Busca activamente cualquier señal de fuga de datos (data leakage), verificando que el escalado (StandardScaler), la imputación y cualquier eventual balanceo se ejecuten dentro de `Pipeline` y del bucle de validación cruzada (`StratifiedKFold`). Reporta de forma crítica si los datos de prueba contaminan el entrenamiento y deja la explicación en Markdown, con foco en los módulos oficiales `data_preprocessing.py`, `model_training.py`, `model_evaluation.py` y `hyperparameter_tuning.py`."

## Skill: modularize-colab
- **Description:** Ayuda a extraer bloques de código del Jupyter Notebook/Colab existente y los convierte en módulos limpios `.py` listos para producción.
- **Prompt:** "Toma las funciones de preprocesamiento, modelado o evaluación del notebook que se indique en `mi_proyecto/` y conviértelas en código modular listo para producción dentro de los módulos oficiales de `mi_proyecto/src/`: `data_preprocessing.py`, `model_training.py`, `model_evaluation.py` y `hyperparameter_tuning.py`. Mantén docstrings claras, compatibilidad con Scikit-Learn y trazabilidad para que los notebooks importen desde `src/` en vez de duplicar lógica."

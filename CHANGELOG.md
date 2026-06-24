# CHANGELOG

## 2026-06-24

### Correcciones aplicadas

- `wrestling-pipeline/etl/run_etl.py`
  - se corrigió el import roto que impedía ejecutar el ETL
  - el fallback de nombres ahora usa campeones históricos + nombres WWE curados
  - se persiste `wrestlers_thesportsdb.csv` antes de la limpieza para no perder campos ricos
- `wrestling-pipeline/etl/transform.py`
  - `clean_wrestlers()` ya no reduce la entidad a solo `name`, `height_cm`, `weight_kg`, `nationality`, `description`, `debut_year`
  - ahora preserva `real_name`, `birth_date`, `date_born`, `height`, `weight`, `image_url`, `image_large`, `promotion`, `team`, `source` y columnas auxiliares necesarias para el dashboard
- `wrestling-pipeline/etl/extract_thesportsdb.py`
  - se añadió selección estricta del mejor luchador por búsqueda
  - se eliminó el comportamiento que aceptaba candidatos incorrectos como `Benedikt Rocker`, `John Stones`, `Kevin Theophile-Catherine` o `André André`
  - el extractor ahora reutiliza el caché local del repositorio antes de salir a red
  - si el caché por clave quedó contaminado con un match malo, ahora se invalida al no superar la validación estricta
  - se corrigió el crash del logger cuando TheSportsDB respondía `429` o fallaba la conexión
- `wrestling-pipeline/api/main.py`
  - la API ahora combina varias fuentes de catálogo de luchadores y vuelve a deduplicar por `name_slug`
  - esto la hace más robusta si `wrestlers.csv` quedó incompleto pero existe un `wrestlers_thesportsdb.csv` más rico
- `wrestling-pipeline/dashboards/role_views.py`
  - la selección por defecto prioriza perfiles con imagen y datos visibles antes que placeholders vacíos
  - la vista fanática usa también `image_path` como fallback visual

### Validación ejecutada

- Tests locales ejecutados:
  - `wrestling-pipeline/tests/test_api.py`
  - `wrestling-pipeline/tests/test_etl.py`
  - `wrestling-pipeline/tests/test_extract_thesportsdb.py`
- Stack levantado con Docker mediante `wrestling-pipeline/scripts/run_local.sh`
- ETL reejecutado dentro de Docker con el contenedor `etl-runner`
- Verificaciones reales:
  - `http://localhost:8000/health`
  - `http://localhost:8000/wrestlers`
  - `http://localhost:8000/titles`
  - `http://localhost:8501/`

### Estado final comprobado

- `/wrestlers` ya no devuelve catálogo vacío ni perfiles obviamente incorrectos.
- El dashboard tiene de nuevo fichas con imagen para luchadores como `The Undertaker`, `Triple H`, `John Cena`, `Roman Reigns`, `Seth Rollins`, `Cody Rhodes`, `Hulk Hogan` y otros.
- `/titles` entrega 12 reinados enriquecidos y varios campeones históricos quedaron enlazados correctamente a imagen y fecha de nacimiento cuando TheSportsDB tenía ficha.
- Los perfiles que no existen en TheSportsDB siguen entrando como entidad mínima desde la cronología de títulos.
  - Ejemplo: `The Iron Sheik` y `Andre the Giant` aparecen con `title_history`, aunque sin foto si la fuente rica no respondió o no existe en caché.
- `analytics` ya no llega como `{}`.
  - Cuando falta el dataset de combates, la API devuelve una estructura completa con `data_available=false` y una razón explícita.

### Límite que sigue vigente

- Las métricas del perfil `Desarrollador / Analista` siguen en `N/D` mientras no exista un dataset real de combates en `wrestling-pipeline/data/raw/matches.csv` o `wrestling-pipeline/data/raw/wwe_matches.sqlite`.
- Eso ya no es un bug del dashboard ni del join: es ausencia del insumo Kaggle para calcular `wins`, `losses`, `win_rate` y `most_common_match_type`.

### Mejora aplicada al perfil Periodista

- `wrestling-pipeline/api/main.py`
  - `title_history` ahora incluye más contexto histórico por reinado:
    - `title_slug`
    - `event_date`
    - `location`
    - `days_recognized`
    - `era`
    - `notes`
    - `overall_reign`
    - `champion_reign_number`
    - `previous_champion`
    - `next_champion`
    - `defeated_for_title`
    - `lost_title_to`
    - `title_lineage_position`
  - si `end_date` no venía en la fuente, la API la infiere con el inicio del siguiente reinado del mismo campeonato
- `wrestling-pipeline/dashboards/role_views.py`
  - la vista `Periodista` ahora muestra:
    - total de días reconocidos
    - eras cubiertas
    - cards por reinado con evento, lugar, rival previo, sucesor y notas
    - tabla cronológica ampliada con columnas históricas reales
- `wrestling-pipeline/api/tests/test_api.py`
  - se añadieron assertions para verificar que `/titles` y `title_history` exponen el enriquecimiento adicional

### Integración aplicada a Wikipedia

- `wrestling-pipeline/etl/extractors/wikipedia.py`
  - se agregó `enrich_wrestlers_from_titles()` para construir perfiles desde:
    - resumen de Wikipedia
    - scraping del infobox de la página
  - esto permite poblar `extract`, `real_name`, `birth_date`, `height`, `weight` y `debut`
- `wrestling-pipeline/etl/extract_wikipedia.py`
  - se exportó el nuevo helper al nivel del ETL principal
- `wrestling-pipeline/etl/run_etl.py`
  - el pipeline ahora intenta generar `wrestlers_enriched.csv` automáticamente a partir de los nombres reales del catálogo y de los campeones
  - el comportamiento puede desactivarse con `ENABLE_WIKIPEDIA_ENRICHMENT=0`
- `wrestling-pipeline/tests/test_extractors.py`
  - se agregó un test para asegurar que el enriquecimiento de Wikipedia mezcla correctamente resumen + infobox

### Ajuste adicional de perfiles fanáticos

- `wrestling-pipeline/etl/extractors/wikipedia.py`
  - el parser del infobox ahora busca variantes reales de Wikipedia como `billed height`, `billed weight` y claves equivalentes
  - `birth_date` deja de persistirse como bloque textual completo y se reduce a una fecha usable cuando el infobox trae el valor mezclado con nombre y lugar
  - se limpian notas de referencia como `[1]` en altura y peso antes de guardar el CSV enriquecido
- `wrestling-pipeline/dashboards/role_views.py`
  - se quitó `Nombre real` del perfil `Fanático`
  - la tarjeta analítica ya no muestra un subtítulo vacío entre paréntesis cuando `real_name` no existe
- `wrestling-pipeline/tests/test_extractors.py`
  - se agregó cobertura para aliases del infobox de Wikipedia y limpieza de medidas

### Rediseño UI del perfil Periodista

- `wrestling-pipeline/dashboards/role_views.py`
  - la vista `Periodista` dejó de ser una columna larga y pasó a un layout editorial con:
    - hero contextual del luchador
    - fila KPI
    - tabs `Resumen`, `Cronología`, `Campeonatos` y `Datos`
    - timeline visual de reinados
    - tarjetas narrativas por cambio de manos
    - comparativas por campeonato y por era
  - el contenido tabular quedó relegado a la pestaña `Datos` para que la lectura principal no se sienta como un dump
  - se añadieron estilos específicos para badges, cards editoriales y tabs del perfil periodista

### Nueva vista analítica agregada

- `wrestling-pipeline/dashboards/role_views.py`
  - `Desarrollador / Analista` se convirtió en un laboratorio visual del roster completo
  - ahora incluye:
    - filtros por campeonato, era y rango de años
    - histogramas de altura y peso
    - scatter `altura vs peso`
    - boxplots por era o campeonato dominante
    - comparativas de altura, peso y duración media de reinados
    - tendencias de campeones por década
    - perfil individual con freak facts contra el promedio del grupo filtrado
  - se agregaron parsers locales de `height` y `weight` para convertir medidas textuales a `cm` y `kg` sin tocar API ni ETL

### Refactor visual de la UI analítica

- `wrestling-pipeline/dashboards/home.py`
  - se refinó la paleta general sobre el fondo beige
  - el selector de perfil ahora se renderiza visualmente como un control segmentado horizontal mediante CSS
  - se mejoró la jerarquía visual de inputs, charts y expander con superficies blancas, bordes suaves y sombras ligeras
- `wrestling-pipeline/dashboards/role_views.py`
  - `Perfil Desarrollador / Analista` ahora usa título H1 real
  - las métricas Kaggle dejaron de mostrarse como texto suelto y pasaron a cuatro tarjetas uniformes con iconografía integrada
  - cuando no hay dato, las tarjetas muestran `--` y el subtítulo `(Dato no disponible)` en vez de `N/D`
  - la visualización de títulos visibles ahora usa una paleta coherente y una leyenda más legible
  - se eliminó la tarjeta analítica pequeña del payload y fue reemplazada por una ficha unificada del luchador, inspirada en la vista fanática
  - el HTML crudo del payload quedó encapsulado dentro de `st.expander("Ver Payload HTML Crudo")`

### Ajustes de accesibilidad y consistencia visual

- `wrestling-pipeline/dashboards/home.py`
  - el perfil activo del selector horizontal ahora fuerza texto blanco puro sobre el fondo borgoña
  - la fila de estado `API / Admin / Datos enriquecidos` dejó de usar métricas flotantes y pasó a pequeñas tarjetas blancas con indicador visual de estado
  - se redujo el espacio vertical entre buscador y selector de perfil para que funcionen como un panel superior más compacto
- `wrestling-pipeline/dashboards/role_views.py`
  - la vista `Fanático` dejó de quedar plana sobre el fondo beige y ahora reutiliza la ficha unificada del luchador dentro de una tarjeta blanca consistente con el resto del dashboard
  - la imagen del luchador dentro de la ficha unificada dejó de renderizarse recortada; ahora se muestra completa con `object-fit: contain`

## 2026-06-23

### Diagnóstico inicial

- `wrestling-pipeline/etl/extract_thesportsdb.py` tiene funciones útiles anidadas accidentalmente dentro de `_cache_get`, por lo que varios imports esperados por los tests no existen a nivel módulo.
- `wrestling-pipeline/etl/extract_wikipedia.py` ejecuta requests y scraping en tiempo de importación. Eso vuelve frágil el ETL, rompe entornos sin red y contamina cualquier test que solo quiera importar funciones.
- `wrestling-pipeline/etl/run_etl.py` rellena `titles_extracted.csv` con títulos ficticios cuando faltan datos reales. Eso oculta el problema de negocio y hace que `/titles` no represente reinados enriquecidos.
- `wrestling-pipeline/api/main.py` concatena CSVs pero no cruza entidades por una clave común. Resultado: `/wrestlers` y `/titles` exponen datos parciales o vacíos según la fuente.
- Las vistas `Periodista` y `Desarrollador` en Streamlit hoy usan datos estáticos en vez de la capa de datos real, así que no reflejan el estado del pipeline.

### Propuesta de unificación de nombres

- Introducir una clave canónica compartida para cada luchador: `name_slug`.
- Regla base de `name_slug`: minúsculas, trim, colapso de espacios, remoción de acentos y signos, y normalización a tokens ASCII.
- Persistir `name_slug` en todas las salidas relevantes:
  - `wrestlers`: desde `name`
  - `titles/reigns`: desde `champion_name` o `holder`
  - `matches`: desde `winner` y `loser`
- Mantener además `canonical_name` para la etiqueta visible y `alias_source_name` para auditoría cuando una fuente use otra variante.
- Usar coincidencia exacta por `name_slug` como unión primaria.
- Aplicar fuzzy matching solo como respaldo controlado al consolidar catálogos de luchadores, nunca dentro del endpoint en tiempo de consulta.

### Alcance de la siguiente iteración

- Reparar extractores y normalización para producir datos consistentes y testeables.
- Reemplazar los títulos ficticios por reinados reales cuando existan archivos fuente.
- Exponer `/wrestlers` enriquecido con perfil fanático y `/titles` enriquecido con cronología para periodista.
- Rehacer las vistas de Streamlit para que cada rol consuma la misma entidad unificada.

### Cambios aplicados

- Se creó `wrestling-pipeline/etl/name_utils.py` para centralizar limpieza estricta y `slug` de nombres.
- `extract_kaggle.py` ahora normaliza `winner` y `loser` a `winner_slug` y `loser_slug`.
- `extract_wikipedia.py` se reescribió para eliminar requests en tiempo de importación y producir salidas normalizables sin efectos laterales.
- `extract_thesportsdb.py` se reestructuró por completo:
  - se corrigió el problema de funciones anidadas dentro de `_cache_get`
  - se dejaron exports utilizables por los tests
  - se desactiva el caché persistente automáticamente durante `pytest` para evitar contaminación entre tests
- `normalize.py` ahora construye `wrestlers.csv`, `matches.csv` y `titles.csv` usando `name_slug` como clave primaria de conciliación.
- `run_etl.py` dejó de rellenar títulos ficticios cuando existe `data/raw/wwe_champions_initial.csv` y normaliza reinados reales hacia `titles.csv`.
- `api/main.py` ahora:
  - resuelve rutas de datos locales o en contenedor sin hardcode exclusivo a `/app`
  - enriquece `/wrestlers` con `title_history`, `titles_won` y `analytics`
  - enriquece `/titles` con datos del luchador asociado
  - soporta cruces aun cuando falten luchadores base y solo existan apariciones en títulos o matches
- `dashboards/home.py` y las páginas por rol se rehacieron para consumir la entidad unificada:
  - `Fanático`: imagen, nombre artístico, nombre real, biografía, peso, altura y nacimiento
  - `Periodista`: cronología de reinados y eventos
  - `Desarrollador / Analista`: KPIs y gráficos desde `analytics`, con acceso condicionado a la clave de administrador

### Ajustes para ejecutar tests en Python 3.12

- `wrestling-pipeline/etl/requirements.txt`
  - `psycopg2-binary` actualizado a `2.9.10`
  - `pyarrow` actualizado a `17.0.0`
- `wrestling-pipeline/api/requirements.txt`
  - stack actualizado a `fastapi 0.115.12`, `uvicorn 0.30.6`, `httpx 0.27.2`
- Los tests API del repositorio dejaron de depender de `TestClient`, porque en este entorno ASGI quedaba bloqueado incluso con apps mínimas. Ahora validan directamente los handlers y el contrato JSON esperado.

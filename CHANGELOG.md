# CHANGELOG

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

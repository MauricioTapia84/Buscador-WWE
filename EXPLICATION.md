# EXPLICATION

## 1. Qué hace este proyecto

El proyecto arma una entidad única de luchador WWE a partir de varias fuentes:

- `TheSportsDB`: ficha visual y metadatos del luchador
- `Wikipedia`: cronología y enriquecimiento histórico
- `Kaggle / SQLite / CSV de combates`: resultados de luchas para analytics

El objetivo no es mostrar tres tablas separadas.

El objetivo es construir una sola identidad por luchador para que:

- la foto pertenezca al mismo luchador,
- los títulos pertenezcan al mismo luchador,
- los combates pertenezcan al mismo luchador.

Eso es exactamente el cruce entre fuentes.

---

## 2. Cómo se extrae cada fuente

### TheSportsDB

Archivo principal:

- [wrestling-pipeline/etl/extract_thesportsdb.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_thesportsdb.py)

Qué hace:

1. Busca luchadores por nombre.
2. Recupera la ficha del mejor candidato.
3. Guarda campos como:
   - `name`
   - `real_name`
   - `date_born`
   - `nationality`
   - `image_url`
   - `image_large`
   - `description`
   - `team`
   - `promotion`

Punto importante:

Antes el extractor aceptaba resultados flojos y eso produjo perfiles incorrectos como:

- `Benedikt Rocker`
- `John Stones`
- `Kevin Theophile-Catherine`
- `André André`

Ahora el extractor hace dos cosas:

1. toma solo el mejor candidato,
2. exige coincidencia fuerte de nombre antes de aceptarlo.

Si no hay un match confiable, no inventa el perfil.

---

### Wikipedia

Archivo principal:

- [wrestling-pipeline/etl/extract_wikipedia.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_wikipedia.py)

Qué hace:

1. Puede leer páginas o URLs de Wikipedia.
2. Extrae extractos y campos de infobox.
3. Puede producir:
   - `extract`
   - `real_name`
   - `birth_date`
   - `height`
   - `weight`
   - `debut`

En este proyecto también se usa para cronología histórica de campeonatos y eventos.

---

### Kaggle / combates

Archivo principal:

- [wrestling-pipeline/etl/extract_kaggle.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_kaggle.py)

Qué hace:

1. Busca `matches.csv` o `wwe_matches.sqlite`.
2. Normaliza columnas distintas a una forma común.
3. Produce columnas como:
   - `winner`
   - `loser`
   - `match_type`
   - `event_name`
   - `event_date`

Ese dataset es el que alimenta el perfil `Desarrollador / Analista`.

Si ese archivo no existe, el dashboard no puede calcular:

- total de luchas,
- victorias,
- derrotas,
- win-rate,
- estipulación más común.

Por eso ahora la API responde con:

- `data_available = false`
- `reason = "...no se encontró un dataset de combates..."`

en vez de devolver `analytics: {}` vacío.

---

## 3. Cómo se limpian los nombres

Archivo principal:

- [wrestling-pipeline/etl/name_utils.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/name_utils.py)

La regla central del sistema es:

```text
no unir por nombre crudo;
unir por nombre normalizado
```

Ejemplo conceptual:

- `" Triple H "` -> `triple h`
- `"André the Giant"` -> `andre the giant`
- `"The Iron  Sheik"` -> `the iron sheik`

El proceso hace:

1. `strip()` de espacios,
2. colapso de espacios dobles,
3. minúsculas,
4. remoción de acentos,
5. remoción de signos extra,
6. generación de una clave compartida: `name_slug`

Eso permite unir aunque las fuentes no escriban el nombre exactamente igual.

---

## 4. Cómo se hace el cruce entre fuentes

Archivo principal:

- [wrestling-pipeline/etl/normalize.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/normalize.py)

La lógica real de join es esta:

### Paso 1. Se normalizan los catálogos de luchadores

Se mezclan varias salidas:

- `wrestlers_thesportsdb.csv`
- `wrestlers_enriched.csv`
- `wrestlers_extracted.csv`

Todas pasan por:

- limpieza del nombre visible,
- generación de `name_slug`,
- deduplicación por identidad.

---

### Paso 2. Se normalizan los títulos

Se unifican columnas históricas como:

- `holder`
- `champion_name`
- `won_date`
- `start_date`
- `event_name`

También se genera:

- `holder_slug`

Entonces un reinado de `Bob Backlund` puede unirse al mismo `Bob Backlund` de TheSportsDB.

---

### Paso 3. Se normalizan los combates

Se convierten variantes como:

- `Winner` -> `winner`
- `Loser` -> `loser`
- `MatchType` -> `match_type`

Y luego:

- `winner_slug`
- `loser_slug`

Eso permite sumar wins y losses por la misma identidad normalizada.

---

### Paso 4. La API arma la entidad final

Archivo principal:

- [wrestling-pipeline/api/main.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/api/main.py)

La API carga:

- luchadores normalizados,
- títulos normalizados,
- combates normalizados.

Luego hace el cruce así:

1. `name_slug` del luchador
2. `holder_slug` del título
3. `winner_slug` y `loser_slug` del combate

Con esa unión construye un payload único por luchador con:

- perfil base,
- `title_history`,
- `titles_won`,
- `analytics`

Eso es lo que consume Streamlit.

---

## 5. Por qué el dashboard estaba vacío o roto

Hubo varios problemas distintos:

### Problema A. Streamlit apuntaba mal a la API

Dentro de Docker, `localhost` no era la API sino el mismo contenedor.

La URL correcta interna es:

```text
http://api:8000
```

Eso ya quedó corregido.

---

### Problema B. El ETL perdía columnas útiles

Antes `clean_wrestlers()` reducía la tabla a campos mínimos y descartaba:

- `image_url`
- `real_name`
- `birth_date`
- `date_born`
- `height`
- `weight`
- `promotion`
- `team`

Resultado:

- la API recibía luchadores casi vacíos,
- el dashboard no tenía foto,
- no había biografía ni fecha visible.

Ahora esos campos se preservan.

---

### Problema C. TheSportsDB devolvía matches incorrectos

Antes se aceptaban candidatos demasiado laxos.

Eso contaminó el catálogo y provocó cruces absurdos.

Ahora:

- se valida el nombre,
- se usa caché local del repo,
- se invalida caché viejo incorrecto,
- si no hay match confiable, se descarta.

---

### Problema D. Faltaba el dataset de combates

El perfil analítico depende de:

- `data/raw/matches.csv`
- o `data/raw/wwe_matches.sqlite`

Si ese archivo no existe, no hay forma legítima de calcular analytics.

Eso no se corrige inventando valores.

Se corrige:

1. detectando la ausencia,
2. devolviendo `data_available = false`,
3. mostrando `N/D` en el dashboard.

---

## 6. Cómo se alimenta cada perfil del dashboard

### Fanático

Usa principalmente:

- `image_url`
- `artist_name`
- `real_name`
- `biography`
- `weight`
- `height`
- `birth_date`

Si no existe imagen, muestra un placeholder visual.

---

### Periodista

Usa:

- `title_history`
- `start_date`
- `end_date`
- `event_name`
- `won_date`
- `reign_days`

Es una vista de cronología.

---

### Desarrollador / Analista

Usa:

- `analytics.total_matches`
- `analytics.wins`
- `analytics.losses`
- `analytics.win_rate`
- `analytics.most_common_match_type`

Esta vista solo se habilita al ingresar la clave de administrador.

Si falta el dataset de combates, la vista queda explícitamente en `N/D`.

---

## 7. Qué quedó validado en esta iteración

Se comprobó realmente:

- `http://localhost:8000/health`
- `http://localhost:8000/wrestlers`
- `http://localhost:8000/titles`
- `http://localhost:8501/`

Resultado validado:

- la API está levantando,
- `/titles` devuelve 12 reinados enriquecidos,
- `/wrestlers` ya no devuelve catálogo vacío,
- el dashboard vuelve a tener luchadores con imagen,
- ejemplos confirmados con imagen:
  - `The Undertaker`
  - `Triple H`
  - `John Cena`
  - `Roman Reigns`
  - `Seth Rollins`
  - `Cody Rhodes`
  - `Hulk Hogan`
  - `Bob Backlund`

También se comprobó que algunos campeones históricos siguen entrando aunque no exista ficha rica:

- `The Iron Sheik`
- `Andre the Giant`

En esos casos:

- sí aparece la cronología de reinados,
- pero pueden faltar foto y biografía si la fuente rica no respondió o no existe en caché.

---

## 8. Resumen corto del flujo completo

El flujo real del sistema es:

1. extraer datos crudos,
2. limpiar nombres,
3. generar `slug` compartido,
4. normalizar luchadores, títulos y combates,
5. unir todo en la API,
6. consumir la entidad unificada desde Streamlit.

La identidad técnica del luchador no es el nombre “bonito”.

La identidad técnica es la clave limpia:

```text
name_slug
```

Ese es el corazón del cruce entre fuentes.

---

## 9. Archivos clave

- [wrestling-pipeline/etl/name_utils.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/name_utils.py)
- [wrestling-pipeline/etl/extract_kaggle.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_kaggle.py)
- [wrestling-pipeline/etl/extract_thesportsdb.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_thesportsdb.py)
- [wrestling-pipeline/etl/extract_wikipedia.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_wikipedia.py)
- [wrestling-pipeline/etl/normalize.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/normalize.py)
- [wrestling-pipeline/etl/run_etl.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/run_etl.py)
- [wrestling-pipeline/api/main.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/api/main.py)
- [wrestling-pipeline/dashboards/home.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/dashboards/home.py)
- [wrestling-pipeline/dashboards/role_views.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/dashboards/role_views.py)

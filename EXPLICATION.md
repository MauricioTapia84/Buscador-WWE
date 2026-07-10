# EXPLICATION

## 1. Objetivo real del cruce

El proyecto no trabaja con tres listas separadas.

Construye una sola entidad por luchador para que:

- la foto pertenezca al luchador correcto,
- los reinados pertenezcan a ese mismo luchador,
- los combates pertenezcan a ese mismo luchador.

Eso es el cruce entre fuentes.

La regla principal es:

```text
no unir por nombre crudo;
unir por nombre normalizado
```

---

## 2. De dónde sale cada dato

### TheSportsDB

Archivo clave:

- [wrestling-pipeline/etl/extract_thesportsdb.py](wrestling-pipeline/etl/extract_thesportsdb.py)

Se usa para traer perfil visual del luchador:

- `name`
- `real_name`
- `date_born`
- `nationality`
- `image_url`
- `image_large`
- `description`
- `team`
- `promotion`

Antes aceptaba resultados demasiado flojos y eso generaba perfiles incorrectos.

Ahora:

1. elige solo el mejor candidato,
2. exige coincidencia fuerte de nombre,
3. usa caché local cuando existe,
4. descarta un match si no es confiable.

La API exacta usada ahí es:

```text
https://www.thesportsdb.com/api/v1/json/{API_KEY}/searchplayers.php?p={nombre}
```

---

### Wikipedia

Archivos clave:

- [wrestling-pipeline/etl/extract_wikipedia.py](wrestling-pipeline/etl/extract_wikipedia.py)
- [wrestling-pipeline/etl/extractors/wikipedia.py](wrestling-pipeline/etl/extractors/wikipedia.py)

Se usa para:

- extractos y biografía,
- datos de infobox,
- cronología histórica,
- páginas de eventos y campeonatos.

Puede aportar:

- `extract`
- `real_name`
- `birth_date`
- `height`
- `weight`
- `debut`

Los endpoints exactos usados en Wikipedia son:

```text
https://en.wikipedia.org/api/rest_v1/page/summary/{title}
https://en.wikipedia.org/api/rest_v1/page/html/{page_title}
```

El primero trae el resumen.

El segundo permite scrapear el HTML para leer la infobox.

Importante:

- Wikipedia no entrega estos datos ya listos para todos los luchadores.
- En muchos perfiles de wrestling la infobox usa claves como `Billed height` y `Billed weight`, no solo `Height` y `Weight`.
- Por eso el extractor ahora no busca una sola clave exacta; busca aliases y luego limpia referencias como `[1]`.

---

### Kaggle / combates

Archivo clave:

- [wrestling-pipeline/etl/extract_kaggle.py](wrestling-pipeline/etl/extract_kaggle.py)

Se usa para el perfil `Desarrollador / Analista`.

Normaliza columnas como:

- `winner`
- `loser`
- `match_type`
- `event_name`
- `event_date`

Si no existe `matches.csv` o `wwe_matches.sqlite`, no hay forma legítima de calcular:

- luchas registradas,
- victorias,
- derrotas,
- win-rate,
- estipulación más común.

Por eso la API devuelve una estructura completa con:

- `data_available = false`
- `reason = "...no se encontró un dataset de combates..."`

en vez de mandar `analytics: {}`.

---

## 3. Cómo se normalizan los nombres

Archivo clave:

- [wrestling-pipeline/etl/name_utils.py](wrestling-pipeline/etl/name_utils.py)

Cada nombre pasa por limpieza estricta:

1. trim de espacios,
2. colapso de espacios dobles,
3. minúsculas,
4. remoción de acentos,
5. remoción de signos,
6. generación de una clave común: `name_slug`

Ejemplos:

- `" Triple H "` -> `triple h`
- `"André the Giant"` -> `andre the giant`
- `"The Iron  Sheik"` -> `the iron sheik`

Esa clave es la identidad técnica del luchador.

---

## 4. Cómo se hace el cruce entre fuentes

Archivo clave:

- [wrestling-pipeline/api/main.py](wrestling-pipeline/api/main.py)

La API une los datos usando estas claves:

- `name_slug` para luchadores,
- `holder_slug` para reinados,
- `winner_slug` y `loser_slug` para combates.

Con eso arma una sola entidad por luchador con:

- perfil base,
- `title_history`,
- `titles_won`,
- `analytics`.

---

## 5. Qué fallaba antes

### Problema A. El dashboard no apuntaba bien a la API

Dentro de Docker, `localhost` no era la API.

La URL correcta interna es:

```text
http://api:8000
```

---

### Problema B. El ETL tiraba columnas útiles

Antes `clean_wrestlers()` descartaba:

- `image_url`
- `real_name`
- `birth_date`
- `date_born`
- `height`
- `weight`
- `promotion`
- `team`

Entonces la API recibía perfiles casi vacíos.

Ahora esos campos se preservan.

---

### Problema C. TheSportsDB contaminaba el catálogo

Antes aceptaba resultados erróneos y aparecían perfiles como:

- `Benedikt Rocker`
- `John Stones`
- `Kevin Theophile-Catherine`
- `André André`

Ahora el extractor valida el match antes de aceptarlo.

---

### Problema D. El periodista recibía una cronología demasiado pobre

Antes `title_history` llevaba solo algo parecido a:

- `title`
- `start_date`
- `end_date`
- `event_name`
- `won_date`
- `reign_days`

Eso servía poco para una lectura periodística.

### Problema E. Wikipedia sí existía, pero no alimentaba el flujo principal

El código de Wikipedia estaba implementado, pero `run_etl.py` no generaba
`wrestlers_enriched.csv` de forma automática para el dashboard.

En la práctica:

- TheSportsDB sí estaba entrando,
- Wikipedia casi no,
- por eso muchos perfiles mostraban:
  - fecha de nacimiento sí,
  - nombre real no,
  - altura no,
  - peso no,
  - biografía no.

Además había un detalle fino:

- la biografía venía del endpoint `summary`, por eso empezó a aparecer antes;
- pero altura y peso dependen del scraping del infobox;
- si el parser no reconoce `billed height` o `billed weight`, esos campos quedan vacíos aunque la página sí los tenga.

---

## 6. Qué se agregó para el perfil Periodista

Ahora la API enriquece cada reinado con más contexto histórico cuando el dato existe.

Campos nuevos o mejor aprovechados:

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
- `end_date_inferred`

Además:

1. la API ordena los reinados por campeonato y fecha,
2. detecta el campeón previo,
3. detecta el campeón siguiente,
4. si `end_date` no existe, la infiere usando el inicio del siguiente reinado del mismo título.

Ejemplo real:

```json
{
  "title": "WWE Championship",
  "start_date": "1978-02-20",
  "end_date": "1983-12-26",
  "end_date_inferred": true,
  "event_name": "WWF on MSG Network",
  "location": "New York, NY",
  "days_recognized": 2135,
  "era": "WWWF/WWF",
  "previous_champion": "\"Superstar\" Billy Graham",
  "next_champion": "The Iron Sheik",
  "defeated_for_title": "\"Superstar\" Billy Graham",
  "lost_title_to": "The Iron Sheik"
}
```

Eso ya permite responder preguntas como:

- cuándo empezó y terminó un reinado,
- dónde ocurrió el cambio,
- a quién destronó,
- quién lo reemplazó,
- en qué era histórica ocurrió.

Además, el ETL ahora intenta enriquecer el catálogo de luchadores desde
Wikipedia automáticamente, para que la vista fanática y la periodista no
dependan solo de TheSportsDB.

---

## 7. Cómo se alimenta cada perfil del dashboard

### Fanático

Usa principalmente:

- `image_url`
- `artist_name`
- `real_name`
- `biography`
- `weight`
- `height`
- `birth_date`

---

### Periodista

Usa:

- `title_history`
- `start_date`
- `end_date`
- `event_name`
- `location`
- `reign_days`
- `days_recognized`
- `era`
- `notes`
- `previous_champion`
- `next_champion`

Es una vista de cronología, contexto histórico y cambios de manos.

---

### Desarrollador / Analista

Usa:

- `analytics.total_matches`
- `analytics.wins`
- `analytics.losses`
- `analytics.win_rate`
- `analytics.most_common_match_type`

Si falta el dataset de combates, la vista muestra `N/D`.

---

## 8. Qué quedó validado

Se validó realmente:

- `http://localhost:8000/health`
- `http://localhost:8000/wrestlers`
- `http://localhost:8000/titles`
- `http://localhost:8501/`

También se verificó localmente que el handler del API ya produce `title_history` enriquecido con:

- `end_date`
- `location`
- `days_recognized`
- `era`
- `previous_champion`
- `next_champion`

Ejemplos con ficha rica confirmada:

- `The Undertaker`
- `Triple H`
- `John Cena`
- `Roman Reigns`
- `Seth Rollins`
- `Cody Rhodes`
- `Hulk Hogan`
- `Bob Backlund`

Y campeones históricos que igual entran por cronología aunque no tengan ficha rica completa:

- `The Iron Sheik`
- `Andre the Giant`

---

## 9. Resumen corto del flujo

El flujo final es:

1. extraer datos crudos,
2. limpiar nombres,
3. generar `slug`,
4. normalizar luchadores, títulos y combates,
5. unir todo en la API,
6. consumir la entidad unificada desde Streamlit.

La clave del sistema es:

```text
name_slug
```

No el texto original del nombre.

---

## 10. Archivos clave

- [wrestling-pipeline/etl/name_utils.py](wrestling-pipeline/etl/name_utils.py)
- [wrestling-pipeline/etl/extract_kaggle.py](wrestling-pipeline/etl/extract_kaggle.py)
- [wrestling-pipeline/etl/extract_thesportsdb.py](wrestling-pipeline/etl/extract_thesportsdb.py)
- [wrestling-pipeline/etl/extract_wikipedia.py](wrestling-pipeline/etl/extract_wikipedia.py)
- [wrestling-pipeline/etl/extractors/wikipedia.py](wrestling-pipeline/etl/extractors/wikipedia.py)
- [wrestling-pipeline/api/main.py](wrestling-pipeline/api/main.py)
- [wrestling-pipeline/dashboards/role_views.py](wrestling-pipeline/dashboards/role_views.py)

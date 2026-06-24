# Investigacion Wikipedia API para Rol C

## Objetivo

Definir la mejor forma de extraer la tabla de campeones de `List of WWE Champions` sin scraping invasivo y con una ruta sostenible para el ETL.

## Hallazgos

### 1. La opcion mas segura hoy es la MediaWiki Action API

El endpoint base oficial para Wikipedia en ingles es:

```text
https://en.wikipedia.org/w/api.php
```

La documentacion oficial de MediaWiki indica que la Action API es el punto de entrada general para operaciones de lectura, busqueda y parseo de paginas. Para este proyecto sirve porque permite pedir una pagina por titulo y devolver HTML ya parseado o el wikitexto fuente.

Consulta sugerida para obtener HTML parseado:

```text
https://en.wikipedia.org/w/api.php?action=parse&page=List_of_WWE_Champions&prop=text&format=json
```

Consulta sugerida para obtener wikitexto original:

```text
https://en.wikipedia.org/w/api.php?action=parse&page=List_of_WWE_Champions&prop=wikitext&format=json
```

### 2. El endpoint REST `page/html` del acta debe quedar como alternativa legacy

El acta apunta a:

```text
https://en.wikipedia.org/api/rest_v1/page/html/List_of_WWE_Champions
```

Ese camino historicamente ha servido para recuperar HTML de la pagina, pero la documentacion actual del portal Core REST API aparece marcada como deprecada. Por eso conviene dejar la estrategia principal sobre `w/api.php?action=parse` y usar `page/html` solo como compatibilidad o referencia historica.

### 3. Recomendaciones oficiales de consumo

Para evitar problemas con Wikimedia, la documentacion tecnica recomienda:

- usar `User-Agent` descriptivo
- hacer solicitudes en serie y no en paralelo
- preferir `GET` para lectura
- usar `maxlag` en tareas no interactivas
- cachear respuestas cuando sea posible

## Estrategia recomendada para el ETL

### Semana 1

- Crear un CSV semilla manual con los primeros campeones.
- Documentar estructura esperada de columnas.

### Semana 2

- Implementar `extract_wikipedia.py` con `requests`.
- Consumir `action=parse` con `prop=text`.
- Procesar el HTML devuelto con `BeautifulSoup`.
- Ubicar la tabla `Reigns` y normalizar columnas clave.

### Semana 3

- Agregar validacion con Pydantic para fechas, dias y nombres.
- Comparar el resultado contra el CSV inicial para detectar cambios de estructura.
- Guardar una copia cruda del payload en `data/raw/` como respaldo para la demo.

## Columnas sugeridas para la primera version

- `overall_reign`
- `champion`
- `date_won`
- `event`
- `location`
- `champion_reign_number`
- `days_held`
- `days_recognized`
- `era`
- `notes`

## Riesgos detectados

- La pagina mezcla reinados reconocidos y no reconocidos.
- Algunas filas tienen notas multilinea.
- Hay cambios historicos de nombre del titulo que deben conservarse.
- La pagina puede cambiar su estructura HTML aunque el titulo siga siendo el mismo.

## Decision tecnica del rol C

Para este proyecto recomiendo:

1. usar `w/api.php?action=parse` como fuente principal
2. mantener el CSV inicial manual como control de regresion
3. dejar `page/html` solo como fallback documentado

## Referencias oficiales

- https://www.mediawiki.org/wiki/API:Main_page
- https://www.mediawiki.org/wiki/API:Parsing_wikitext
- https://www.mediawiki.org/wiki/Special:MyLanguage/API:Etiquette
- https://api.wikimedia.org/wiki/Core_REST_API/Reference/Pages


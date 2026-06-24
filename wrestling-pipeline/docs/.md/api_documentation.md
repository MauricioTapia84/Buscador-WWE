# Documentación de la API

## Base URL
- `http://localhost:8000`

## Endpoints

### `GET /wrestlers`
Devuelve una lista de luchadores.

Query params:
- `source` (opcional): `thesportsdb`, `wikipedia`, `all` o nombre de archivo CSV.

Ejemplos:
- `/wrestlers`
- `/wrestlers?source=all`
- `/wrestlers?source=thesportsdb`

Respuesta ejemplo:
```json
[
  {"id": 1, "name": "John Doe", "nationality": "USA"},
  {"id": 2, "name": "Jane Smith", "nationality": "Canada"}
]
```

### `GET /titles`
Devuelve una lista de títulos procesados.

Respuesta ejemplo:
```json
[
  {"id": 1, "title": "World Championship", "holder": "John Doe"}
]
```

### `GET /matches`
Devuelve la lista de combates normalizados.

Respuesta ejemplo:
```json
[
  {"id": 1, "winner": "John Doe", "loser": "Jane Smith", "date": "2025-01-01"}
]
```

### `GET /wrestlers/{wrestler_id}`
Devuelve el luchador con el `id` especificado.

- Retorna 404 si no existe.

### `GET /titles/{title_id}`
Devuelve el título con el `id` especificado.

- Retorna 404 si no existe.

### `GET /search`
Busca luchadores y títulos.

Query params:
- `q` (opcional): texto de búsqueda.

Ejemplo:
- `/search?q=rock`

### `GET /health`
Endpoint de salud que retorna:
```json
{"status": "ok"}
```

## Notas de implementación

- Los datos se leen desde CSVs en `/app/data/processed`.
- El endpoint `/search` combina resultados de luchadores y títulos.
- Los valores `NaN` o infinitos se limpian como `null`.

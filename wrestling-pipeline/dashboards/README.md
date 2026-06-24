# Dashboard Rol C

## Ejecutar en local

Desde `wrestling-pipeline/dashboards/`:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuracion de API

Por defecto el dashboard espera la API en:

```text
http://localhost:8000
```

Si trabajas con Docker o con otro host, configura:

```bash
API_URL=http://api:8000 streamlit run app.py
```

## Endpoints esperados

- `/health`
- `/wrestlers`
- `/titles`
- `/search?q=...`

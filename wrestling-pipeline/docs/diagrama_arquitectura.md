# Diagrama de Arquitectura

```mermaid
flowchart LR
    subgraph Sources[Fuentes de datos]
        A[TheSportsDB API]
        B[Wikipedia Action API]
        C[Kaggle SQLite]
        D[CSV inicial manual de campeones]
    end

    subgraph ETL[Pipeline ETL en Python]
        E1[extract_thesportsdb.py]
        E2[extract_wikipedia.py]
        E3[extract_kaggle.py]
        T[transform.py]
        V[validate.py con Pydantic]
        L[load.py]
    end

    subgraph Storage[Persistencia]
        DB[(wrestling.db)]
        RAW[(data/raw)]
        PROC[(data/processed)]
    end

    subgraph Serve[Exposicion]
        API[FastAPI]
    end

    subgraph UX[Dashboard Streamlit]
        APP[app.py]
        FAN[Vista Fanatico]
        PER[Vista Periodista]
        DEV[Vista Desarrollador]
    end

    A --> E1
    B --> E2
    C --> E3
    D --> E2

    E1 --> RAW
    E2 --> RAW
    E3 --> RAW

    E1 --> T
    E2 --> T
    E3 --> T
    T --> V
    V --> L
    L --> DB
    DB --> PROC
    DB --> API

    API --> APP
    APP --> FAN
    APP --> PER
    APP --> DEV
```

## Lectura del flujo

- `Rol A` alimenta el ETL y consolida datos en `wrestling.db`.
- `Rol B` expone la base mediante FastAPI y Docker.
- `Rol C` documenta, deja el CSV semilla, investiga Wikipedia y construye el dashboard que consume la API local.


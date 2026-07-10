# Análisis Final — Wrestling Pipeline / Buscador WWE

**Integrantes:**
- Tomás Zapata
- Gabriel Muñoz
- Mauricio Tapia

**Repositorio:** https://github.com/MauricioTapia84/Buscador-WWE

---

## 1. Descripción del Proyecto

Wrestling Pipeline es una solución integral de datos para lucha libre profesional (WWE). El proyecto extrae información de múltiples fuentes externas, la transforma en artefactos limpios y consistentes, y la expone mediante una API REST y un dashboard interactivo de Streamlit. Adicionalmente, incluye un modelo de Machine Learning que clasifica el perfil histórico de un luchador como "campeón" o "no campeón" basándose en estadísticas de combate.

### Objetivos del proyecto

1. Extraer datos de al menos tres fuentes externas diferentes (TheSportsDB, Wikipedia, Kaggle).
2. Normalizar, limpiar y validar la información para producir artefactos consistentes.
3. Exponer los datos mediante una API REST documentada con FastAPI.
4. Crear un dashboard Streamlit con análisis por perfil de audiencia (Fanático, Periodista, Desarrollador/Analista).
5. Entrenar un modelo de Machine Learning para clasificar el perfil histórico de un luchador.
6. Empaquetar todo con Docker y orquestarlo con Docker Compose.

---

## 2. Arquitectura General

### 2.1 Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend ETL | Python 3.12, Pandas, Pydantic |
| API REST | FastAPI, Uvicorn |
| Dashboard | Streamlit, Plotly |
| Modelo ML | Scikit-learn, XGBoost, joblib |
| Base de datos | SQLite (local), PostgreSQL (producción) |
| Infraestructura | Docker, Docker Compose |
| Fuentes de datos | TheSportsDB API, Wikipedia API, Kaggle SQLite |

### 2.2 Estructura del Proyecto

```
wrestling-pipeline/
├── etl/                    # Pipeline ETL: extractores y transformaciones
│   ├── extractors/
│   │   ├── thesportsdb.py  # Extractor API TheSportsDB
│   │   ├── wikipedia.py    # Extractor Wikipedia (scraping + API)
│   │   └── kaggle.py       # Extractor Kaggle SQLite
│   ├── transform/
│   │   └── normalize.py    # Normalización y name_slug
│   └── run_etl.py          # Orquestador del pipeline
├── api/
│   └── main.py             # API FastAPI
├── dashboards/
│   ├── home.py             # Aplicación Streamlit principal
│   └── role_views.py       # Vistas por perfil de usuario
├── models/
│   ├── 01_eda.ipynb        # Notebook EDA
│   ├── train.py            # Entrenamiento y selección de modelos
│   ├── preprocess.py       # Preprocesamiento (pipelines sklearn)
│   ├── split_data.py       # División del dataset
│   ├── evaluate.py         # Métricas de evaluación
│   ├── champion_predictor.pkl   # Modelo entrenado exportado
│   └── evaluation_report.json  # Métricas del modelo
├── data/
│   ├── raw/                # Datos crudos de fuentes externas
│   └── processed/          # Artefactos limpios y listos
└── tests/                  # Pruebas unitarias e integración
```

### 2.3 Flujo de Datos

```
TheSportsDB API ──┐
Wikipedia API   ──┤──► ETL (extracción + normalización) ──► data/processed/ ──► API + Dashboard
Kaggle SQLite   ──┘                                                         └──► Modelo ML
```

---

## 3. Pipeline ETL — Proceso Realizado

### 3.1 Extracción de Datos

Se implementaron tres extractores independientes:

| Extractor | Fuente | Formato | Descripción |
|-----------|--------|---------|-------------|
| `thesportsdb.py` | TheSportsDB API | JSON | Perfil biográfico, imagen, peso, altura, fecha de nacimiento |
| `wikipedia.py` | Wikipedia API + scraping | HTML/JSON | Infobox con datos demográficos, extracto biográfico |
| `kaggle.py` | Kaggle SQLite | SQLite | Historial completo de combates: ganadores, perdedores, tipo de match, resultado |

**Estrategia de caché:** Los extractores priorizan datos locales en `data/raw/` para evitar llamadas repetitivas. Si los datos no existen localmente, se consultan las fuentes y se almacenan en caché.

**TheSportsDB:** Se implementó selección estricta del mejor candidato por búsqueda con invalidación de caché cuando el candidato no supera la validación, evitando mapeos erróneos como `Benedikt Rocker` o `John Stones`.

**Wikipedia:** Se agregó `enrich_wrestlers_from_titles()` para construir perfiles desde resumen y scraping del infobox. Se controlaron aliases para nombres ambiguos (`The Rock`, `Batista`, `Edge`, `Daniel Bryan`, etc.) y se rechazaron resúmenes de páginas de desambiguación.

### 3.2 Normalización y Limpieza

#### Clave canónica `name_slug`

Se introdujo una clave canónica compartida para cruzar entidades entre fuentes:
- Regla: minúsculas, trim, colapso de espacios, remoción de acentos y signos, normalización ASCII.
- Aplicada en: `wrestlers`, `titles/reigns`, `matches` (winner, loser).
- Unión primaria por coincidencia exacta de `name_slug`; fuzzy matching como respaldo controlado (score cutoff: 88).

#### Limpieza de campos

- Unificación de nombres de columnas entre fuentes.
- Conversión de fechas con `pd.to_datetime(..., errors='coerce')`.
- Limpieza de valores `NaN`, `inf` y duplicados.
- Parsing de medidas textuales (`6 ft 3 in` → `cm`, `266 lb` → `kg`).
- Limpieza de notas de referencia (`[1]`) en altura y peso.

#### Artefactos generados

| Artefacto | Registros | Descripción |
|-----------|-----------|-------------|
| `wrestling_clean.csv` | 19.278 | Dataset principal para ML y dashboard |
| `wrestlers_cleaned.csv` | 19.278 | Catálogo de luchadores |
| `wrestlers_enriched.csv` | 61 | Luchadores con datos biográficos ricos (Wikipedia) |
| `matches_normalized.csv` | 88.243 | Historial de combates normalizado |
| `titles_cleaned.csv` | 178 | Registros de campeonatos |
| `validation_report_wrestlers.*` | — | Reporte de validación (CSV, HTML, JSON) |
| `wrestlers_metadata.json` | — | Metadata del proceso de merge |
| `matches_metadata.json` | — | Metadata de validación de matches |

#### Metadata del proceso (wrestlers)

```json
{
  "generated_at": "2026-07-10T04:37:04Z",
  "source_files": ["wrestlers_thesportsdb.csv", "wrestlers_enriched.csv", "wrestlers_extracted.csv"],
  "rows_input": 148,
  "unique_before": 68,
  "unique_after": 67,
  "merges_performed": 2,
  "score_cutoff": 88
}
```

### 3.3 Ingeniería de Variables para ML

A partir del historial de combates (`matches_normalized.csv`) se derivaron estadísticas agregadas por luchador y se consolidaron en `wrestling_clean.csv`:

| Variable derivada | Descripción |
|-------------------|-------------|
| `total_wins` | Total de victorias históricas |
| `total_losses` | Total de derrotas históricas |
| `total_matches` | Total de combates disputados |
| `win_rate` | Proporción de victorias (wins / matches) |
| `total_titles` | Número de títulos ganados |
| `es_campeon` | Variable objetivo: 1 si tiene al menos un título registrado |
| `championship_probability` | Score de probabilidad entregado por el modelo entrenado (%) |

---

## 4. Análisis Exploratorio de Datos (EDA)

### 4.1 Descripción General del Dataset

| Dimensión | Valor |
|-----------|-------|
| Total de luchadores | **19.278** |
| Total de combates | **88.243** |
| Registros de títulos | **178** |
| Luchadores con campeonato | **738** (3,83 %) |
| Luchadores sin campeonato | **18.540** (96,17 %) |
| Cambios de título | **1.762** (2,00 % de combates) |

### 4.2 Distribución de Combates por Tipo de Victoria

| Tipo de resultado | Cantidad |
|-------------------|----------|
| `def. (pin)` — Derrota por pin | 44.988 |
| `def.` — Decisión | 29.974 |
| `def. (sub)` — Rendición | 4.801 |
| `def. (DQ)` — Descalificación | 4.640 |
| `draw (NC)` — Empate (sin conclusión) | 1.621 |
| `def. (CO)` — Conteo fuera | 984 |
| Otros tipos | 1.235 |

El resultado por pin es el más común (51 %), seguido por decisión directa (34 %). Las rendiciones representan el 5,4 % y las descalificaciones el 5,3 %.

### 4.3 Estadísticas de Rendimiento de Luchadores

#### Distribución de `win_rate`

| Estadístico | Valor |
|-------------|-------|
| Media | 0,331 |
| Desviación estándar | 0,416 |
| Mínimo | 0,000 |
| Percentil 25 | 0,000 |
| Mediana | 0,000 |
| Percentil 75 | 0,714 |
| Máximo | 1,000 |

La distribución es fuertemente bimodal: la mediana es 0 porque la mayoría de los luchadores del dataset tiene muy pocos combates registrados (solo 1 en el percentil 50).

#### Distribución de `total_matches`

| Estadístico | Valor |
|-------------|-------|
| Media | 9,15 combates |
| Desviación estándar | 40,75 |
| Mínimo | 1 |
| Percentil 75 | 3 |
| Máximo | 995 (Kane) |

La distribución tiene una cola derecha muy pronunciada (larga cola positiva). La gran mayoría de luchadores tiene 1–3 combates registrados, mientras que las leyendas del roster acumulan cientos.

### 4.4 Comparación: Campeones vs No Campeones

| Métrica | Campeones | No Campeones |
|---------|-----------|--------------|
| Win rate promedio | **0,610** | 0,320 |
| Total victorias (media) | **71,5** | 1,9 |
| Total derrotas (media) | **47,8** | 2,9 |
| Total combates (media) | **119,3** | 4,8 |
| Títulos ganados (media) | **2,4** | 0,0 |

Los campeones tienen en promedio ~25× más combates que los no campeones, y su win rate es casi el doble. Esto confirma una separación clara de perfiles que el modelo puede aprender.

### 4.5 Desbalance de Clases

```
Clase 0 (no campeón): 18.540 registros — 96,17 %
Clase 1 (campeón):       738 registros —  3,83 %
Ratio de desbalance: ~25:1
```

El desbalance severo es el principal desafío del modelo. Para mitigarlo se usó `class_weight='balanced'` en Logistic Regression, `class_weight='balanced'` en Random Forest, y `scale_pos_weight` calculado automáticamente para XGBoost.

### 4.6 Top 10 Luchadores por Victorias Totales

| Luchador | Victorias | Derrotas | Combates | Win Rate | Títulos | Score ML |
|----------|-----------|----------|----------|----------|---------|----------|
| John Cena | 796 | 170 | 966 | 82,4 % | 23 | 58,5 % |
| The Undertaker | 634 | 151 | 785 | 80,8 % | 7 | 56,9 % |
| Randy Orton | 612 | 326 | 938 | 65,2 % | 15 | 46,4 % |
| The Big Show | 593 | 373 | 966 | 61,4 % | 8 | 43,4 % |
| Sheamus | 556 | 287 | 843 | 65,9 % | 9 | 46,7 % |
| Chris Jericho | 543 | 420 | 963 | 56,4 % | 19 | 40,5 % |
| Kane | 536 | 459 | 995 | 53,9 % | 6 | 38,0 % |
| Dolph Ziggler | 512 | 479 | 991 | 51,7 % | 10 | 36,8 % |
| Roman Reigns | 475 | 65 | 540 | 87,9 % | 8 | 62,1 % |
| Rob Van Dam | 452 | 149 | 601 | 75,2 % | 13 | 53,5 % |

Roman Reigns tiene el win rate más alto del top 10 (87,9 %) a pesar de tener menos combates totales, lo que refleja su dominio en períodos recientes del roster.

### 4.7 Distribución del Score de Probabilidad

| Métrica | Valor |
|---------|-------|
| Media del score (todos) | 23,3 % |
| Desviación estándar | 29,2 % |
| Mediana | 0,0 % |
| Score máximo | 85,0 % |
| Luchadores con score ≥ 70 % | **4.264** |

La distribución bimodal del score refleja la separación del dataset: la mayoría de luchadores queda en 0 % (no campeones con historial mínimo) y una cola de luchadores con buen historial alcanza scores altos.

---

## 5. Modelo de Machine Learning

### 5.1 Objetivo del Modelo

El modelo clasifica si un luchador tiene **perfil histórico de campeón** basándose exclusivamente en sus estadísticas de combate. No predice el futuro: es una clasificación comparativa contra los patrones históricos del dataset.

- **Clase 1:** El luchador se parece al grupo histórico de campeones.
- **Clase 0:** El luchador se parece más al grupo sin campeonatos visibles.

### 5.2 Features Utilizadas

| Feature | Descripción |
|---------|-------------|
| `total_wins` | Total de victorias |
| `total_losses` | Total de derrotas |
| `total_matches` | Total de combates |
| `win_rate` | Proporción victorias/combates |

### 5.3 Variable Objetivo

`es_campeon`: binaria (0 = no campeón, 1 = campeón), derivada de si el luchador tiene al menos un título registrado en `titles_cleaned.csv`.

### 5.4 Preprocesamiento

```
Imputación (mediana) ──► Escalado estándar (StandardScaler) ──► Clasificador
```

Se usó un `Pipeline` de scikit-learn que encadena `SimpleImputer(strategy='median')` y `StandardScaler()` para las features numéricas, garantizando que los valores nulos no rompan el entrenamiento.

### 5.5 División del Dataset

| Conjunto | Registros | Proporción |
|----------|-----------|------------|
| Entrenamiento | 15.422 | 80 % |
| Test | 3.856 | 20 % |

División estratificada (`stratify=y`) para mantener la proporción de clases en ambos conjuntos.

### 5.6 Selección del Modelo — GridSearchCV

Se evaluaron tres algoritmos mediante `GridSearchCV` con validación cruzada estratificada de 5 folds (`StratifiedKFold`). La métrica de selección fue **F1 macro** para dar igual peso a ambas clases:

| Modelo | Hiperparámetros buscados | Manejo del desbalance |
|--------|--------------------------|----------------------|
| **Logistic Regression** | `C`: [0.1, 1.0, 10.0] | `class_weight='balanced'` |
| **Random Forest** | `n_estimators`: [100, 200], `max_depth`: [5, 10, None], `min_samples_leaf`: [1, 3] | `class_weight='balanced'` |
| **XGBoost** | `n_estimators`: [100, 200], `learning_rate`: [0.01, 0.05, 0.1], `max_depth`: [3, 5] | `scale_pos_weight` = 25,12 |

**Modelo seleccionado: Logistic Regression** con F1 macro de validación cruzada = **0,7409**.

### 5.7 Resultados del Modelo en Test

#### Métricas globales

| Métrica | Valor |
|---------|-------|
| **Accuracy** | **94,61 %** |
| **F1 Score (clase 1 — campeón)** | **0,5439** |
| **ROC-AUC** | **0,9530** |
| F1 macro promedio | 0,7576 |
| F1 ponderado | 0,9549 |

#### Reporte de Clasificación Detallado

| Clase | Precisión | Recall | F1-Score | Soporte |
|-------|-----------|--------|----------|---------|
| **0** (No campeón) | 0,9932 | 0,9504 | 0,9713 | 3.708 |
| **1** (Campeón) | 0,4026 | 0,8378 | 0,5439 | 148 |
| **Macro avg** | 0,6979 | 0,8941 | 0,7576 | 3.856 |
| **Weighted avg** | 0,9706 | 0,9461 | 0,9549 | 3.856 |

#### Interpretación de los Resultados

- **Alta accuracy (94,6 %):** Se explica por el desbalance de clases: el modelo puede alcanzar 96 % simplemente prediciendo siempre "no campeón". El accuracy no es el indicador más informativo en este caso.

- **ROC-AUC = 0,953:** Excelente capacidad discriminativa del modelo para separar campeones de no campeones a distintos umbrales de probabilidad. El modelo captura muy bien el orden relativo.

- **Recall clase 1 = 83,8 %:** El modelo identifica correctamente 8 de cada 10 campeones reales. Esto es valioso: minimiza falsos negativos (campeones no detectados).

- **Precisión clase 1 = 40,3 %:** Al predecir "campeón", el modelo acierta en 4 de cada 10 casos. La baja precisión es consecuencia directa del desbalance: hay muchos no campeones que, por tener un buen win rate en pocos combates, quedan cerca de la frontera.

- **F1 clase 1 = 0,544:** Balance entre precisión y recall para la clase minoritaria. Razonable dado el desbalance severo (25:1).

#### Balance de Clases en el Dataset Completo

```
Clase 0 (no campeón): 18.540 registros
Clase 1 (campeón):       738 registros
Total:                 19.278 registros
```

### 5.8 Exportación del Modelo

El modelo final fue exportado con `joblib` en:

```
wrestling-pipeline/models/champion_predictor.pkl
```

Y las métricas completas en:

```
wrestling-pipeline/models/evaluation_report.json
```

El score de afinidad histórica (`championship_probability`) de cada luchador fue generado en batch y persistido en `wrestling_clean.csv` para su consumo directo por la API y el dashboard.

### 5.9 Limitaciones del Modelo

1. **No usa contexto actual:** No considera storylines, popularidad real, lesiones ni retiros.
2. **Dependencia del dataset:** Si un luchador tiene pocas apariciones en el historial de combates, su score no es representativo.
3. **No distingue eras:** Un luchador de los 80s y uno actual comparten la misma lógica.
4. **Clasificación histórica, no predicción:** El score refleja similitud con el patrón histórico, no probabilidad de ganar un título en el futuro.

---

## 6. API REST

### 6.1 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/wrestlers` | Lista de luchadores con filtros (source, limit, offset) |
| GET | `/wrestlers/{id}` | Detalle: perfil fanático, title_history, analytics |
| GET | `/titles` | Lista de campeonatos con historial |
| GET | `/matches` | Lista de combates |
| GET | `/search?q=<term>` | Búsqueda global en wrestlers, titles, matches |
| GET | `/health` | Estado del servicio |

### 6.2 Enriquecimiento por Perfil

- **Fanático:** imagen, nombre artístico, nombre real, biografía, peso, altura y nacimiento.
- **Periodista:** cronología completa de reinados con `event_date`, `location`, `days_recognized`, `era`, `previous_champion`, `next_champion`, `notes`.
- **Desarrollador/Analista:** KPIs agregados (`wins`, `losses`, `win_rate`, `win_type` más frecuente), score ML, score de afinidad.

---

## 7. Dashboard

### 7.1 Perfiles de Usuario

| Perfil | Visualizaciones |
|--------|----------------|
| **Fanático** | Ficha biográfica, imagen, estadísticas básicas, curiosidades |
| **Periodista** | Hero contextual, KPIs, tabs (Resumen/Cronología/Campeonatos/Datos), timeline de reinados, tarjetas narrativas por cambio de manos |
| **Desarrollador/Analista** | Filtros por campeonato/era/año, histogramas altura y peso, scatter altura×peso, boxplots por era, tendencias por década, freak facts individuales |

---

## 8. Pruebas y Calidad

### 8.1 Cobertura de Tests

| Módulo | Archivo | Qué valida |
|--------|---------|-----------|
| Extractores | `tests/test_extractors.py` | Cada extractor individual, aliases Wikipedia, invalidación de caché TheSportsDB |
| ETL | `tests/test_etl.py` | Normalización, `normalize_titles()` con roster académico |
| API | `tests/test_api.py` | Contratos JSON de endpoints, enriquecimiento de `/titles` y `title_history` |

### 8.2 Criterios de Validación del Pipeline

- ✅ El ETL procesa al menos 3 fuentes de datos diferentes.
- ✅ `matches_metadata.json` confirma 88.243 filas sin pérdida en validación.
- ✅ `wrestlers_metadata.json` reporta merge de 2 fuentes con score cutoff 88.
- ✅ El modelo exportado genera `championship_probability` para los 19.278 luchadores.
- ✅ La API devuelve `data_available: false` con razón explícita cuando faltan datos.

---

## 9. Despliegue

### 9.1 Prerrequisitos

- Docker ≥ 24.0, Docker Compose ≥ 2.20
- Variable `THESPORTSDB_API_KEY` definida en `.env`

### 9.2 Ejecución Local

```bash
cd wrestling-pipeline
./scripts/run_local.sh
```

El script construye imágenes, ejecuta el ETL, levanta la API y el dashboard, y valida que los servicios respondan.

### 9.3 Servicios Disponibles

| Servicio | URL |
|----------|-----|
| API REST | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| Dashboard | `http://localhost:8501` |

---

## 10. Conclusiones

### 10.1 Resultados del EDA

- El dataset contiene **19.278 luchadores y 88.243 combates** históricos, con un desbalance pronunciado: solo el **3,83 %** de los luchadores tienen al menos un campeonato registrado.
- Los campeones presentan estadísticas significativamente superiores: win rate promedio de **61 %** vs **32 %** en no campeones, y **119 combates promedio** vs **4,8** en no campeones.
- El tipo de resultado más común es el pin (51 %), y solo el **2 %** de los combates implican un cambio de título.
- El dataset tiene una larga cola positiva en combates: la mediana es 1, pero el máximo llega a 995 (Kane), lo que requiere normalización y manejo cuidadoso de outliers.

### 10.2 Resultados del Modelo de ML

- El modelo de **Regresión Logística** fue seleccionado como el mejor por GridSearchCV entre tres candidatos (LR, Random Forest, XGBoost), obteniendo un **F1 macro de 0,741** en validación cruzada.
- En el conjunto de test alcanzó un **ROC-AUC de 0,953**, lo que indica excelente capacidad de separación entre clases a distintos umbrales.
- El **recall de la clase campeón es 83,8 %**: el modelo detecta correctamente 8 de cada 10 campeones.
- La baja precisión de la clase campeón (40,3 %) es esperable con un desbalance de 25:1, y puede mejorarse ajustando el umbral de decisión según el caso de uso.

### 10.3 Valor del Proyecto

- Integra tres fuentes heterogéneas (API REST, web scraping, SQLite) en un único pipeline reproducible y testeado.
- Entrega una herramienta de exploración interactiva adaptada a tres perfiles de usuario distintos.
- El modelo ML convierte datos históricos dispersos en una lectura comparativa simple, útil para análisis, narrativa y exploración del roster.

### 10.4 Trabajo Futuro

- **Datos biográficos:** Completar `height_cm`, `weight_kg`, `birth_date` para los 19.278 luchadores (actualmente solo disponibles en el subconjunto enriquecido por Wikipedia).
- **Modelo multi-clase:** Extender la predicción a categorías de título específicas (WWE Championship, Royal Rumble, etc.).
- **Features adicionales:** Incorporar racha de victorias consecutivas, tipo de combate predominante, duración promedio y era de actividad.
- **Despliegue en la nube:** Migrar a AWS/GCP/Azure con CI/CD automatizado via GitHub Actions.
- **Monitoreo de drift:** Detectar cambios en las distribuciones del dataset cuando se actualicen las fuentes.

---

*Informe generado a partir de los artefactos de datos producidos por el pipeline el 2026-07-10.*

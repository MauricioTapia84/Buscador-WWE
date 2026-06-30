# Plan de Implementación: Modelo Predictivo WWE y Refactorización del Pipeline

## Objetivo

Implementar un modelo de Machine Learning que prediga si un luchador será campeón, refactorizando el pipeline ETL actual para unificar fuentes, realizar una limpieza robusta, y desplegar el modelo en el dashboard mediante Docker, cumpliendo al 100% con la rúbrica del encargo.

## Open Questions

- **Métricas de Evaluación:** Dado el desbalance de clases (hay pocos campeones en comparación con todo el roster), propongo usar F1-Score y AUC-ROC como métricas principales. ¿Estás de acuerdo con enfocar la evaluación en estas métricas en lugar de "Accuracy"?
- si estoy de acuerdo
- **Automatización CI/CD:** Mencionas que debe estar automatizado. ¿Prefieres que agreguemos un flujo de GitHub Actions para correr pruebas automatizadas del ETL y Modelos, o te refieres solo a la automatización mediante `docker-compose` en el servidor local
- me gustaria que inicalmente se haga con automatizacion local con el docker-compose, usando el script que arranque los docker y los compile como ya tenia el proyecto

## Flujo de Trabajo Propuesto (Arquitectura)

cambie el diagrama a formato svg puedes hacer que se visualze en mi archivo

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1250" viewBox="0 0 1100 1250">
  <defs>
    <!-- Flechas -->
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#6c757d" />
    </marker>
    <!-- Sombra para recuadros -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="#000" flood-opacity="0.08" />
    </filter>
    <!-- Gradientes -->
    <linearGradient id="gradETL" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#e3f2fd" />
      <stop offset="100%" stop-color="#bbdefb" />
    </linearGradient>
    <linearGradient id="gradML" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fce4ec" />
      <stop offset="100%" stop-color="#f8bbd0" />
    </linearGradient>
    <linearGradient id="gradDeploy" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#e8f5e9" />
      <stop offset="100%" stop-color="#c8e6c9" />
    </linearGradient>
  </defs>

  <style>
    .box {
      fill: #ffffff;
      stroke: #dee2e6;
      stroke-width: 2px;
      rx: 12px;
      ry: 12px;
      filter: url(#shadow);
    }
    .box-etl { fill: url(#gradETL); stroke: #90caf9; stroke-width: 2px; rx: 12px; ry: 12px; filter: url(#shadow); }
    .box-ml { fill: url(#gradML); stroke: #f48fb1; stroke-width: 2px; rx: 12px; ry: 12px; filter: url(#shadow); }
    .box-deploy { fill: url(#gradDeploy); stroke: #81c784; stroke-width: 2px; rx: 12px; ry: 12px; filter: url(#shadow); }
    .title {
      font: bold 15px 'Segoe UI', 'Inter', sans-serif;
      fill: #212529;
      letter-spacing: -0.2px;
    }
    .subtitle {
      font: 13px 'Segoe UI', 'Inter', sans-serif;
      fill: #495057;
    }
    .small-text {
      font: 12px 'Segoe UI', 'Inter', sans-serif;
      fill: #6c757d;
    }
    .section-label {
      font: bold 16px 'Segoe UI', 'Inter', sans-serif;
      fill: #212529;
      letter-spacing: 0.5px;
    }
    .arrow {
      fill: none;
      stroke: #6c757d;
      stroke-width: 2.5px;
      marker-end: url(#arrowhead);
    }
    .dashed-arrow {
      fill: none;
      stroke: #adb5bd;
      stroke-width: 2px;
      stroke-dasharray: 6 4;
      marker-end: url(#arrowhead);
    }
  </style>

  <!-- ============================ -->
  <!-- SECCIÓN 1: ETL EXTRACT      -->
  <!-- ============================ -->
  <rect x="40" y="20" width="1020" height="28" rx="6" ry="6" fill="#e3f2fd" stroke="#90caf9" stroke-width="1" />
  <text x="60" y="39" class="section-label">1. Extracción y Unificación (ETL - Extract)</text>

  <!-- Fuentes de datos -->
  <rect x="40" y="60" width="300" height="80" class="box-etl" />
  <text x="65" y="85" class="title">🗄️ Kaggle SQLite</text>
  <text x="65" y="105" class="subtitle">Matches · Titles · Wrestlers</text>
  <text x="65" y="125" class="small-text">~171 MB de datos históricos</text>

  <rect x="380" y="60" width="300" height="80" class="box-etl" />
  <text x="405" y="85" class="title">🌐 TheSportsDB API</text>
  <text x="405" y="105" class="subtitle">Bios · Medidas · Imágenes</text>
  <text x="405" y="125" class="small-text">REST API con clave pública</text>

  <rect x="720" y="60" width="300" height="80" class="box-etl" />
  <text x="745" y="85" class="title">📄 Wikipedia API</text>
  <text x="745" y="105" class="subtitle">Extras · Campeones</text>
  <text x="745" y="125" class="small-text">Tablas de títulos y fechas</text>

  <!-- Unificador -->
  <rect x="300" y="175" width="460" height="70" class="box" fill="#ffffff" stroke="#90caf9" stroke-width="2" />
  <text x="325" y="200" class="title">🔗 Unificador & Fuzzy Matching</text>
  <text x="325" y="220" class="subtitle">Resolución de nombres: Triple H → Hunter Hearst Helmsley</text>

  <!-- Flechas -->
  <path class="arrow" d="M 190 140 L 190 160 L 530 160 L 530 175" />
  <path class="arrow" d="M 530 140 L 530 175" />
  <path class="arrow" d="M 870 140 L 870 160 L 530 160 L 530 175" />

  <!-- ============================ -->
  <!-- SECCIÓN 2: ETL TRANSFORM    -->
  <!-- ============================ -->
  <rect x="40" y="280" width="1020" height="28" rx="6" ry="6" fill="#e3f2fd" stroke="#90caf9" stroke-width="1" />
  <text x="60" y="299" class="section-label">2. Limpieza y Normalización (ETL - Transform)</text>

  <rect x="40" y="320" width="1020" height="80" class="box-etl" />
  <text x="65" y="345" class="title">🧹 Estandarización y Limpieza</text>
  <text x="65" y="365" class="subtitle">• Manejo de nulos e imputación (media por nacionalidad)</text>
  <text x="65" y="385" class="subtitle">• Transformaciones con Pandas: merge, groupby, vectorización</text>

  <!-- Flecha interna -->
  <path class="arrow" d="M 550 400 L 550 420" />

  <!-- Dataset consolidado -->
  <rect x="300" y="430" width="460" height="60" class="box" fill="#ffffff" stroke="#90caf9" stroke-width="2" />
  <text x="325" y="455" class="title">💾 Data Set Consolidado</text>
  <text x="325" y="475" class="subtitle">data/processed/wrestling_clean.csv</text>

  <!-- ============================ -->
  <!-- SECCIÓN 3: ML PREPARACIÓN   -->
  <!-- ============================ -->
  <rect x="40" y="530" width="1020" height="28" rx="6" ry="6" fill="#fce4ec" stroke="#f48fb1" stroke-width="1" />
  <text x="60" y="549" class="section-label">3. Preparación Machine Learning</text>

  <rect x="40" y="570" width="300" height="70" class="box-ml" />
  <text x="65" y="595" class="title">📊 Train/Test Split</text>
  <text x="65" y="615" class="subtitle">80/20 · Evita Data Leakage</text>

  <rect x="380" y="570" width="300" height="70" class="box-ml" />
  <text x="405" y="595" class="title">📈 Análisis EDA</text>
  <text x="405" y="615" class="subtitle">Correlaciones · Distribuciones</text>

  <rect x="720" y="570" width="300" height="70" class="box-ml" />
  <text x="745" y="595" class="title">⚙️ Feature Engineering</text>
  <text x="745" y="615" class="subtitle">Scaling · OneHotEncoding</text>

  <!-- Flechas -->
  <path class="arrow" d="M 340 605 L 365 605" />
  <path class="arrow" d="M 680 605 L 705 605" />

  <!-- ============================ -->
  <!-- SECCIÓN 4: MODELADO        -->
  <!-- ============================ -->
  <rect x="40" y="680" width="1020" height="28" rx="6" ry="6" fill="#fce4ec" stroke="#f48fb1" stroke-width="1" />
  <text x="60" y="699" class="section-label">4. Modelado y Selección</text>

  <rect x="40" y="720" width="280" height="70" class="box-ml" />
  <text x="65" y="745" class="title">📉 Regresión Logística</text>
  <text x="65" y="765" class="subtitle">Baseline · Interpretable</text>

  <rect x="360" y="720" width="280" height="70" class="box-ml" />
  <text x="385" y="745" class="title">🌲 Random Forest</text>
  <text x="385" y="765" class="subtitle">Con GridSearchCV</text>

  <rect x="680" y="720" width="280" height="70" class="box-ml" />
  <text x="705" y="745" class="title">⚡ XGBoost</text>
  <text x="705" y="765" class="subtitle">Con GridSearchCV</text>

  <!-- Evaluación -->
  <rect x="300" y="820" width="460" height="60" class="box" fill="#ffffff" stroke="#f48fb1" stroke-width="2" />
  <text x="325" y="845" class="title">🏆 Evaluación & Selección</text>
  <text x="325" y="865" class="subtitle">F1-Score · AUC-ROC · Matriz de Confusión → best_model.pkl</text>

  <!-- Flechas hacia evaluación -->
  <path class="arrow" d="M 180 790 L 180 810 L 530 810 L 530 820" />
  <path class="arrow" d="M 500 790 L 500 820" />
  <path class="arrow" d="M 820 790 L 820 810 L 530 810 L 530 820" />

  <!-- ============================ -->
  <!-- SECCIÓN 5: DESPLIEGUE      -->
  <!-- ============================ -->
  <rect x="40" y="920" width="1020" height="28" rx="6" ry="6" fill="#e8f5e9" stroke="#81c784" stroke-width="1" />
  <text x="60" y="939" class="section-label">5. Despliegue y Automatización (Docker)</text>

  <!-- API -->
  <rect x="40" y="960" width="480" height="80" class="box-deploy" />
  <text x="65" y="985" class="title">🚀 API REST FastAPI</text>
  <text x="65" y="1005" class="subtitle">Endpoint /predict · Carga best_model.pkl</text>
  <text x="65" y="1025" class="small-text">Recibe datos físicos e históricos → devuelve probabilidad</text>

  <!-- Dashboard -->
  <rect x="560" y="960" width="480" height="80" class="box-deploy" />
  <text x="585" y="985" class="title">📊 Dashboard Streamlit</text>
  <text x="585" y="1005" class="subtitle">Interfaz de Usuario · Panel de consulta</text>
  <text x="585" y="1025" class="small-text">Selecciona luchador → consulta al modelo</text>

  <!-- Docker Compose -->
  <rect x="300" y="1070" width="460" height="50" class="box" fill="#ffffff" stroke="#81c784" stroke-width="2" />
  <text x="325" y="1095" class="title">🐳 Docker Compose</text>
  <text x="325" y="1115" class="subtitle">Levanta API + Dashboard + Base de Datos</text>

  <!-- Flechas hacia API y Dashboard -->
  <path class="arrow" d="M 530 880 L 530 945 L 280 945 L 280 960" />
  <path class="arrow" d="M 530 880 L 530 960" />

  <!-- Flechas desde Docker Compose -->
  <path class="dashed-arrow" d="M 460 1095 L 280 1095 L 280 1040" />
  <path class="dashed-arrow" d="M 600 1095 L 800 1095 L 800 1040" />

  <!-- ============================ -->
  <!-- LEYENDA / PIE DE PÁGINA     -->
  <!-- ============================ -->
  <rect x="40" y="1155" width="1020" height="30" rx="8" ry="8" fill="#f1f3f5" stroke="#dee2e6" stroke-width="1" />
  <text x="60" y="1175" class="small-text" fill="#495057">
    🔄 Flujo End‑to‑End: Extracción → Limpieza → ML → Despliegue con Docker
  </text>
  <text x="840" y="1175" class="small-text" fill="#6c757d">
    ⚡ Proyecto alineado al 100% con rúbrica EFT
  </text>

</svg>
```

## Checklist Detallado (Alineado a la Rúbrica)

### 1. Extracción y Limpieza (ETL Avanzado - IEE 1.1.1, IEE 1.2.1, IEE 1.3.1, IEE 3.1.1)

- [ ] **Unificación de Fuentes:** Refactorizar `extract_kaggle.py`, `extract_thesportsdb.py` y `extract_wikipedia.py` para converger en un único DataFrame base.
- [ ] **Resolución de Nombres:** Implementar *fuzzy matching* para unificar a un luchador que se llame distinto en Kaggle vs TheSportsDB (ej. "Triple H" vs "Hunter Hearst Helmsley").
- [ ] **Transformaciones Pandas Avanzadas:** Usar `.merge()`, `.groupby()` con chunking o vectorización para calcular el historial de victorias.
- [ ] **Imputación de Nulos:** Documentar por qué se reemplazan valores nulos en peso/altura (ej. imputar por la media según nacionalidad/género).
- [ ] **Exportación:** Guardar el dataset limpio en `data/processed/`.

### 2. Machine Learning (IEE 2.1.1)

- [ ] **Train/Test Split:** Separar los datos 80/20 antes del análisis.
- [ ] **Análisis Exploratorio (EDA):** Crear `/models/01_eda.ipynb` para analizar correlaciones de altura/peso vs. campeonatos.
- [ ] **Feature Engineering Pipeline:** Crear un `ColumnTransformer` (Scikit-Learn) que escale numéricos (`StandardScaler`) y codifique categóricos (`OneHotEncoder`).
- [ ] **Entrenamiento de Modelos:** Crear script `/models/train.py`.
- [ ] **Optimización (Tuning):** Usar `GridSearchCV` en Random Forest y XGBoost.
- [ ] **Evaluación:** Comparar métricas, matriz de confusión y exportar el mejor modelo (ej. `best_model.pkl`).

### 3. API y Dashboard (Integración Continua)

- [ ] **Crear Endpoint:** Añadir una ruta `/predict` en la carpeta `/api/` que reciba los datos físicos e históricos de un luchador y devuelva la probabilidad de campeonato.
- [ ] **Integración en Dashboard:** Modificar el código de `/dashboards/` para incluir un panel donde el usuario elija un luchador o ingrese atributos para consultar al modelo.
- [ ] **Dockerización:** Actualizar el `docker-compose.yml` para asegurarse de que el contenedor de la API levante el modelo correctamente.

### 4. Aspectos Formales e Informe Técnico

- [ ] **Testing:** Escribir tests unitarios en `/tests/` para verificar que el modelo carga y la API responde.
- [ ] **Documentación en Código:** Asegurar que todo código nuevo tenga Docstrings.
- [ ] **Redacción del Informe Final:** Armar la presentación y reporte técnico.

## Verificación

- Levantaremos todo el stack con `docker-compose up --build`.
- Haremos peticiones de prueba a la API de predicción.
- Simularemos el uso del dashboard.


# Entonces el sistema puede concluir correctamente:

Hola Codex. Logramos levantar la API con éxito (ya detecta los luchadores y reinados), pero tenemos dos problemas críticos en el Dashboard de Streamlit (según vemos en la interfaz y en el payload analítico de personajes como "Triple H"):

1. El objeto "analytics": {} viene completamente vacío para casi todos los luchadores, dejando las métricas de combates, victorias y Win-Rate en cero.
2. El tema visual tiene un problema grave de contraste: los números de las métricas se renderizan en color blanco/gris muy claro sobre fondo crema, lo que los hace invisibles.

Necesito que apliques las siguientes correcciones de inmediato:

### Tarea 1: Corregir el Contraste Visual de Streamlit

- Revisa el archivo `.streamlit/config.toml`. Si no existe, créalo en la raíz del frontend.
- Asegúrate de forzar un tema con alto contraste. Si el fondo (`backgroundColor`) es claro, el color del texto (`textColor`) debe ser explícitamente oscuro. Configúralo idealmente así:

```toml
  [theme]
  primaryColor = "#d32f2f"
  backgroundColor = "#f8f9fa"
  secondaryBackgroundColor = "#ffffff"
  textColor = "#212121"
  font = "sans ser
```

- la foto y biografía pertenecen al mismo luchador,
- el reinado pertenece a ese mismo perfil,
- las victorias en matches también pertenecen a ese mismo perfil.

Ese es el cruce real.

No se hace por texto “bonito”.

Se hace por clave limpia y consistente.

---

## 9. Resumen corto

La lógica de cruce entre fuentes funciona así:

Hola Codex. Logramos levantar la API con éxito (ya detecta los luchadores y reinados), pero tenemos dos problemas críticos en el Dashboard de Streamlit (según vemos en la interfaz y en el payload analítico de personajes como "Triple H"):

1. El objeto "analytics": {} viene completamente vacío para casi todos los luchadores, dejando las métricas de combates, victorias y Win-Rate en cero.
2. El tema visual tiene un problema grave de contraste: los números de las métricas se renderizan en color blanco/gris muy claro sobre fondo crema, lo que los hace invisibles.

Necesito que apliques las siguientes correcciones de inmediato:

### Tarea 1: Corregir el Contraste Visual de Streamlit

- Revisa el archivo `.streamlit/config.toml`. Si no existe, créalo en la raíz del frontend.
- Asegúrate de forzar un tema con alto contraste. Si el fondo (`backgroundColor`) es claro, el color del texto (`textColor`) debe ser explícitamente oscuro. Configúralo idealmente así:

```toml
  [theme]
  primaryColor = "#d32f2f"
  backgroundColor = "#f8f9fa"
  secondaryBackgroundColor = "#ffffff"
  textColor = "#212121"
  font = "sans serif"
```


1. se extraen datos de varias fuentes con estructuras distintas,
2. se limpian nombres y se genera una clave tipo `slug`,
3. esa clave se usa como identidad común del luchador,
4. la API une:
   - biografía,
   - reinados,
   - combates,
5. el dashboard consume el resultado ya enriquecido.

La regla más importante del sistema es:

```text
no unir por nombre crudo;
unir por nombre normalizado
```

---

## 10. Archivos clave para entender el flujo

- [wrestling-pipeline/etl/name_utils.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/name_utils.py)
- [wrestling-pipeline/etl/extract_kaggle.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_kaggle.py)
- [wrestling-pipeline/etl/extract_thesportsdb.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_thesportsdb.py)
- [wrestling-pipeline/etl/extract_wikipedia.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/extract_wikipedia.py)
- [wrestling-pipeline/etl/normalize.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/normalize.py)
- [wrestling-pipeline/etl/run_etl.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/etl/run_etl.py)
- [wrestling-pipeline/api/main.py](/home/tomy/Downloads/Instituto/Buscador-WWE/wrestling-pipeline/api/main.py)

Si quieres, en el siguiente paso puedo agregarte al mismo `EXPLICATION.md` un diagrama visual tipo flujo ETL -> normalización -> API -> dashboard.

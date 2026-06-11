1.3 - Título del cambio

Resumen breve (1 línea):

Descripción detallada:
- Qué se cambió:
  - Lista de archivos añadidos/movidos/eliminados
  - Principales funciones o comportamientos implementados

- Por qué se hizo (motivo / contexto):

- Impacto / Consideraciones:
  - Instrucciones para probar localmente
  - Dependencias añadidas
  - Cambios en configuración (variables de entorno, puertos)

Referencias:
- Issue/Task: # (si aplica)
- Archivos clave: `wrestling-pipeline/api/main.py`, `wrestling-pipeline/docker/docker-compose.yml`, `wrestling-pipeline/etl/`...

Ejemplo de uso (commit):

```bash
git add .
git commit -m "1.3: Estructura inicial del proyecto — API, ETL, dashboards, docker-compose"
git push origin <branch>
```

Checklist antes de merge:
- [ ] Tests locales pasan (`pytest tests/`)
- [ ] `README.md` actualizado
- [ ] `docs/guia_despliegue.md` revisada

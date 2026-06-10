---
name: data-skills
description: Herramientas especializadas para analizar archivos CSV, ejecutar notebooks de Jupyter y explicar código Python.
license: MIT
compatibility: python>=3.8, agentnova>=0.1.0
---

# Skill: data-skills

Este skill proporciona utilidades para análisis de datos y asistencia de programación en Python.

## Capacidades

### 1. Analizar Archivo CSV
Permite analizar la estructura y estadísticas descriptivas de un archivo CSV local.
- **Implementación**: `python3 -m agent.skills.data_skills analyze_csv <ruta_del_csv>`

### 2. Ejecutar Jupyter Notebook
Permite ejecutar todas las celdas de un archivo `.ipynb` de forma programática y guardar el resultado.
- **Implementación**: `python3 -m agent.skills.data_skills run_notebook <ruta_del_notebook>`

### 3. Explicar Código Python
Analiza la estructura sintáctica de un fragmento de código o archivo Python para listar clases, funciones e importaciones.
- **Implementación**: `python3 -m agent.skills.data_skills explain_code <ruta_o_fragmento_de_codigo>`

## Instrucciones para el Agente
1. Cuando el usuario te pida analizar un archivo CSV, usa la herramienta de shell para ejecutar `python3 -m agent.skills.data_skills analyze_csv <ruta>`.
2. Cuando se solicite ejecutar o correr un notebook `.ipynb`, ejecuta `python3 -m agent.skills.data_skills run_notebook <ruta>`.
3. Para dar una explicación estructural rápida de un archivo o bloque de código, ejecuta `python3 -m agent.skills.data_skills explain_code <ruta_o_bloque>`.

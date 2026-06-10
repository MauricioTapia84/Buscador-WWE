#!/usr/bin/env python3
"""
Módulo de Skills de Ciencia de Datos para AgentNova
"""

import sys
import os
import json
import ast

def analyze_csv(file_path: str) -> str:
    """Analiza un archivo CSV y retorna estadísticas básicas."""
    if not os.path.exists(file_path):
        return f"Error: El archivo '{file_path}' no existe."
    
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas no está instalado en el entorno actual."
    
    try:
        df = pd.read_csv(file_path)
        stats = {
            "num_rows": int(df.shape[0]),
            "num_cols": int(df.shape[1]),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        # Obtener descripción estadística para columnas numéricas
        numeric_desc = df.describe().to_dict()
        
        output = [
            "=== Análisis de CSV ===",
            f"Ruta: {file_path}",
            f"Filas: {stats['num_rows']} | Columnas: {stats['num_cols']}",
            "\nTipos de Datos y Valores Faltantes:",
        ]
        for col in df.columns:
            missing = stats['missing_values'][col]
            output.append(f" - {col}: {stats['data_types'][col]} (Faltantes: {missing})")
            
        if numeric_desc:
            output.append("\nResumen Estadístico Numérico:")
            for col, desc in numeric_desc.items():
                output.append(f"\nColumna: {col}")
                for stat_name, val in desc.items():
                    output.append(f"  {stat_name}: {val:.4f}" if isinstance(val, float) else f"  {stat_name}: {val}")
                    
        return "\n".join(output)
    except Exception as e:
        return f"Error al analizar el CSV: {str(e)}"

def run_notebook(notebook_path: str) -> str:
    """Ejecuta todas las celdas de un Jupyter Notebook y lo guarda."""
    if not os.path.exists(notebook_path):
        return f"Error: El notebook '{notebook_path}' no existe."
        
    try:
        import nbformat
        from nbconvert.preprocessors import ExecutePreprocessor
    except ImportError:
        return "Error: jupyter, nbformat o nbconvert no están instalados."
        
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
            
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path) or '.'}})
        
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
            
        return f"Notebook ejecutado con éxito y guardado en: {notebook_path}"
    except Exception as e:
        return f"Error al ejecutar el notebook: {str(e)}"

def explain_code(code_input: str) -> str:
    """Explica la estructura de un código Python (funciones, clases, dependencias)."""
    # Si es una ruta de archivo, leer el archivo
    code_content = code_input
    if os.path.exists(code_input):
        try:
            with open(code_input, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            return f"Error al leer el archivo de código: {str(e)}"
            
    try:
        tree = ast.parse(code_content)
        
        imports = []
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                # Solo funciones a nivel de módulo, no métodos de clase
                functions.append(node.name)
                
        explanation = [
            "=== Explicación de Código Python ===",
            f"Importaciones detectadas: {', '.join(imports) if imports else 'Ninguna'}",
            f"Clases definidas: {', '.join(classes) if classes else 'Ninguna'}",
            f"Funciones definidas: {', '.join(functions) if functions else 'Ninguna'}",
            "\nEstructura general del código:",
        ]
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                explanation.append(f" - Clase '{node.name}'")
                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef):
                        explanation.append(f"   * Método '{subnode.name}'")
            elif isinstance(node, ast.FunctionDef):
                explanation.append(f" - Función '{node.name}'")
                
        return "\n".join(explanation)
    except SyntaxError as e:
        return f"Error de sintaxis al parsear el código: {str(e)}"
    except Exception as e:
        return f"Error al analizar el código: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python -m agent.skills.data_skills [analyze_csv|run_notebook|explain_code] [argumento]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    arg = sys.argv[2]
    
    if cmd == "analyze_csv":
        print(analyze_csv(arg))
    elif cmd == "run_notebook":
        print(run_notebook(arg))
    elif cmd == "explain_code":
        print(explain_code(arg))
    else:
        print(f"Comando desconocido: {cmd}")
        sys.exit(1)

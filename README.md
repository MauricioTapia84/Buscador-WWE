# Buscador-WWE
Repositorio para proyecto de ciencia de datos donde se juntan multiples origenes de datos relacionados con la lucha libre

IA Oruga (subpaquete)
- Ruta: `IA_Oruga_Portable`
- Propósito: Asistente local portable con UI web y agentes para extracción y generación de contenidos.

Instrucciones rápidas (Linux / Zorin):

1. Preparar e instalar dependencias:

```bash
cd IA_Oruga_Portable
bash setup.sh
```

2. Activar entorno virtual:

```bash
source venv/bin/activate
```

3. Ejecutar la interfaz web:

```bash
./start-oruga.sh
```

Notas:
- Si un script busca `ia-oruga/scripts/build_ia_oruga_package.sh`, ahora existe y crea `IA_Oruga_Package.zip`.
- En Windows se dispone de `start-oruga.bat` para iniciar desde CMD/PowerShell; crear manualmente un venv si se requiere replicar `setup.sh`.
 - Comprobaciones post-setup:

	- Linux: `bash ia-oruga/scripts/check_setup.sh` (usa el `python` del `venv` si está presente).
	- Windows: `ia-oruga\scripts\check_setup.bat`.

# Proyect_Clinica

Sistema de escritorio offline-first para termografia medica, desarrollado con Python, PySide6, OpenCV, SQLAlchemy y ReportLab.

Permite gestionar historias clinicas, visualizar multiples camaras termicas, asociar capturas a pacientes y generar informes PDF.

Aplicacion de escritorio offline-first para registrar historias clinicas, visualizar camaras termicas, guardar capturas y generar informes PDF.

## Estructura

- `main.py`: punto de entrada de la aplicacion.
- `database.py`: modelos SQLAlchemy, sesiones y rutas de almacenamiento local.
- `services/`: persistencia de pacientes, captura de video y reportes.
- `ui/`: ventana y controles PySide6.
- `storage/`: base SQLite, capturas e informes generados. Los datos clinicos se excluyen de Git.

## Ejecucion en Windows

```powershell
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

La aplicacion puede ejecutarse sin internet despues de instalar las dependencias. Las camaras se intentan abrir en los indices 0, 1 y 2; si alguna no esta conectada, esa vista informa el problema y las demas continuan disponibles.

## Flujo recomendado

1. Buscar una cedula o crear un paciente nuevo.
2. Completar y guardar la historia clinica.
3. Capturar las camaras cuando exista un paciente guardado.
4. Generar el informe PDF.

## Versionado en GitHub

No se deben subir bases de datos, capturas ni informes porque contienen informacion medica. Cada avance puede registrarse con commits pequenos y descriptivos, por ejemplo:

```powershell
git add .
git commit -m "feat: separar servicios de captura y pacientes"
git push origin main
```

Antes del primer `push`, configura el repositorio remoto y verifica que `git status` no muestre archivos de `storage/`.

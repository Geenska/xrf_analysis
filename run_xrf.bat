@echo off
echo ===================================================
echo   Laboratorio CODICE - Iniciador XRF v2 (Windows)
echo ===================================================
echo.

cd /d "%~dp0"

:: Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH de Windows.
    echo Por favor, descarga e instala Python 3.9 a 3.12 desde python.org
    echo e IMPORTANTE: marca la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b
)

:: Crear entorno virtual de Windows si no existe
if not exist venv_win (
    echo Creando entorno virtual (venv_win) en Windows...
    python -m venv venv_win
)

:: Activar entorno virtual e instalar requerimientos
call venv_win\Scripts\activate.bat
echo Instalando/Actualizando dependencias de Python en Windows...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Ejecutar aplicacion (xrf_analysis.py)
echo.
echo Iniciando aplicacion XRF Analyzer (xrf_analysis.py)...
python xrf_analysis.py

pause

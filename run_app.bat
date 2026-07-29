@echo off
REM ConciliaPyme Ledger Pro - Script de Ejecución
REM Copyright 2026 © Creado por Pedro Narváez y Ariel Torres.

echo ========================================
echo   ConciliaPyme Ledger Pro v2.3.0
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instale Python 3.x
    pause
    exit /b 1
)

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Crear directorios necesarios
if not exist "data" mkdir data
if not exist "demo" mkdir demo

REM Ejecutar aplicación
echo Iniciando aplicación...
python src\conciliapyme.py

if errorlevel 1 (
    echo.
    echo ERROR: La aplicación encontró un problema.
    pause
)

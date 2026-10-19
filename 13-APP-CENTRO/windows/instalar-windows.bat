@echo off
rem Doble clic para instalar Centro APARDIAN (icono en el Escritorio y en Inicio).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
echo.
pause

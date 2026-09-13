@echo off
title Ghost Protocol - Phone Stream Viewer (Redmi A3)
color 0b
echo =====================================================================
echo       GHOST PROTOCOL - PHONE STREAM VIEWER (REDMI A3 / VISION PRO)
echo =====================================================================
echo.
echo [*] Demarrage du visualiseur de telephone...
echo [*] Ecran & Cameras (Avant / Arriere) en direct
echo.

cd /d "%~dp0"
python phone_viewer.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Erreur lors du lancement de phone_viewer.py.
    echo [*] Verifiez que webview et paho-mqtt sont bien installes.
    pause
)

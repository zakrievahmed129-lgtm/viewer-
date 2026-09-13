@echo off
:: Déplacement dans le dossier du script
cd /d "%~dp0"

:: Lance le script en arrière-plan de manière invisible (sans console associée)
:: Ainsi, même si vous fermez les invites de commande, le script continue de tourner.
start "" ".\venv\bin\pythonw.exe" ghost_script.py
exit

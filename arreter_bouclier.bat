@echo off
chcp 65001 >nul
echo Arret du bouclier GhostLock...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*pc_lock_shield.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host '[OK] Processus' $_.ProcessId 'arrete.' -ForegroundColor Yellow }"
echo [OK] Bouclier GhostLock arrete.

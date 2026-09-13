@echo off
chcp 65001 >nul
echo ========================================================
echo   INSTALLATION DU DÉMARRAGE AUTOMATIQUE GHOSTLOCK 24/7
echo ========================================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $sc = $WshShell.CreateShortcut(\"$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\GhostLock.lnk\"); $sc.TargetPath = 'C:\Users\zakri\AppData\Local\Programs\Python\Python313\pythonw.exe'; $sc.Arguments = '\"c:\Users\zakri\Desktop\les animations doivent etres incroyables\pc_lock_shield.py\" --lock'; $sc.WorkingDirectory = 'c:\Users\zakri\Desktop\les animations doivent etres incroyables'; $sc.Description = 'GhostLock Biometric Shield 24/7'; $sc.Save(); Write-Host '[OK] GhostLock enregistre pour zakri (avec verrouillage auto) !' -ForegroundColor Green"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$hadijPath = 'C:\Users\hadij\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'; if (Test-Path $hadijPath) { $WshShell = New-Object -ComObject WScript.Shell; $sc = $WshShell.CreateShortcut(\"$hadijPath\GhostLock.lnk\"); $sc.TargetPath = 'C:\Users\zakri\AppData\Local\Programs\Python\Python313\pythonw.exe'; $sc.Arguments = '\"c:\Users\zakri\Desktop\les animations doivent etres incroyables\pc_lock_shield.py\" --lock'; $sc.WorkingDirectory = 'c:\Users\zakri\Desktop\les animations doivent etres incroyables'; $sc.Description = 'GhostLock Biometric Shield 24/7'; $sc.Save(); Write-Host '[OK] GhostLock enregistre pour hadija (avec verrouillage auto) !' -ForegroundColor Green }"
python "%~dp0scratch\register_startup_priority.py"
echo.
echo GhostLock est pret avec verrouillage immediat au demarrage.
pause


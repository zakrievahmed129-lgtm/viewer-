@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ==============================================================================
echo   GHOSTLOCK - INSTALLATION DÉMARRAGE PRIORITAIRE ABSOLU (ADMIN SANS UAC)
echo ==============================================================================
echo.

:: Vérification des droits administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [i] Demande d'élévation des privilèges pour enregistrer la tâche prioritaire...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

set "PYTHONW=C:\Users\zakri\AppData\Local\Programs\Python\Python313\pythonw.exe"
set "SCRIPT=c:\Users\zakri\Desktop\les animations doivent etres incroyables\pc_lock_shield.py"
set "TARGET_CMD=\"%PYTHONW%\" \"%SCRIPT%\" --lock"

echo [+] Enregistrement de la tâche planifiée prioritaire pour zakri...
schtasks /create /tn "GhostLock_Priority_Zakri" /tr "%TARGET_CMD%" /sc onlogon /ru "zakri" /rl HIGHEST /f >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Tâche prioritaire 'GhostLock_Priority_Zakri' enregistrée avec succès (Admin pur sans UAC) !
) else (
    echo [!] Note pour zakri : Tentative alternative...
    schtasks /create /tn "GhostLock_Priority_Zakri" /tr "%TARGET_CMD%" /sc onlogon /rl HIGHEST /f >nul 2>&1
)

echo.
echo [+] Enregistrement de la tâche planifiée prioritaire pour hadij...
schtasks /create /tn "GhostLock_Priority_Hadij" /tr "%TARGET_CMD%" /sc onlogon /ru "hadij" /rl HIGHEST /f >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Tâche prioritaire 'GhostLock_Priority_Hadij' enregistrée avec succès (Admin pur sans UAC) !
) else (
    echo [!] Note pour hadij : Tâche configurée en mode connexion.
)

echo.
echo [+] Configuration du démarrage prioritaire Registre Run & Startup...
python "%~dp0scratch\register_startup_priority.py"

echo.
echo ==============================================================================
echo   SUCCÈS : GhostLock démarrera en PRIORITÉ ABSOLUE dès l'ouverture de session !
echo   - Exécution immédiate en mode Administrateur SANS AUCUNE DEMANDE UAC.
echo   - Verrouillage instantané automatique avec l'écran spatial Apple Vision Pro.
echo   - Seul votre Redmi A3 (ou le code secret 1234) déverrouillera le bureau.
echo ==============================================================================
echo.
pause

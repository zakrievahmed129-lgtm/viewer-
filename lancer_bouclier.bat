@echo off
chcp 65001 >nul
echo ========================================================
echo   BOUCLIER GHOSTLOCK EN ARRIERE-PLAN
echo ========================================================
powershell -NoProfile -ExecutionPolicy Bypass -Command "$running = Get-CimInstance Win32_Process | Where-Object { ($_.Name -like 'python*') -and ($_.CommandLine -like '*pc_lock_shield.py*') }; if ($running) { Write-Host '[i] Le bouclier GhostLock est DEJA actif (PID: ' $running.ProcessId ')' -ForegroundColor Cyan } else { $pyw = 'C:\Users\zakri\AppData\Local\Programs\Python\Python313\pythonw.exe'; $dir = 'c:\Users\zakri\Desktop\les animations doivent etres incroyables'; $script = Join-Path $dir 'pc_lock_shield.py'; $cmd = '\"' + $pyw + '\" \"' + $script + '\"'; Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$cmd; CurrentDirectory=$dir} | Out-Null; Write-Host '[OK] GhostLock lance avec succes en arriere-plan (Pret 24h/24).' -ForegroundColor Green }"

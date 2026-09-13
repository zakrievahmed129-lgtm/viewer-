# -*- coding: utf-8 -*-
import os
import sys
import winreg

def setup():
    python_exe = r"C:\Users\zakri\AppData\Local\Programs\Python\Python313\pythonw.exe"
    script_path = r"C:\Users\zakri\Desktop\les animations doivent etres incroyables\pc_lock_shield.py"
    script_dir = os.path.dirname(script_path)
    cmd_run = f'"{python_exe}" "{script_path}" --bg'

    # 1. Registre Windows HKCU Run
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "GhostLock_Shield", 0, winreg.REG_SZ, cmd_run)
        winreg.CloseKey(key)
        print("[OK] Registre HKCU Run configuré.")
    except Exception as e:
        print(f"[!] Erreur Registre: {e}")

    # 2. Script VBS silencieux dans Startup
    try:
        appdata = os.environ.get("APPDATA", "")
        startup_dir = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup")
        if os.path.isdir(startup_dir):
            vbs_file = os.path.join(startup_dir, "GhostLockShield.vbs")
            vbs_content = (
                'Set WshShell = CreateObject("WScript.Shell")\r\n'
                f'WshShell.CurrentDirectory = "{script_dir}"\r\n'
                f'WshShell.Run """{python_exe}"" ""{script_path}"" --bg", 0, False\r\n'
            )
            with open(vbs_file, "w", encoding="utf-8") as f:
                f.write(vbs_content)
            print(f"[OK] Lanceur silencieux VBS créé : {vbs_file}")
            
            # Nettoyer l'ancien raccourci GhostLock.lnk si obsolète
            old_lnk = os.path.join(startup_dir, "GhostLock.lnk")
            if os.path.isfile(old_lnk):
                try:
                    os.remove(old_lnk)
                    print("[OK] Ancien raccourci GhostLock.lnk nettoyé.")
                except Exception:
                    pass
    except Exception as e:
        print(f"[!] Erreur Startup VBS: {e}")

if __name__ == "__main__":
    setup()

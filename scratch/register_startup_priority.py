import winreg
import os
import win32com.client

pythonw_path = r"C:\Users\zakri\AppData\Local\Programs\Python\Python313\pythonw.exe"
script_path = r"c:\Users\zakri\Desktop\les animations doivent etres incroyables\pc_lock_shield.py"
cmd_value = f'"{pythonw_path}" "{script_path}" --lock'

print("=== ENREGISTREMENT DU DÉMARRAGE PRIORITAIRE GHOSTLOCK ===")

# 1. Clé de Registre Run (Lancée avant le dossier Démarrage)
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "GhostLock_Priority", 0, winreg.REG_SZ, cmd_value)
    winreg.CloseKey(key)
    print("[OK] Clé HKCU\\...\\Run 'GhostLock_Priority' enregistrée avec succès !")
    print("     Valeur :", cmd_value)
except Exception as e:
    print("[!] Erreur registre HKCU Run :", e)

# 2. Mise à jour des raccourcis Startup (Zakri et Hadij) avec le flag --lock
shell = win32com.client.Dispatch("WScript.Shell")
shortcuts = [
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\GhostLock.lnk"),
    r"C:\Users\hadij\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\GhostLock.lnk"
]

for sc_path in shortcuts:
    try:
        sc = shell.CreateShortcut(sc_path)
        sc.TargetPath = pythonw_path
        sc.Arguments = f'"{script_path}" --lock'
        sc.WorkingDirectory = os.path.dirname(script_path)
        sc.Description = "GhostLock Biometric Shield 24/7 (Lock at Startup)"
        sc.Save()
        print(f"[OK] Raccourci de secours mis à jour avec --lock : {sc_path}")
    except Exception as e:
        print(f"[!] Erreur sur {sc_path} :", e)

import os
import sys

startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
os.makedirs(startup_dir, exist_ok=True)
vbs_path = os.path.join(startup_dir, "GhostLockShield.vbs")

pc_lock_py = os.path.abspath("pc_lock_shield.py")
pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(pythonw_exe):
    pythonw_exe = "pythonw.exe"

vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{os.path.dirname(pc_lock_py)}"
WshShell.Run Chr(34) & "{pythonw_exe}" & Chr(34) & " " & Chr(34) & "{pc_lock_py}" & Chr(34), 0, False
'''

with open(vbs_path, "w", encoding="utf-8") as f:
    f.write(vbs_content)

print(f"[OK] Fichier VBS créé avec succès dans Startup : {vbs_path}")
print("Contenu :")
print(vbs_content)

import win32com.client
import os

shortcut_path = r"C:\Users\hadij\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\GhostLock.lnk"
desktop_shortcut = r"C:\Users\hadij\Desktop\ghost_script.lnk"

shell = win32com.client.Dispatch("WScript.Shell")

print("=== VERIFICATION HADIJ STARTUP SHORTCUT ===")
if os.path.exists(shortcut_path):
    s = shell.CreateShortcut(shortcut_path)
    print(f"[OK] Raccourci de demarrage trouve : {shortcut_path}")
    print(f"     - TargetPath : {s.TargetPath} (Existe : {os.path.exists(s.TargetPath)})")
    print(f"     - Arguments  : {s.Arguments}")
    clean_arg = s.Arguments.strip(' "')
    print(f"     - Cible script existe : {os.path.exists(clean_arg)}")
    print(f"     - WorkingDir : {s.WorkingDirectory} (Existe : {os.path.exists(s.WorkingDirectory)})")
else:
    print(f"[ERREUR] Le raccourci {shortcut_path} n'existe pas !")

print("\n=== VERIFICATION HADIJ DESKTOP GHOST SCRIPT ===")
if os.path.exists(desktop_shortcut):
    s2 = shell.CreateShortcut(desktop_shortcut)
    print(f"[OK] Raccourci bureau trouve : {desktop_shortcut}")
    print(f"     - TargetPath : {s2.TargetPath} (Existe : {os.path.exists(s2.TargetPath)})")
    print(f"     - WorkingDir : {s2.WorkingDirectory} (Existe : {os.path.exists(s2.WorkingDirectory)})")
else:
    print(f"[INFO] Aucun raccourci bureau ghost_script sur hadij.")

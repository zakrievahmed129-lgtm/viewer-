import subprocess
import os

pythonw = r"C:\Users\zakri\AppData\Local\Programs\Python\Python313\pythonw.exe"
script = r"c:\Users\zakri\Desktop\les animations doivent etres incroyables\pc_lock_shield.py"
target_cmd = f'"{pythonw}" "{script}" --lock'

print("=== CONFIGURATION DE LA TÂCHE PRIORITAIRE GHOSTLOCK (ADMIN SANS UAC) ===")

# 1. Tâche pour l'utilisateur zakri
cmd_zakri = [
    'schtasks', '/create',
    '/tn', 'GhostLock_Priority_Zakri',
    '/tr', target_cmd,
    '/sc', 'onlogon',
    '/ru', 'zakri',
    '/rl', 'highest',
    '/f'
]
res1 = subprocess.run(cmd_zakri, capture_output=True, text=True, errors='ignore')
print("Zakri Task ReturnCode:", res1.returncode)
print("Zakri Stdout:", res1.stdout.strip())
if res1.stderr:
    print("Zakri Stderr:", res1.stderr.strip())

# 2. Tâche pour l'utilisateur hadij
cmd_hadij = [
    'schtasks', '/create',
    '/tn', 'GhostLock_Priority_Hadij',
    '/tr', target_cmd,
    '/sc', 'onlogon',
    '/ru', 'hadij',
    '/rl', 'highest',
    '/f'
]
res2 = subprocess.run(cmd_hadij, capture_output=True, text=True, errors='ignore')
print("Hadij Task ReturnCode:", res2.returncode)
print("Hadij Stdout:", res2.stdout.strip())
if res2.stderr:
    print("Hadij Stderr:", res2.stderr.strip())

import sys

with open("ghost_script.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

in_class = None
for i, line in enumerate(lines):
    if line.strip().startswith("class "):
        parts = line.strip().split()
        if len(parts) > 1:
            in_class = parts[1].split("(")[0].replace(":", "")
    if line.strip().startswith("def "):
        parts = line.strip().split()
        if len(parts) > 1 and parts[1].startswith("show_troll_window"):
            in_class = "show_troll_window"
            
    l = line.lower()
    if any(w in l for w in ["shadow", "ombre", "#020617"]):
        print(f"Line {i+1} [{in_class}]: {line.strip()[:110]}")

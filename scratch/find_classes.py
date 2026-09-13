import re

with open("ghost_script.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ["CartoonWallOverlay", "CartoonKeysOverlay", "CartoonGhostOverlay", "ElusiveWindowLegsOverlay"]):
        print(f"Found class at {i+1}: {line.strip()[:60]}")

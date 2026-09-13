with open("ghost_script.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

def inspect_range(name, start, end):
    print(f"=== {name} ({start}-{end}) ===")
    for idx in range(start-1, end):
        l = lines[idx].lower()
        if any(term in l for term in ["shadow", "ombre", "ground", "halo"]):
            print(f"{idx+1}: {lines[idx].strip()}")

inspect_range("CartoonWallOverlay", 3727, 3897)
inspect_range("CartoonKeysOverlay", 4742, 5060)
inspect_range("CartoonGhostOverlay", 5061, 5500)
inspect_range("ElusiveWindowLegsOverlay", 6064, 6250)

with open("ghost_script.py", "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        if "toggle_" in line or "elusive_window" in line:
            print(f"{line_num}: {line.strip()[:100]}")

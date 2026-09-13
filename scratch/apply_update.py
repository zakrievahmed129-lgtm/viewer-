import sys
import py_compile
from extract_test import extracted_classes

with open("ghost_script.py", "r", encoding="utf-8") as f:
    orig_code = f.read()

# 1. Prepare block 1: _shake_window_briefly + 8 cartoon overlay classes
shake_def = '''def _shake_window_briefly(hwnd, orig_x, orig_y):
    try:
        for s in [7, -7, 6, -6, 4, -4, 2, -2, 0]:
            ctypes.windll.user32.SetWindowPos(hwnd, 0, orig_x + s, orig_y, 0, 0, 0x0001 | 0x0004 | 0x0010)
            time.sleep(0.02)
    except Exception:
        pass

'''

cartoons_8 = "\n\n".join([
    extracted_classes["CartoonPullerOverlay"],
    extracted_classes["CartoonDrunkOverlay"],
    extracted_classes["CartoonWallOverlay"],
    extracted_classes["CartoonPainterOverlay"],
    extracted_classes["CartoonKeysOverlay"],
    extracted_classes["CartoonGhostOverlay"],
    extracted_classes["CartoonMegaphoneOverlay"],
    extracted_classes["CartoonRotateOverlay"],
])

block1_replacement = shake_def + cartoons_8 + "\n\n"

# 2. Prepare block 2: _ghost_sounds_loop
block2_replacement = '''def _ghost_sounds_loop():
    """
    Poltergeist cartoon interactif plein écran :
    Émet des glissandos sonores spectraux, coordonné avec le fantôme qui hante l'écran.
    """
    global ghost_sounds_active, ghost_state, ghost_overlay_instance
    while ghost_sounds_active:
        time.sleep(random.uniform(2.5, 4.5))
        if not ghost_sounds_active:
            break
        try:
            if ghost_overlay_instance and ghost_overlay_instance.state != "JUMPSCARE":
                ghost_overlay_instance.trigger_booh()
            notes = [random.choice([800, 1100, 1400, 1800]), random.choice([350, 450, 550])]
            if HAS_WINSOUND:
                for f in notes:
                    if not ghost_sounds_active:
                        break
                    winsound.Beep(f, 180)
                    time.sleep(0.05)
        except Exception:
            pass

'''

# 3. Prepare block 3: ElusiveWindowLegsOverlay
block3_replacement = extracted_classes["ElusiveWindowLegsOverlay"] + "\n\n"

# Locate positions in orig_code
pos1 = orig_code.find("class CartoonPullerOverlay:")
pos2 = orig_code.find("def ensure_prank_overlays_started():")

pos3 = orig_code.find("def _ghost_sounds_loop():")
pos4 = orig_code.find("def toggle_ghost_sounds(active):")

pos5 = orig_code.find("class ElusiveWindowLegsOverlay:")
pos6 = orig_code.find("def ensure_legs_overlay_started():")

assert pos1 != -1 and pos2 != -1 and pos3 != -1 and pos4 != -1 and pos5 != -1 and pos6 != -1

# Splice together
new_code = (
    orig_code[:pos1] +
    block1_replacement +
    orig_code[pos2:pos3] +
    block2_replacement +
    orig_code[pos4:pos5] +
    block3_replacement +
    orig_code[pos6:]
)

# Backup original file
with open("ghost_script.py.bak", "w", encoding="utf-8") as bak:
    bak.write(orig_code)

# Write updated file
with open("ghost_script.py", "w", encoding="utf-8") as f:
    f.write(new_code)

print("Applied updates to ghost_script.py successfully!")

# Verify syntax
try:
    py_compile.compile("ghost_script.py", doraise=True)
    print("py_compile PASSED for ghost_script.py with 0 errors!")
except Exception as e:
    print(f"py_compile FAILED: {e}")
    # Restore backup
    with open("ghost_script.py", "w", encoding="utf-8") as f:
        f.write(orig_code)
    sys.exit(1)

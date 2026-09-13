import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("Importing ghost_script...")
import ghost_script

print("Initializing Tkinter root...")
ghost_script.root = ghost_script.tk.Tk()
ghost_script.root.withdraw()

print("Testing ensure_prank_overlays_started...")
ghost_script.ensure_prank_overlays_started()
ghost_script.root.update()

print("Testing toggle_monkey_volume(True)...")
ghost_script.toggle_monkey_volume(True)
for _ in range(25):
    ghost_script.root.update()
    time.sleep(0.04)

print("Overlay visible:", ghost_script.monkey_overlay_instance.visible if ghost_script.monkey_overlay_instance else "None")
print("Frames loaded:", len(ghost_script.monkey_overlay_instance.frames) if ghost_script.monkey_overlay_instance else 0)

print("Testing toggle_monkey_volume(False)...")
ghost_script.toggle_monkey_volume(False)
for _ in range(10):
    ghost_script.root.update()
    time.sleep(0.04)

print("Overlay visible after toggle False:", ghost_script.monkey_overlay_instance.visible if ghost_script.monkey_overlay_instance else "None")

print("Testing destroy_all_cartoon_overlays...")
ghost_script.destroy_all_cartoon_overlays()
ghost_script.root.update()

ghost_script.root.destroy()
print("All tests passed successfully!")

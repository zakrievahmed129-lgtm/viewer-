import sys
sys.path.insert(0, ".")
import tkinter as tk
import ghost_script

root = tk.Tk()
root.withdraw()

print("Testing CartoonPullerOverlay...")
puller = ghost_script.CartoonPullerOverlay(root)
ghost_script.puller_state["active"] = True
ghost_script.puller_state["mx"] = 400
ghost_script.puller_state["my"] = 300
ghost_script.puller_state["dir_x"] = 1.0
ghost_script.puller_state["dir_y"] = 0.0
for _ in range(5):
    puller._draw(250, 150, 400, 300)
print("CartoonPullerOverlay OK")

print("Testing CartoonDrunkOverlay (Drinking phase)...")
drunk = ghost_script.CartoonDrunkOverlay(root)
ghost_script.drunk_state["active"] = True
ghost_script.drunk_state["drinking"] = True
ghost_script.drunk_state["mx"] = 400
ghost_script.drunk_state["my"] = 300
for _ in range(10):
    drunk.phase += 0.2
    drunk._draw(is_drinking=True)
print("CartoonDrunkOverlay Drinking OK")

print("Testing CartoonDrunkOverlay (Drunk phase - no bottle, stars orbiting, head spinning)...")
ghost_script.drunk_state["drinking"] = False
for _ in range(20):
    drunk.phase += 0.2
    drunk._draw(is_drinking=False)
print("CartoonDrunkOverlay Drunk OK")

print("Testing CartoonPainterOverlay...")
painter = ghost_script.CartoonPainterOverlay(root)
ghost_script.painter_state["active"] = True
painter._trigger_throw()
for _ in range(15):
    painter._tick()
print("CartoonPainterOverlay OK")

root.destroy()
print("ALL TESTS PASSED WITH 100% SUCCESS!")

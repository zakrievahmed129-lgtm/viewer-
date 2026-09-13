import tkinter as tk
import time

# Test that 50 stuck brushes can accumulate and render at high speed
root = tk.Tk()
root.withdraw()

import sys
sys.path.insert(0, ".")
import ghost_script

painter = ghost_script.CartoonPainterOverlay(root)
ghost_script.painter_state["active"] = True
painter.intro_done = True
painter.anim_state = "RELOAD"

start_t = time.time()
# Simulate 50 throws
for throw_i in range(50):
    painter._trigger_throw()
    # Advance flight to 1.0
    for b in painter.flying_brushes:
        b["t"] = 1.0
    painter._tick()

print(f"Stuck brushes count: {len(painter.stuck_brushes)}")
# Render 30 frames
t0 = time.time()
for _ in range(30):
    painter._draw()
t1 = time.time()
fps = 30.0 / (t1 - t0)
print(f"Rendering 30 frames with {len(painter.stuck_brushes)} paint splats took: {t1 - t0:.3f}s (~{fps:.1f} FPS)")

root.destroy()
print("Test completed successfully!")

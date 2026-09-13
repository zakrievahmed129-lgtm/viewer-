import tkinter as tk
import math
import time
import ctypes
from ctypes import wintypes

# Win32 Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

def make_clickthrough(hwnd):
    try:
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)
    except Exception as e:
        print("make_clickthrough error:", e)

def test():
    root = tk.Tk()
    root.title("Test Legs Standalone")
    root.geometry("400x300+300+300")
    
    # Overlay window for legs
    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.attributes("-transparentcolor", "#010101")
    overlay.configure(bg="#010101")
    
    w, h = 400, 100
    canvas = tk.Canvas(overlay, width=w, height=h, bg="#010101", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    overlay.update()
    hwnd = ctypes.windll.user32.GetParent(overlay.winfo_id())
    if not hwnd:
        hwnd = overlay.winfo_id()
    make_clickthrough(hwnd)
    
    phase = [0.0]
    running = [True]
    facing = [1] # 1 right, -1 left
    
    def draw_legs(cx, cy, p, is_moving, dir_x):
        canvas.delete("all")
        # Draw 2 legs: left leg (index 0) and right leg (index 1)
        leg_dist = 40 # distance between hips
        for i, offset in enumerate([-leg_dist, leg_dist]):
            leg_phase = p + (math.pi if i == 1 else 0)
            hip_x = cx + offset
            hip_y = cy
            
            if is_moving:
                # Running kinematics
                stride = math.sin(leg_phase) * 35 * dir_x
                lift = abs(math.cos(leg_phase)) * 22
                
                knee_x = hip_x + stride * 0.5 + (dir_x * 8)
                knee_y = hip_y + 25 - lift * 0.4
                
                foot_x = hip_x + stride
                foot_y = hip_y + 55 - lift
            else:
                # Idle stance
                knee_x = hip_x + (offset * 0.2)
                knee_y = hip_y + 25
                foot_x = hip_x + (offset * 0.3)
                foot_y = hip_y + 55
            
            # Draw leg (thick cartoon outline)
            # Thigh
            canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill="#111111", width=12, capstyle=tk.ROUND)
            canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill="#3b82f6", width=8, capstyle=tk.ROUND)
            # Calf
            canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill="#111111", width=10, capstyle=tk.ROUND)
            canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill="#3b82f6", width=6, capstyle=tk.ROUND)
            
            # White sock
            canvas.create_oval(foot_x - 5, foot_y - 8, foot_x + 5, foot_y + 2, fill="#ffffff", outline="#111111", width=2)
            
            # Cartoon red sneaker / shoe
            shoe_dir = dir_x if is_moving else (1 if offset > 0 else -1)
            toe_x = foot_x + (shoe_dir * 18)
            toe_y = foot_y + 4
            heel_x = foot_x - (shoe_dir * 10)
            heel_y = foot_y + 4
            
            # Sneaker body
            canvas.create_polygon(
                heel_x, heel_y - 6,
                foot_x, foot_y - 6,
                toe_x, toe_y - 3,
                toe_x + (shoe_dir * 4), toe_y + 5,
                heel_x - (shoe_dir * 2), heel_y + 5,
                fill="#ef4444", outline="#111111", width=2
            )
            # White sole
            canvas.create_line(heel_x - 3, heel_y + 5, toe_x + 5, toe_y + 5, fill="#ffffff", width=3)
    
    def tick():
        # Keep overlay positioned right under root
        rx = root.winfo_x()
        ry = root.winfo_y()
        rw = root.winfo_width()
        rh = root.winfo_height()
        
        overlay.geometry(f"{rw}x100+{rx}+{ry + rh - 5}")
        
        phase[0] += 0.35
        draw_legs(rw // 2, 5, phase[0], True, facing[0])
        root.after(30, tick)
        
    tick()
    root.after(3000, lambda: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    test()

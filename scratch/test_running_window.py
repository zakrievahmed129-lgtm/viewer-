import tkinter as tk
import math
import time
import ctypes
from ctypes import wintypes
import threading

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

def make_clickthrough(hwnd):
    try:
        ex = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)
    except Exception as e:
        pass

class WindowLegsOverlay:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        
        self.w, self.h = 260, 95
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.win.update()
        hwnd = ctypes.windll.user32.GetParent(self.win.winfo_id()) or self.win.winfo_id()
        make_clickthrough(hwnd)
        
        self.phase = 0.0
        self.is_running = False
        self.facing = 1.0 # 1.0 right, -1.0 left
        self.speed = 0.0
        self.visible = False
        self.dust_particles = [] # [(x, y, radius, alpha)]
        
    def set_visible(self, visible):
        if self.visible != visible:
            self.visible = visible
            if visible:
                self.win.deiconify()
                self.win.lift()
            else:
                self.win.withdraw()
                
    def update_position(self, target_cx, target_bottom, is_moving, dir_x, dir_y, speed):
        if not self.visible:
            self.set_visible(True)
            
        self.is_running = is_moving
        if abs(dir_x) > 0.1:
            self.facing = 1.0 if dir_x > 0 else -1.0
        self.speed = speed
        
        if is_moving:
            self.phase += max(0.25, min(0.65, speed * 0.035))
            # Spawn dust puffs when sprinting
            if len(self.dust_particles) < 6 and (int(self.phase * 3) % 2 == 0):
                puff_x = (self.w // 2) - (self.facing * 35) + (math.sin(self.phase) * 15)
                puff_y = self.h - 12
                self.dust_particles.append([puff_x, puff_y, 4.0, 1.0])
        else:
            self.phase += 0.05 # Idle breathing
            
        x = int(target_cx - (self.w // 2))
        y = int(target_bottom - 6)
        self.win.geometry(f"{self.w}x{self.h}+{x}+{y}")
        self.draw()
        
    def draw(self):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = 5
        
        # 1. Dessiner les nuages de poussière de course cartoon
        new_dust = []
        for d in self.dust_particles:
            dx, dy, dr, da = d
            color = "#888888" if da > 0.5 else "#555555"
            self.canvas.create_oval(dx - dr, dy - dr, dx + dr, dy + dr, fill=color, outline="", width=0)
            dr += 1.2
            da -= 0.18
            if da > 0 and dr < 20:
                new_dust.append([dx, dy, dr, da])
        self.dust_particles = new_dust
        
        # 2. Dessiner les deux jambes cartoon articulées
        leg_spacing = 36
        offsets = [-leg_spacing, leg_spacing]
        
        # Idle breathing offset
        idle_bounce = math.sin(self.phase * 2.5) * 2.0 if not self.is_running else 0.0
        
        for i, offset in enumerate(offsets):
            leg_phase = self.phase + (math.pi if i == 1 else 0)
            hip_x = cx + offset
            hip_y = cy + idle_bounce
            
            if self.is_running:
                # Dynamique de sprint cartoon
                stride_x = math.sin(leg_phase) * 32.0 * self.facing
                lift_y = max(0.0, math.cos(leg_phase)) * 26.0
                
                knee_x = hip_x + (stride_x * 0.55) + (self.facing * 10.0)
                knee_y = hip_y + 28.0 - (lift_y * 0.45)
                
                foot_x = hip_x + stride_x
                foot_y = hip_y + 60.0 - lift_y
                
                shoe_angle = self.facing * (20.0 - math.sin(leg_phase) * 35.0)
            else:
                # Posture debout normale avec léger écartement
                knee_x = hip_x + (offset * 0.15)
                knee_y = hip_y + 28.0
                foot_x = hip_x + (offset * 0.25)
                foot_y = hip_y + 60.0
                shoe_angle = 15.0 if offset > 0 else -15.0
                
            # Dessin de la cuisse (outline noir épais + remplissage bleu jean)
            self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill="#0f172a", width=13, capstyle=tk.ROUND)
            self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill="#3b82f6", width=8, capstyle=tk.ROUND)
            
            # Articulation genou cartoon
            self.canvas.create_oval(knee_x - 5, knee_y - 5, knee_x + 5, knee_y + 5, fill="#1d4ed8", outline="#0f172a", width=2)
            
            # Dessin du mollet
            self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill="#0f172a", width=11, capstyle=tk.ROUND)
            self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill="#3b82f6", width=6, capstyle=tk.ROUND)
            
            # Chaussette blanche
            self.canvas.create_oval(foot_x - 6, foot_y - 7, foot_x + 6, foot_y + 3, fill="#f8fafc", outline="#0f172a", width=2)
            # Rayure rouge sur la chaussette
            self.canvas.create_line(foot_x - 4, foot_y - 2, foot_x + 4, foot_y - 2, fill="#ef4444", width=2)
            
            # Sneaker cartoon rouge vif (forme profilée dynamique)
            shoe_dir = self.facing if self.is_running else (1.0 if offset > 0 else -1.0)
            toe_x = foot_x + (shoe_dir * 22)
            toe_y = foot_y + 6
            heel_x = foot_x - (shoe_dir * 12)
            heel_y = foot_y + 6
            
            # Corps de la chaussure
            self.canvas.create_polygon(
                heel_x, heel_y - 8,
                foot_x, foot_y - 8,
                toe_x - (shoe_dir * 2), toe_y - 5,
                toe_x + (shoe_dir * 3), toe_y + 4,
                heel_x - (shoe_dir * 2), heel_y + 4,
                fill="#dc2626", outline="#0f172a", width=2
            )
            # Semelle blanche épaisse
            self.canvas.create_line(heel_x - (shoe_dir * 2), heel_y + 5, toe_x + (shoe_dir * 4), toe_y + 5, fill="#ffffff", width=4)
            # Lacets / détails
            self.canvas.create_line(foot_x - (shoe_dir * 2), foot_y - 6, foot_x + (shoe_dir * 4), foot_y - 2, fill="#ffffff", width=2)

def main():
    root = tk.Tk()
    root.title("Fenêtre Fuyante avec Jambes")
    root.geometry("340x220+400+300")
    root.configure(bg="#181825")
    
    lbl = tk.Label(root, text="Attrape-moi si tu peux ! 🏃‍♂️", fg="#38bdf8", bg="#181825", font=("Segoe UI", 13, "bold"))
    lbl.pack(pady=40)
    
    overlay = WindowLegsOverlay(root)
    
    def on_tick():
        rx = root.winfo_x()
        ry = root.winfo_y()
        rw = root.winfo_width()
        rh = root.winfo_height()
        
        # Test avec la souris
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        mx, my = pt.x, pt.y
        
        cx = rx + rw // 2
        cy = ry + rh // 2
        
        dist = math.hypot(cx - mx, cy - my)
        is_fleeing = dist < 220
        dir_x = (cx - mx) if is_fleeing else 1.0
        dir_y = (cy - my) if is_fleeing else 0.0
        
        if is_fleeing:
            norm = math.hypot(dir_x, dir_y) or 1.0
            vx = (dir_x / norm) * 12.0
            vy = (dir_y / norm) * 12.0
            new_x = int(rx + vx)
            new_y = int(ry + vy)
            root.geometry(f"+{new_x}+{new_y}")
            overlay.update_position(new_x + rw // 2, new_y + rh, True, dir_x, dir_y, 14.0)
        else:
            overlay.update_position(rx + rw // 2, ry + rh, False, 1.0, 0.0, 0.0)
            
        root.after(25, on_tick)
        
    root.after(100, on_tick)
    root.after(3000, lambda: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    main()

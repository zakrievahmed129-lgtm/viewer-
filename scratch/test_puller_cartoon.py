import tkinter as tk
import math
import time
import ctypes
from ctypes import wintypes
import random

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

class CartoonPullerOverlay:
    """
    Bonhomme cartoon musclé et expressif qui attrape la souris avec une corde
    et tire de toutes ses forces (effort phénoménal : transpiration qui gicle,
    dents serrées, corps penché à 45°, fumée aux pieds et tremblements de tension).
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        
        self.w, self.h = 240, 200
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.win.winfo_id()) or self.win.winfo_id()
        make_clickthrough(hwnd)
        
        self.phase = 0.0
        self.sweat_drops = [] # [(x, y, vx, vy, life)]
        self.dust_puffs = []
        self.strain_text_timer = 0
        self.strain_text = "HNNNGH!"
        self.visible = False
        
    def set_visible(self, visible):
        if self.visible != visible:
            self.visible = visible
            if visible:
                self.win.deiconify()
                self.win.lift()
            else:
                self.win.withdraw()
                
    def update_puller(self, mx, my, pull_dir_x, pull_dir_y, pull_force):
        if not self.visible:
            self.set_visible(True)
            
        self.phase += 0.4
        
        # Positionner le bonhomme en avant de la souris dans la direction où il tire
        norm = math.hypot(pull_dir_x, pull_dir_y) or 1.0
        ndx = pull_dir_x / norm
        ndy = pull_dir_y / norm
        
        # Distance entre la souris et le bonhomme
        dist = 90
        char_screen_x = mx + int(ndx * dist)
        char_screen_y = my + int(ndy * dist)
        
        # Centrer la fenêtre overlay sur la zone souris-bonhomme
        center_x = (mx + char_screen_x) // 2
        center_y = (my + char_screen_y) // 2
        
        wx = center_x - (self.w // 2)
        wy = center_y - (self.h // 2)
        self.win.geometry(f"{self.w}x{self.h}+{wx}+{wy}")
        self.win.lift()
        
        # Coordonnées locales dans le canvas
        local_mx = mx - wx
        local_my = my - wy
        local_cx = char_screen_x - wx
        local_cy = char_screen_y - wy
        
        self._draw(local_mx, local_my, local_cx, local_cy, ndx, ndy, pull_force)
        
    def _draw(self, mx, my, cx, cy, ndx, ndy, force):
        self.canvas.delete("all")
        
        # Orientation horizontale du bonhomme
        facing = 1.0 if ndx >= 0 else -1.0
        
        # 1. Dessin de la corde sous tension extrême (qui vibre)
        shake = math.sin(self.phase * 5.0) * 2.5
        # Corde tendue avec tremblement
        mid_rx = (mx + cx) / 2.0 + (ndy * shake)
        mid_ry = (my + cy) / 2.0 - (ndx * shake)
        
        # Ligne de corde épaisse marron tressée
        self.canvas.create_line(mx, my, mid_rx, mid_ry, cx, cy, fill="#78350f", width=5, capstyle=tk.ROUND)
        self.canvas.create_line(mx, my, mid_rx, mid_ry, cx, cy, fill="#d97706", width=2, capstyle=tk.ROUND)
        
        # Nœud autour de la souris
        self.canvas.create_oval(mx - 6, my - 6, mx + 6, my + 6, fill="#b45309", outline="#451a03", width=2)
        
        # 2. Gouttes de sueur cartoon (effort phénoménal)
        if len(self.sweat_drops) < 8 and random.random() < 0.6:
            head_x = cx + (facing * 5)
            head_y = cy - 25
            self.sweat_drops.append([head_x, head_y, random.uniform(-2, 2) - (facing * 2), random.uniform(-4, -1), 1.0])
            
        new_sweat = []
        for s in self.sweat_drops:
            sx, sy, svx, svy, life = s
            sx += svx
            sy += svy
            svy += 0.35 # Gravité
            life -= 0.08
            if life > 0:
                # Goutte bleue cyan
                self.canvas.create_oval(sx - 3, sy - 4, sx + 3, sy + 4, fill="#38bdf8", outline="#0284c7", width=1)
                new_sweat.append([sx, sy, svx, svy, life])
        self.sweat_drops = new_sweat
        
        # 3. Nuages de poussière sous les pieds qui glissent
        if len(self.dust_puffs) < 6 and random.random() < 0.4:
            feet_x = cx - (facing * 18)
            feet_y = cy + 32
            self.dust_puffs.append([feet_x, feet_y, 4.0, 1.0])
            
        new_dust = []
        for d in self.dust_puffs:
            dx, dy, dr, da = d
            color = "#94a3b8" if da > 0.5 else "#64748b"
            self.canvas.create_oval(dx - dr, dy - dr, dx + dr, dy + dr, fill=color, outline="", width=0)
            dr += 1.2
            da -= 0.16
            if da > 0 and dr < 18:
                new_dust.append([dx, dy, dr, da])
        self.dust_puffs = new_dust
        
        # 4. Dessin du bonhomme cartoon : corps penché en arrière à 45°
        # Tremblement d'effort sur tout le corps
        strain_shake_x = random.uniform(-1.5, 1.5)
        strain_shake_y = random.uniform(-1.5, 1.5)
        bx = cx + strain_shake_x
        by = cy + strain_shake_y
        
        # Jambes ancrées dans le sol (écartées, pliées, en opposition totale)
        hip_x = bx + (facing * 5)
        hip_y = by + 10
        
        # Jambe avant (tendue en résistance)
        knee_front_x = hip_x + (facing * 20)
        knee_front_y = hip_y + 12
        foot_front_x = knee_front_x + (facing * 12)
        foot_front_y = hip_y + 26
        
        # Jambe arrière (pliée, talon ancré)
        knee_back_x = hip_x - (facing * 14)
        knee_back_y = hip_y + 10
        foot_back_x = knee_back_x - (facing * 16)
        foot_back_y = hip_y + 26
        
        # Cuisses & Mollets en pantalon bleu ouvrier
        self.canvas.create_line(hip_x, hip_y, knee_front_x, knee_front_y, fill="#0f172a", width=11, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, knee_front_x, knee_front_y, fill="#2563eb", width=7, capstyle=tk.ROUND)
        self.canvas.create_line(knee_front_x, knee_front_y, foot_front_x, foot_front_y, fill="#0f172a", width=10, capstyle=tk.ROUND)
        self.canvas.create_line(knee_front_x, knee_front_y, foot_front_x, foot_front_y, fill="#2563eb", width=6, capstyle=tk.ROUND)
        
        self.canvas.create_line(hip_x, hip_y, knee_back_x, knee_back_y, fill="#0f172a", width=11, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, knee_back_x, knee_back_y, fill="#1d4ed8", width=7, capstyle=tk.ROUND)
        self.canvas.create_line(knee_back_x, knee_back_y, foot_back_x, foot_back_y, fill="#0f172a", width=10, capstyle=tk.ROUND)
        self.canvas.create_line(knee_back_x, knee_back_y, foot_back_x, foot_back_y, fill="#1d4ed8", width=6, capstyle=tk.ROUND)
        
        # Grosses chaussures de travail cartoon marron
        for fx, fy in [(foot_front_x, foot_front_y), (foot_back_x, foot_back_y)]:
            self.canvas.create_oval(fx - 10, fy - 5, fx + 10, fy + 5, fill="#78350f", outline="#0f172a", width=2)
            
        # Torse penché en arrière (t-shirt rouge serré d'effort)
        shoulder_x = bx + (facing * 18)
        shoulder_y = by - 12
        self.canvas.create_line(hip_x, hip_y, shoulder_x, shoulder_y, fill="#0f172a", width=16, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, shoulder_x, shoulder_y, fill="#dc2626", width=12, capstyle=tk.ROUND)
        
        # Bras musclés qui tirent sur la corde
        # Épaule -> Coude -> Mains agrippées à la corde
        hand_x = cx - (facing * 10)
        hand_y = cy - 4
        elbow_x = (shoulder_x + hand_x) / 2.0 + (facing * 8)
        elbow_y = shoulder_y + 12
        
        # Bras (peau beige)
        self.canvas.create_line(shoulder_x, shoulder_y, elbow_x, elbow_y, fill="#0f172a", width=12, capstyle=tk.ROUND)
        self.canvas.create_line(shoulder_x, shoulder_y, elbow_x, elbow_y, fill="#fed7aa", width=8, capstyle=tk.ROUND)
        self.canvas.create_line(elbow_x, elbow_y, hand_x, hand_y, fill="#0f172a", width=10, capstyle=tk.ROUND)
        self.canvas.create_line(elbow_x, elbow_y, hand_x, hand_y, fill="#fed7aa", width=6, capstyle=tk.ROUND)
        
        # Gants marrons agrippés
        self.canvas.create_oval(hand_x - 6, hand_y - 6, hand_x + 6, hand_y + 6, fill="#92400e", outline="#0f172a", width=2)
        
        # Tête du bonhomme (rouge d'effort avec yeux plissés et dents serrées)
        head_cx = shoulder_x + (facing * 4)
        head_cy = shoulder_y - 18
        
        # Visage rouge d'effort
        self.canvas.create_oval(head_cx - 14, head_cy - 14, head_cx + 14, head_cy + 14, fill="#fca5a5", outline="#991b1b", width=3)
        # Joues cramoisies
        self.canvas.create_oval(head_cx - 10, head_cy + 1, head_cx - 3, head_cy + 7, fill="#ef4444", outline="")
        self.canvas.create_oval(head_cx + 3, head_cy + 1, head_cx + 10, head_cy + 7, fill="#ef4444", outline="")
        
        # Yeux cartoon d'effort phénoménal (plissés en chevrons "> <" ou exorbités)
        eye_y = head_cy - 3
        # Oeil gauche
        self.canvas.create_line(head_cx - 8, eye_y - 3, head_cx - 2, eye_y + 2, fill="#0f172a", width=3)
        self.canvas.create_line(head_cx - 8, eye_y + 3, head_cx - 2, eye_y - 2, fill="#0f172a", width=3)
        # Oeil droit
        self.canvas.create_line(head_cx + 2, eye_y + 2, head_cx + 8, eye_y - 3, fill="#0f172a", width=3)
        self.canvas.create_line(head_cx + 2, eye_y - 2, head_cx + 8, eye_y + 3, fill="#0f172a", width=3)
        
        # Dents serrées de rage / grimace d'effort
        mouth_y = head_cy + 7
        self.canvas.create_rectangle(head_cx - 7, mouth_y - 3, head_cx + 7, mouth_y + 3, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_line(head_cx - 7, mouth_y, head_cx + 7, mouth_y, fill="#0f172a", width=1)
        self.canvas.create_line(head_cx - 2, mouth_y - 3, head_cx - 2, mouth_y + 3, fill="#0f172a", width=1)
        self.canvas.create_line(head_cx + 2, mouth_y - 3, head_cx + 2, mouth_y + 3, fill="#0f172a", width=1)
        
        # Bandeau rouge sur le front
        self.canvas.create_rectangle(head_cx - 13, head_cy - 12, head_cx + 13, head_cy - 6, fill="#b91c1c", outline="#0f172a", width=2)
        
        # Bulle de texte d'effort cartoon (HNNNGH!, OUFFF!, etc.)
        self.strain_text_timer = (self.strain_text_timer + 1) % 40
        if self.strain_text_timer == 1:
            self.strain_text = random.choice(["HNNNGH!", "OUFFF!", "GRRRR!", "TIIIIRE!"])
            
        if self.strain_text_timer < 25:
            bubble_x = head_cx + (facing * 26)
            bubble_y = head_cy - 24
            # Bulle
            self.canvas.create_rectangle(bubble_x - 30, bubble_y - 12, bubble_x + 30, bubble_y + 12, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_text(bubble_x, bubble_y, text=self.strain_text, fill="#713f12", font=("Impact", 10, "bold"))

def main():
    root = tk.Tk()
    root.withdraw()
    overlay = CartoonPullerOverlay(root)
    
    def loop():
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        mx, my = pt.x, pt.y
        
        # Simuler un tirage vers le bas à droite
        overlay.update_puller(mx, my, 1.0, 0.5, 12.0)
        root.after(20, loop)
        
    root.after(50, loop)
    root.after(3500, lambda: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    main()

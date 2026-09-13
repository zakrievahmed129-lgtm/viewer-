import tkinter as tk
import math
import time
import ctypes
from ctypes import wintypes

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

class CartoonWallOverlay:
    """
    Mur de briques cartoon vivant avec de grands yeux expressifs qui suivent le curseur,
    des sourcils mobiles, un sourire malicieux et des effets d'impact cartoon 'BONK!'
    lorsque la souris tente de franchir la limite.
    """
    def __init__(self, master, wall_x=None):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        
        try:
            self.sw = ctypes.windll.user32.GetSystemMetrics(0)
            self.sh = ctypes.windll.user32.GetSystemMetrics(1)
        except Exception:
            self.sw, self.sh = 1920, 1080
            
        self.wall_x = wall_x if wall_x is not None else (self.sw // 2)
        self.wall_w = 70
        
        # Positionner la fenêtre sur toute la hauteur autour du mur
        self.win.geometry(f"{self.wall_w + 60}x{self.sh}+{self.wall_x - self.wall_w}+{0}")
        
        self.canvas = tk.Canvas(self.win, width=self.wall_w + 60, height=self.sh, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.win.winfo_id()) or self.win.winfo_id()
        make_clickthrough(hwnd)
        
        self.bonk_timer = 0
        self.bonk_y = self.sh // 2
        self.visible = True
        
    def update_wall(self, mx, my, is_bonking=False):
        if is_bonking:
            self.bonk_timer = 15 # 15 frames d'impact
            self.bonk_y = my
            
        self.canvas.delete("all")
        
        # 1. Dessiner le mur de briques cartoon stylisé
        bw = self.wall_w
        bh = 32
        rows = (self.sh // bh) + 2
        
        # Base du mur : briques rouges/orangées cartoon avec biseautage
        for r in range(rows):
            by = r * bh
            # Décalage une rangée sur deux
            offset_x = (r % 2) * (bw // 2)
            
            # Brique principale
            self.canvas.create_rectangle(
                0, by, bw, by + bh,
                fill="#b91c1c", outline="#450a0a", width=3
            )
            # Reflet brique (haut)
            self.canvas.create_line(3, by + 3, bw - 3, by + 3, fill="#ef4444", width=2)
            # Ombre brique (bas)
            self.canvas.create_line(3, by + bh - 2, bw - 3, by + bh - 2, fill="#7f1d1d", width=2)
            # Joint vertical
            jv = (bw // 2 + offset_x) % bw
            self.canvas.create_line(jv, by, jv, by + bh, fill="#450a0a", width=3)
            
        # 2. Dessiner le visage cartoon du mur centré près de la position Y de la souris
        # On contraint la position Y du visage pour qu'il suive la souris en douceur
        face_y = max(100, min(self.sh - 100, my))
        face_cx = bw // 2
        
        # Contour du visage / panneau intégré dans le mur
        self.canvas.create_oval(face_cx - 30, face_y - 45, face_cx + 30, face_y + 45, fill="#991b1b", outline="#450a0a", width=3)
        
        # Grands yeux cartoon
        eye_radius_x = 13
        eye_radius_y = 17
        left_eye_cx = face_cx - 14
        right_eye_cx = face_cx + 14
        eyes_cy = face_y - 12
        
        # Blancs des yeux
        self.canvas.create_oval(left_eye_cx - eye_radius_x, eyes_cy - eye_radius_y, left_eye_cx + eye_radius_x, eyes_cy + eye_radius_y, fill="#ffffff", outline="#0f172a", width=3)
        self.canvas.create_oval(right_eye_cx - eye_radius_x, eyes_cy - eye_radius_y, right_eye_cx + eye_radius_x, eyes_cy + eye_radius_y, fill="#ffffff", outline="#0f172a", width=3)
        
        # Pupilles qui suivent le curseur
        # Calcul de l'angle vers la souris
        dx = mx - self.wall_x
        dy = my - eyes_cy
        angle = math.atan2(dy, dx)
        pupil_dist = min(7.0, math.hypot(dx, dy) * 0.05)
        
        px_l = left_eye_cx + math.cos(angle) * pupil_dist
        py_l = eyes_cy + math.sin(angle) * pupil_dist
        px_r = right_eye_cx + math.cos(angle) * pupil_dist
        py_r = eyes_cy + math.sin(angle) * pupil_dist
        
        # Pupilles noires avec reflet blanc cartoon
        self.canvas.create_oval(px_l - 5, py_l - 6, px_l + 5, py_l + 6, fill="#0f172a", outline="")
        self.canvas.create_oval(px_l - 2, py_l - 4, px_l + 2, py_l, fill="#ffffff", outline="")
        
        self.canvas.create_oval(px_r - 5, py_r - 6, px_r + 5, py_r + 6, fill="#0f172a", outline="")
        self.canvas.create_oval(px_r - 2, py_r - 4, px_r + 2, py_r, fill="#ffffff", outline="")
        
        # Sourcils expressifs (froncés / moqueurs)
        if self.bonk_timer > 0:
            # Yeux plissés / sourcils énervés à l'impact
            self.canvas.create_line(left_eye_cx - 14, eyes_cy - 22, left_eye_cx + 10, eyes_cy - 16, fill="#0f172a", width=5, capstyle=tk.ROUND)
            self.canvas.create_line(right_eye_cx - 10, eyes_cy - 16, right_eye_cx + 14, eyes_cy - 22, fill="#0f172a", width=5, capstyle=tk.ROUND)
        else:
            # Sourcils malicieux confiants
            self.canvas.create_line(left_eye_cx - 12, eyes_cy - 18, left_eye_cx + 12, eyes_cy - 21, fill="#0f172a", width=4, capstyle=tk.ROUND)
            self.canvas.create_line(right_eye_cx - 12, eyes_cy - 21, right_eye_cx + 12, eyes_cy - 18, fill="#0f172a", width=4, capstyle=tk.ROUND)
            
        # Bouche cartoon (sourire moqueur avec dents)
        mouth_y = face_y + 18
        if self.bonk_timer > 0:
            # Dents serrées à l'impact
            self.canvas.create_rectangle(face_cx - 18, mouth_y - 6, face_cx + 18, mouth_y + 6, fill="#ffffff", outline="#0f172a", width=3)
            self.canvas.create_line(face_cx - 18, mouth_y, face_cx + 18, mouth_y, fill="#0f172a", width=2)
            for lx in range(-12, 13, 6):
                self.canvas.create_line(face_cx + lx, mouth_y - 6, face_cx + lx, mouth_y + 6, fill="#0f172a", width=2)
        else:
            # Grand sourire malicieux
            self.canvas.create_arc(face_cx - 20, mouth_y - 12, face_cx + 20, mouth_y + 14, start=0, extent=-180, fill="#7f1d1d", outline="#0f172a", width=3)
            # Dents blanches en haut
            self.canvas.create_rectangle(face_cx - 12, mouth_y, face_cx + 12, mouth_y + 5, fill="#ffffff", outline="#0f172a", width=1)
            
        # 3. Effet d'impact cartoon 'BONK!' si la souris tape dans le mur
        if self.bonk_timer > 0:
            scale = self.bonk_timer / 15.0
            by = self.bonk_y
            # Étoile d'impact jaune/orange
            pts = [
                (bw + 10, by - 25), (bw + 25, by - 12), (bw + 40, by - 22),
                (bw + 30, by), (bw + 48, by + 10), (bw + 26, by + 18),
                (bw + 32, by + 32), (bw + 15, by + 22), (bw + 5, by + 30),
                (bw + 10, by + 10), (bw - 5, by), (bw + 12, by - 10)
            ]
            self.canvas.create_polygon(pts, fill="#facc15", outline="#ea580c", width=3)
            # Texte cartoon 'BONK!'
            self.canvas.create_text(bw + 25, by + 2, text="BONK!", fill="#b91c1c", font=("Impact", int(14 + scale * 4), "bold"))
            self.bonk_timer -= 1

def main():
    root = tk.Tk()
    root.withdraw()
    overlay = CartoonWallOverlay(root)
    
    def loop():
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        mx, my = pt.x, pt.y
        
        # Test de collision
        is_bonk = False
        if mx > overlay.wall_x - 5:
            is_bonk = True
            ctypes.windll.user32.SetCursorPos(overlay.wall_x - 5, my)
            
        overlay.update_wall(mx, my, is_bonk)
        root.after(20, loop)
        
    root.after(50, loop)
    root.after(3500, lambda: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    main()

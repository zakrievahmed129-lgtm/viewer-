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

class CartoonDrunkOverlay:
    """
    Animation de souris ivre :
    1. Introduction : Bouteille d'alcool cartoon qui s'incline pour faire boire la souris (GLOU GLOU 🍾).
    2. En continu : La souris vacille de façon instable, avec joues roses, étoiles de vertige en orbite,
       bulles de hoquet (HIC ! 💫) et spirales cartoon.
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
        self.intro_timer = 0.0 # Temps passé dans la séquence de boisson (0 à 2.8s)
        self.hiccup_bubbles = [] # [(x, y, vy, text, life)]
        self.liquid_drops = [] # [(x, y, vx, vy, life)]
        self.visible = False
        
    def reset_intro(self):
        self.intro_timer = 0.0
        self.liquid_drops.clear()
        self.hiccup_bubbles.clear()
        
    def set_visible(self, visible):
        if self.visible != visible:
            self.visible = visible
            if visible:
                self.win.deiconify()
                self.win.lift()
            else:
                self.win.withdraw()
                
    def update_drunk(self, mx, my):
        if not self.visible:
            self.set_visible(True)
            
        self.phase += 0.12
        self.intro_timer += 0.03
        
        # Centrer la fenêtre autour du curseur
        wx = mx - (self.w // 2)
        wy = my - (self.h // 2)
        self.win.geometry(f"{self.w}x{self.h}+{wx}+{wy}")
        self.win.lift()
        
        local_mx = self.w // 2
        local_my = self.h // 2
        
        self._draw(local_mx, local_my)
        
    def _draw(self, cx, cy):
        self.canvas.delete("all")
        
        is_drinking = (self.intro_timer < 2.6)
        
        # 1. PHASE DE DÉGUSTATION D'ALCOOL (Intro)
        if is_drinking:
            progress = min(1.0, self.intro_timer / 2.6)
            
            # Bouteille d'alcool verte cartoon avec étiquette jaune et bouchon
            # La bouteille descend et s'incline vers le curseur
            tilt_angle = math.radians(min(65.0, progress * 85.0))
            bottle_cx = cx + 55 - (progress * 15)
            bottle_cy = cy - 45 + (math.sin(self.phase * 3.0) * 4)
            
            # Dessin de la bouteille inclinée
            # Corps de la bouteille
            cos_a = math.cos(tilt_angle)
            sin_a = math.sin(tilt_angle)
            
            def rot(px, py):
                return (bottle_cx + px * cos_a - py * sin_a, bottle_cy + px * sin_a + py * cos_a)
                
            p1 = rot(-16, -30)
            p2 = rot(16, -30)
            p3 = rot(16, 25)
            p4 = rot(-16, 25)
            self.canvas.create_polygon([p1, p2, p3, p4], fill="#15803d", outline="#052e16", width=3)
            
            # Étiquette de vin/liqueur
            ep1 = rot(-14, -10)
            ep2 = rot(14, -10)
            ep3 = rot(14, 15)
            ep4 = rot(-14, 15)
            self.canvas.create_polygon([ep1, ep2, ep3, ep4], fill="#fef08a", outline="#ca8a04", width=2)
            lbl_pt = rot(0, 2)
            self.canvas.create_text(lbl_pt[0], lbl_pt[1], text="XXX", fill="#713f12", font=("Impact", 8, "bold"))
            
            # Goulot de la bouteille
            g1 = rot(-6, 25)
            g2 = rot(6, 25)
            g3 = rot(6, 48)
            g4 = rot(-6, 48)
            self.canvas.create_polygon([g1, g2, g3, g4], fill="#166534", outline="#052e16", width=2)
            
            # Jet / Gouttes de liquide qui coulent vers le curseur
            neck_end = rot(0, 48)
            if progress > 0.3:
                # Filet de liquide doré/ambre qui coule vers le curseur
                self.canvas.create_line(neck_end[0], neck_end[1], cx + 2, cy - 2, fill="#f59e0b", width=5, capstyle=tk.ROUND)
                self.canvas.create_line(neck_end[0], neck_end[1], cx + 2, cy - 2, fill="#fef08a", width=2, capstyle=tk.ROUND)
                
                # Gouttes qui giclent
                if random.random() < 0.5 and len(self.liquid_drops) < 8:
                    self.liquid_drops.append([cx + random.uniform(-6, 6), cy + random.uniform(-4, 4), random.uniform(-1.5, 1.5), random.uniform(-3, -0.5), 1.0])
                    
            # Texte cartoon GLOU GLOU !
            glou_x = bottle_cx + 25
            glou_y = bottle_cy - 25
            self.canvas.create_rectangle(glou_x - 36, glou_y - 12, glou_x + 36, glou_y + 12, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_text(glou_x, glou_y, text="GLOU GLOU!", fill="#713f12", font=("Impact", 9, "bold"))
            
        else:
            # 2. PHASE SOURIS TOTALEMENT IVRE (Vacillement, étoiles et hoquets)
            
            # Étoiles de vertige cartoon dorées qui orbitent autour du curseur
            num_stars = 3
            for s_idx in range(num_stars):
                orbit_angle = self.phase * 2.2 + (s_idx * (2.0 * math.pi / num_stars))
                orbit_r = 28.0 + math.sin(self.phase * 3.0 + s_idx) * 6.0
                star_x = cx + math.cos(orbit_angle) * orbit_r
                star_y = cy - 8 + math.sin(orbit_angle) * (orbit_r * 0.45)
                
                # Étoile 4 branches cartoon
                sr = 6.0
                pts = [
                    (star_x, star_y - sr), (star_x + sr * 0.35, star_y - sr * 0.35),
                    (star_x + sr, star_y), (star_x + sr * 0.35, star_y + sr * 0.35),
                    (star_x, star_y + sr), (star_x - sr * 0.35, star_y + sr * 0.35),
                    (star_x - sr, star_y), (star_x - sr * 0.35, star_y - sr * 0.35)
                ]
                self.canvas.create_polygon(pts, fill="#facc15", outline="#ca8a04", width=1.5)
                
            # Joues roses d'ivresse sur le curseur
            self.canvas.create_oval(cx - 15, cy - 2, cx - 5, cy + 6, fill="#f43f5e", outline="")
            self.canvas.create_oval(cx + 5, cy - 2, cx + 15, cy + 6, fill="#f43f5e", outline="")
            
            # Spirale de vertige cartoon au-dessus
            sp_y = cy - 28 + (math.sin(self.phase * 2.0) * 4.0)
            self.canvas.create_arc(cx - 12, sp_y - 10, cx + 12, sp_y + 10, start=0, extent=240, style="arc", outline="#e11d48", width=3)
            self.canvas.create_arc(cx - 7, sp_y - 6, cx + 7, sp_y + 6, start=120, extent=240, style="arc", outline="#f43f5e", width=2)
            
            # Bulles de hoquet (HIC! 💫)
            if random.random() < 0.06 and len(self.hiccup_bubbles) < 3:
                txt = random.choice(["*HIC !*", "HUUUP !", "*BURP !*", "~hic~ 💫"])
                self.hiccup_bubbles.append([cx + random.uniform(-20, 20), cy - 20, -1.2, txt, 1.0])
                
        # Animation des bulles de hoquet
        new_bubbles = []
        for b in self.hiccup_bubbles:
            bx, by, bvy, btxt, blife = b
            by += bvy
            bx += math.sin(by * 0.1) * 0.8
            blife -= 0.03
            if blife > 0:
                self.canvas.create_rectangle(bx - 26, by - 10, bx + 26, by + 10, fill="#fef08a", outline="#ca8a04", width=1.5)
                self.canvas.create_text(bx, by, text=btxt, fill="#713f12", font=("Impact", 9, "bold"))
                new_bubbles.append([bx, by, bvy, btxt, blife])
        self.hiccup_bubbles = new_bubbles
        
        # Animation des gouttes de boisson
        new_drops = []
        for d in self.liquid_drops:
            dx, dy, dvx, dvy, dlife = d
            dx += dvx
            dy += dvy
            dvy += 0.25
            dlife -= 0.08
            if dlife > 0:
                self.canvas.create_oval(dx - 3, dy - 3, dx + 3, dy + 3, fill="#f59e0b", outline="#b45309", width=1)
                new_drops.append([dx, dy, dvx, dvy, dlife])
        self.liquid_drops = new_drops

def main():
    root = tk.Tk()
    root.withdraw()
    overlay = CartoonDrunkOverlay(root)
    overlay.reset_intro()
    
    def loop():
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        mx, my = pt.x, pt.y
        overlay.update_drunk(mx, my)
        root.after(20, loop)
        
    root.after(50, loop)
    root.after(4000, lambda: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    main()

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

class CartoonPainterOverlay:
    """
    Bonhomme cartoon farceur qui sort à moitié de l'écran (en bas),
    rigole et balance des pinceaux et des seaux de peinture sur l'écran
    en créant des éclaboussures cartoon colorées, épaisses et dégoulinantes (SPLAT !).
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        try:
            self.sw = ctypes.windll.user32.GetSystemMetrics(0)
            self.sh = ctypes.windll.user32.GetSystemMetrics(1)
        except Exception:
            self.sw, self.sh = 1920, 1080
            
        self.win.geometry(f"{self.sw}x{self.sh}+0+0")
        self.canvas = tk.Canvas(self.win, width=self.sw, height=self.sh, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        try:
            self.win.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.win.winfo_id()) or self.win.winfo_id()
            ex = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(
                hwnd, -20,
                ex | 0x00080000 | 0x00000020 | 0x00000080 | 0x08000000
            )
        except Exception:
            pass
            
        self.phase = 0.0
        self.visible = False
        self._loop_active = True
        
        # Position du bonhomme (en bas de l'écran)
        self.char_x = self.sw // 2 + 150
        self.char_base_y = self.sh
        self.emerge_progress = 0.0 # 0.0 caché, 1.0 sorti à moitié
        self.throw_timer = 0.0
        self.arm_angle = 0.0
        
        # Projectiles en vol (pinceaux lancés)
        self.projectiles = [] # [(x, y, vx, vy, rot, vrot, color)]
        
        # Taches d'éclaboussures de peinture sur l'écran
        self.splats = [] # [{x, y, radius, color, dark_color, drips: [{x, y, len, max_len, speed}], satellites: [...]}]
        
        # Textes 'SPLAT!'
        self.splat_texts = [] # [(x, y, text, life)]
        
        self.colors_palette = [
            ("#ef4444", "#991b1b"), # Rouge vif
            ("#3b82f6", "#1d4ed8"), # Bleu roi
            ("#10b981", "#047857"), # Vert émeraude
            ("#f59e0b", "#b45309"), # Orange / Jaune
            ("#ec4899", "#be185d"), # Rose fluo
            ("#8b5cf6", "#6d28d9"), # Violet électrique
            ("#06b6d4", "#0e7490"), # Cyan
        ]
        
        self._tick()
        
    def _tick(self):
        if not self._loop_active:
            return
        try:
            global painter_state
            is_active = painter_state.get("active", False) if "painter_state" in globals() else True
            
            if is_active:
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    self.emerge_progress = 0.0
                    
                self.phase += 0.15
                self.win.lift()
                
                # Montée progressive du bonhomme hors du bord de l'écran
                if self.emerge_progress < 1.0:
                    self.emerge_progress = min(1.0, self.emerge_progress + 0.05)
                    
                # Cycle de lancer de pinceau
                self.throw_timer += 0.04
                if self.throw_timer > 1.2:
                    self.throw_timer = 0.0
                    self._launch_paintbrush()
                    
                # Mettre à jour les projectiles
                new_proj = []
                for p in self.projectiles:
                    px, py, pvx, pvy, prot, pvrot, pcol = p
                    px += pvx
                    py += pvy
                    pvy += 0.45 # gravité
                    prot += pvrot
                    
                    # Impact quand il atteint son zénith ou sa cible
                    if pvy > 3.0 or py < self.sh * 0.15 or (pvy > 0 and random.random() < 0.08):
                        self._create_splat(px, py, pcol)
                    else:
                        new_proj.append([px, py, pvx, pvy, prot, pvrot, pcol])
                self.projectiles = new_proj
                
                # Mettre à jour les coulures de peinture
                for s in self.splats:
                    for d in s["drips"]:
                        if d["len"] < d["max_len"]:
                            d["len"] += d["speed"]
                            
                # Mettre à jour les textes SPLAT!
                new_texts = []
                for t in self.splat_texts:
                    tx, ty, tstr, tlife = t
                    tlife -= 0.03
                    ty -= 0.5
                    if tlife > 0:
                        new_texts.append([tx, ty, tstr, tlife])
                self.splat_texts = new_texts
                
                self._draw()
            else:
                if self.visible:
                    self.emerge_progress -= 0.08
                    if self.emerge_progress <= 0:
                        self.visible = False
                        self.win.withdraw()
                        self.splats.clear()
                        self.projectiles.clear()
                        self.splat_texts.clear()
                    else:
                        self._draw()
        except Exception:
            pass
            
        if self.master:
            self.master.after(16, self._tick)
            
    def _launch_paintbrush(self):
        # Lancer un pinceau vers une zone aléatoire de l'écran
        start_x = self.char_x - 30
        start_y = self.sh - int(self.emerge_progress * 130)
        
        target_x = random.randint(int(self.sw * 0.1), int(self.sw * 0.85))
        target_y = random.randint(int(self.sh * 0.15), int(self.sh * 0.65))
        
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy) or 1.0
        
        speed = random.uniform(18.0, 24.0)
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed - 6.0
        
        col, dark_col = random.choice(self.colors_palette)
        self.projectiles.append([start_x, start_y, vx, vy, random.uniform(0, 360), random.uniform(-18, 18), (col, dark_col)])
        
    def _create_splat(self, x, y, colors):
        col, dark_col = colors
        radius = random.randint(35, 65)
        
        # Générer des coulures réalistes qui descendent
        drips = []
        num_drips = random.randint(2, 5)
        for _ in range(num_drips):
            offset_x = random.randint(-radius + 8, radius - 8)
            drips.append({
                "x": x + offset_x,
                "y": y + int(math.sqrt(max(0, radius**2 - offset_x**2)) * 0.6),
                "width": random.randint(4, 9),
                "len": 0,
                "max_len": random.randint(30, 110),
                "speed": random.uniform(0.8, 2.2)
            })
            
        # Gouttes satellites autour de la tache
        satellites = []
        for _ in range(random.randint(6, 12)):
            ang = random.uniform(0, 2 * math.pi)
            dist = radius + random.uniform(8, 45)
            satellites.append((x + math.cos(ang) * dist, y + math.sin(ang) * dist, random.randint(3, 8)))
            
        # Forme organique de la tache principale (polygone irrégulier)
        pts = []
        num_pts = 16
        for i in range(num_pts):
            a = i * (2 * math.pi / num_pts)
            r = radius * random.uniform(0.75, 1.25)
            pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
            
        self.splats.append({
            "x": x, "y": y,
            "pts": pts,
            "radius": radius,
            "color": col,
            "dark_color": dark_col,
            "drips": drips,
            "satellites": satellites
        })
        
        # Limiter à 18 taches max pour ne pas saturer
        if len(self.splats) > 18:
            self.splats.pop(0)
            
        txt = random.choice(["SPLAT !", "SPLOUCH !", "PLOUF !", "PAF !"])
        self.splat_texts.append([x + random.uniform(-20, 20), y - radius - 15, txt, 1.0])

    def _draw(self):
        self.canvas.delete("all")
        
        # 1. DESSINER TOUTES LES ÉCLABOUSSURES DE PEINTURE SUR L'ÉCRAN
        for s in self.splats:
            col = s["color"]
            dark_col = s["dark_color"]
            
            # Gouttes satellites
            for sx, sy, sr in s["satellites"]:
                self.canvas.create_oval(sx - sr, sy - sr, sx + sr, sy + sr, fill=col, outline=dark_col, width=2)
                self.canvas.create_oval(sx - sr * 0.4, sy - sr * 0.4, sx + sr * 0.1, sy + sr * 0.1, fill="#ffffff", outline="")
                
            # Coulures verticales qui descendent
            for d in s["drips"]:
                if d["len"] > 0:
                    dw = d["width"]
                    dx = d["x"]
                    dy = d["y"]
                    d_end = dy + d["len"]
                    # Ligne de coulure
                    self.canvas.create_line(dx, dy, dx, d_end, fill=dark_col, width=dw + 3, capstyle=tk.ROUND)
                    self.canvas.create_line(dx, dy, dx, d_end, fill=col, width=dw, capstyle=tk.ROUND)
                    # Goutte au bout de la coulure
                    self.canvas.create_oval(dx - dw, d_end - dw, dx + dw, d_end + dw, fill=col, outline=dark_col, width=2)
                    self.canvas.create_oval(dx - dw * 0.4, d_end - dw * 0.4, dx, d_end, fill="#ffffff", outline="")
                    
            # Tache principale (splat)
            self.canvas.create_polygon(s["pts"], fill=col, outline=dark_col, width=3, smooth=True)
            
            # Reflets brillants cartoon (effet liquide 3D brillant)
            cx, cy, cr = s["x"], s["y"], s["radius"]
            self.canvas.create_arc(cx - cr * 0.6, cy - cr * 0.6, cx + cr * 0.3, cy + cr * 0.3, start=90, extent=70, style="arc", outline="#ffffff", width=4)
            self.canvas.create_oval(cx - cr * 0.2, cy - cr * 0.4, cx - cr * 0.05, cy - cr * 0.25, fill="#ffffff", outline="")
            
        # 2. DESSINER LES TEXTES SPLAT!
        for tx, ty, tstr, tlife in self.splat_texts:
            scale = int(14 + tlife * 6)
            self.canvas.create_text(tx, ty, text=tstr, fill="#fef08a", font=("Impact", scale, "bold"))
            
        # 3. DESSINER LES PINCEAUX EN PLEIN VOL
        for p in self.projectiles:
            px, py, pvx, pvy, prot, pvrot, pcol = p
            col, dark_col = pcol
            
            rad = math.radians(prot)
            cos_r = math.cos(rad)
            sin_r = math.sin(rad)
            
            def p_rot(lx, ly):
                return (px + lx * cos_r - ly * sin_r, py + lx * sin_r + ly * cos_r)
                
            # Manche en bois
            m1 = p_rot(-4, -28)
            m2 = p_rot(4, -28)
            m3 = p_rot(3, 10)
            m4 = p_rot(-3, 10)
            self.canvas.create_polygon([m1, m2, m3, m4], fill="#b45309", outline="#451a03", width=2)
            
            # Bague métallique
            b1 = p_rot(-5, 10)
            b2 = p_rot(5, 10)
            b3 = p_rot(5, 16)
            b4 = p_rot(-5, 16)
            self.canvas.create_polygon([b1, b2, b3, b4], fill="#cbd5e1", outline="#334155", width=2)
            
            # Poils du pinceau gorgés de peinture
            po1 = p_rot(-6, 16)
            po2 = p_rot(6, 16)
            po3 = p_rot(3, 34)
            po4 = p_rot(-3, 34)
            self.canvas.create_polygon([po1, po2, po3, po4], fill=col, outline=dark_col, width=2)
            
            # Gouttes qui s'échappent du pinceau en vol
            gx, gy = p_rot(0, 38)
            self.canvas.create_oval(gx - 3, gy - 3, gx + 3, gy + 3, fill=col, outline="")
            
        # 4. DESSINER LE PETIT BONHOMME PEINTRE CARTOON
        # Il sort à moitié par le bas de l'écran
        visible_h = int(self.emerge_progress * 135)
        if visible_h > 10:
            cx = self.char_x
            cy = self.sh - visible_h + 30
            
            # Bobbing d'excitation
            cx += int(math.sin(self.phase * 3.0) * 3)
            cy += int(math.cos(self.phase * 3.0) * 2)
            
            # Mains qui s'agrippent au bord de l'écran (main gauche)
            edge_hand_x = cx - 55
            edge_hand_y = self.sh - 5
            self.canvas.create_oval(edge_hand_x - 10, edge_hand_y - 8, edge_hand_x + 10, edge_hand_y + 8, fill="#fed7aa", outline="#0f172a", width=2)
            # Taches de peinture sur la main
            self.canvas.create_oval(edge_hand_x - 4, edge_hand_y - 3, edge_hand_x + 2, edge_hand_y + 3, fill="#ef4444", outline="")
            
            # Corps / Buste (T-shirt rayé bleu marine et blanc style marin/artiste)
            torso_top = cy + 25
            torso_bot = self.sh + 10
            self.canvas.create_rectangle(cx - 36, torso_top, cx + 36, torso_bot, fill="#f8fafc", outline="#0f172a", width=3)
            # Rayures marines
            for ry in range(torso_top + 8, torso_bot, 14):
                self.canvas.create_line(cx - 34, ry, cx + 34, ry, fill="#1e3a8a", width=6)
                
            # Salissures de peinture sur le T-shirt
            self.canvas.create_oval(cx - 15, torso_top + 15, cx - 3, torso_top + 25, fill="#10b981", outline="")
            self.canvas.create_oval(cx + 8, torso_top + 20, cx + 22, torso_top + 32, fill="#ec4899", outline="")
            
            # Tête cartoon expressive
            head_y = cy
            self.canvas.create_oval(cx - 32, head_y - 32, cx + 32, head_y + 32, fill="#fed7aa", outline="#0f172a", width=3)
            
            # Cheveux ébouriffés cartoon
            hair_pts = [
                (cx - 30, head_y - 20), (cx - 38, head_y - 35), (cx - 22, head_y - 32),
                (cx - 15, head_y - 45), (cx, head_y - 35), (cx + 18, head_y - 46),
                (cx + 25, head_y - 32), (cx + 38, head_y - 35), (cx + 30, head_y - 20)
            ]
            self.canvas.create_polygon(hair_pts, fill="#78350f", outline="#0f172a", width=2)
            
            # BÉRET D'ARTISTE ROUGE / VIOLET penché sur le côté
            beret_cx = cx + 8
            beret_cy = head_y - 34
            self.canvas.create_oval(beret_cx - 36, beret_cy - 16, beret_cx + 36, beret_cy + 16, fill="#b91c1c", outline="#0f172a", width=3)
            # Petit pompon au sommet du béret
            self.canvas.create_line(beret_cx, beret_cy - 16, beret_cx, beret_cy - 24, fill="#0f172a", width=3)
            self.canvas.create_oval(beret_cx - 3, beret_cy - 27, beret_cx + 3, beret_cy - 21, fill="#b91c1c", outline="#0f172a", width=2)
            
            # Grands yeux cartoon malicieux
            eye_y = head_y - 6
            # Blancs des yeux
            self.canvas.create_oval(cx - 24, eye_y - 12, cx - 4, eye_y + 12, fill="#ffffff", outline="#0f172a", width=2.5)
            self.canvas.create_oval(cx + 4, eye_y - 12, cx + 24, eye_y + 12, fill="#ffffff", outline="#0f172a", width=2.5)
            
            # Pupilles farceuses qui regardent en l'air vers les éclaboussures
            pupil_offset_y = -3
            pupil_offset_x = int(math.sin(self.phase * 2.0) * 3)
            self.canvas.create_oval(cx - 16 + pupil_offset_x, eye_y - 7 + pupil_offset_y, cx - 8 + pupil_offset_x, eye_y + 3 + pupil_offset_y, fill="#0f172a", outline="")
            self.canvas.create_oval(cx - 14 + pupil_offset_x, eye_y - 5 + pupil_offset_y, cx - 11 + pupil_offset_x, eye_y - 2 + pupil_offset_y, fill="#ffffff", outline="")
            
            self.canvas.create_oval(cx + 8 + pupil_offset_x, eye_y - 7 + pupil_offset_y, cx + 16 + pupil_offset_x, eye_y + 3 + pupil_offset_y, fill="#0f172a", outline="")
            self.canvas.create_oval(cx + 10 + pupil_offset_x, eye_y - 5 + pupil_offset_y, cx + 13 + pupil_offset_x, eye_y - 2 + pupil_offset_y, fill="#ffffff", outline="")
            
            # Sourcils malicieux en accent circonflexe
            self.canvas.create_line(cx - 24, eye_y - 16, cx - 6, eye_y - 19, fill="#0f172a", width=3, capstyle=tk.ROUND)
            self.canvas.create_line(cx + 6, eye_y - 19, cx + 24, eye_y - 16, fill="#0f172a", width=3, capstyle=tk.ROUND)
            
            # Nez cartoon rond avec tache de peinture
            self.canvas.create_oval(cx - 6, eye_y + 4, cx + 6, eye_y + 14, fill="#fca5a5", outline="#0f172a", width=2)
            self.canvas.create_oval(cx - 2, eye_y + 6, cx + 3, eye_y + 11, fill="#3b82f6", outline="") # Tache bleue sur le nez
            
            # Grand sourire malicieux avec dents et langue
            mouth_y = head_y + 16
            self.canvas.create_arc(cx - 20, mouth_y - 6, cx + 20, mouth_y + 14, start=0, extent=-180, fill="#7f1d1d", outline="#0f172a", width=2.5)
            # Dents blanches en haut
            self.canvas.create_rectangle(cx - 12, mouth_y, cx + 12, mouth_y + 4, fill="#ffffff", outline="#0f172a", width=1)
            # Langue rose qui dépasse
            self.canvas.create_oval(cx - 6, mouth_y + 3, cx + 6, mouth_y + 10, fill="#fb7185", outline="")
            
            # Bras droit qui balance le pinceau (animation de jet)
            throw_cycle = (self.throw_timer / 1.2) * 2 * math.pi
            arm_wind = math.sin(throw_cycle) * 28
            
            shoulder_rx = cx + 32
            shoulder_ry = torso_top + 8
            hand_rx = shoulder_rx + 25 + arm_wind
            hand_ry = shoulder_ry - 35 - abs(arm_wind * 0.6)
            
            # Bras droit
            self.canvas.create_line(shoulder_rx, shoulder_ry, hand_rx, hand_ry, fill="#0f172a", width=11, capstyle=tk.ROUND)
            self.canvas.create_line(shoulder_rx, shoulder_ry, hand_rx, hand_ry, fill="#fed7aa", width=7, capstyle=tk.ROUND)
            # Main droite
            self.canvas.create_oval(hand_rx - 8, hand_ry - 8, hand_rx + 8, hand_ry + 8, fill="#fed7aa", outline="#0f172a", width=2)
            
            # Pinceau tenu en main (prêt à être lancé)
            if self.throw_timer < 0.6:
                self.canvas.create_line(hand_rx - 6, hand_ry + 18, hand_rx + 14, hand_ry - 25, fill="#b45309", width=4, capstyle=tk.ROUND)
                self.canvas.create_oval(hand_rx + 10, hand_ry - 32, hand_rx + 18, hand_ry - 22, fill="#ef4444", outline="#991b1b", width=2)
                
            # Bulle de rire cartoon : "HEHEHE ! 🎨"
            laugh_bubble_x = cx - 75
            laugh_bubble_y = cy - 45
            self.canvas.create_rectangle(laugh_bubble_x - 36, laugh_bubble_y - 12, laugh_bubble_x + 36, laugh_bubble_y + 12, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_text(laugh_bubble_x, laugh_bubble_y, text="HEHEHE ! 🎨", fill="#713f12", font=("Impact", 10, "bold"))

def main():
    root = tk.Tk()
    root.withdraw()
    overlay = CartoonPainterOverlay(root)
    root.after(4500, lambda: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    main()

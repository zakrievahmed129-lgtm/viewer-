import tkinter as tk
import math
import random

class DrunkMouseTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Drunk Mouse Revamp")
        self.root.geometry("800x600")
        self.root.configure(bg="#0f172a")
        
        self.canvas = tk.Canvas(self.root, width=780, height=580, bg="#020617", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.phase = 0.0
        self.t = 0.0
        self.mx = 390
        self.my = 300
        
        # Bulles d'alcool pétillantes
        self.bubbles = []
        
        self._tick()
        
    def _tick(self):
        self.phase += 0.22
        self.t += 0.04
        
        # Vacillement physique simulé de la souris
        sway_x = math.sin(self.t * 2.2) * 22.0 + math.cos(self.t * 1.1) * 12.0
        sway_y = math.cos(self.t * 1.8) * 16.0 + math.sin(self.t * 0.9) * 8.0
        cur_mx = self.mx + sway_x
        cur_my = self.my + sway_y
        
        self._draw(cur_mx, cur_my)
        self.root.after(20, self._tick)
        
    def _draw(self, mx, my):
        self.canvas.delete("all")
        
        # =====================================================================
        # 1. ORBITE 3D D'ÉTOILES ET TRUCS QUI TOURNENT AUTOUR DE LA TÊTE (ARRIÈRE)
        # =====================================================================
        head_x = mx
        head_y = my - 15
        
        orbit_rx = 42.0
        orbit_ry = 16.0
        star_count = 5
        
        # Dessiner d'abord les objets en arrière-plan (sin(ang) < 0)
        for i in range(star_count):
            ang = self.phase * 1.8 + i * (2 * math.pi / star_count)
            sin_a = math.sin(ang)
            if sin_a < 0:
                sx = head_x + math.cos(ang) * orbit_rx
                sy = head_y + sin_a * orbit_ry
                scale = 0.75 + 0.25 * (sin_a + 1.0) / 2.0
                font_sz = max(8, int(13 * scale))
                sym = "⭐" if i % 2 == 0 else "💫"
                self.canvas.create_text(sx, sy, text=sym, font=("Segoe UI Emoji", font_sz))
                
        # =====================================================================
        # 2. LA SOURIS (CURSEUR FLÈCHE) QUI VACILLE ET QUI BOIT
        # =====================================================================
        # Angle de vacillement de la souris (titubement comique)
        sway_angle = math.sin(self.phase * 1.5) * 26.0 + math.cos(self.phase * 0.7) * 10.0
        sway_rad = math.radians(sway_angle)
        
        # Points du curseur classique orienté selon le vacillement
        # Forme standard de la flèche de souris
        base_pts = [
            (0, 0),       # Pointe
            (0, 28),      # Bord gauche
            (7, 21),      # Coin intérieur gauche
            (14, 32),     # Patte extérieure
            (19, 30),     # Patte bas
            (12, 18),     # Coin intérieur droit
            (21, 18)      # Bord droit
        ]
        
        # Rotation des points autour de la pointe (0, 0)
        rot_pts = []
        cos_r = math.cos(sway_rad)
        sin_r = math.sin(sway_rad)
        for px, py in base_pts:
            rx = mx + (px * cos_r - py * sin_r)
            ry = my + (px * sin_r + py * cos_r)
            rot_pts.append((rx, ry))
            
        # Curseur flèche avec corps blanc nacré et contour noir épais net
        self.canvas.create_polygon(rot_pts, fill="#ffffff", outline="#000000", width=2.5)
        
        # Joues roses / rougeaudes d'ivresse sur le corps du curseur !
        cheek1_x = mx + (5 * cos_r - 14 * sin_r)
        cheek1_y = my + (5 * sin_r + 14 * cos_r)
        self.canvas.create_oval(cheek1_x - 4, cheek1_y - 3, cheek1_x + 4, cheek1_y + 3, fill="#fb7185", outline="")
        
        # Yeux tourbillonnants d'ivresse dessinés sur le curseur
        eye_x = mx + (6 * cos_r - 8 * sin_r)
        eye_y = my + (6 * sin_r + 8 * cos_r)
        self.canvas.create_text(eye_x, eye_y, text="🌀", font=("Segoe UI Emoji", 8))
        
        # =====================================================================
        # 3. LA BOUTEILLE D'ALCOOL SUPER RÉALISTE
        # =====================================================================
        # La bouteille est penchée au-dessus de la pointe de la souris (mx, my)
        # Elle glougloute avec des petits bobs réguliers
        gulp_bob = math.sin(self.phase * 4.0) * 3.5
        bottle_tip_x = mx - 2
        bottle_tip_y = my - 6 + gulp_bob
        
        # Angle de la bouteille inclinée (~ -42°)
        b_ang = math.radians(-44.0 + math.sin(self.phase * 2.0) * 6.0)
        b_cos = math.cos(b_ang)
        b_sin = math.sin(b_ang)
        
        # Dimensions de la bouteille de spiritueux
        b_len = 82.0
        b_w = 26.0
        
        # Base de la bouteille
        b_base_x = bottle_tip_x - b_cos * b_len
        b_base_y = bottle_tip_y - b_sin * b_len
        
        # Normal perpendiculaire
        nx = -b_sin * (b_w / 2.0)
        ny = b_cos * (b_w / 2.0)
        
        # Goulot de la bouteille
        neck_len = 28.0
        neck_w = 11.0
        nnx = -b_sin * (neck_w / 2.0)
        nny = b_cos * (neck_w / 2.0)
        
        neck_base_x = bottle_tip_x - b_cos * neck_len
        neck_base_y = bottle_tip_y - b_sin * neck_len
        
        # --- Verre de la bouteille (corps en verre ambré / vert émeraude fumé) ---
        # 1. Corps principal en verre
        body_pts = [
            (neck_base_x + nx, neck_base_y + ny),
            (b_base_x + nx, b_base_y + ny),
            (b_base_x - nx, b_base_y - ny),
            (neck_base_x - nx, neck_base_y - ny)
        ]
        self.canvas.create_polygon(body_pts, fill="#78350f", outline="#451a03", width=2.5)
        # Cul de bouteille bombé
        self.canvas.create_oval(b_base_x - 14, b_base_y - 14, b_base_x + 14, b_base_y + 14, fill="#451a03", outline="")
        
        # 2. Liquide d'alcool ambré / doré à l'intérieur
        liq_base_x = b_base_x + b_cos * 6
        liq_base_y = b_base_y + b_sin * 6
        liq_pts = [
            (neck_base_x + nx*0.75, neck_base_y + ny*0.75),
            (liq_base_x + nx*0.75, liq_base_y + ny*0.75),
            (liq_base_x - nx*0.75, liq_base_y - ny*0.75),
            (neck_base_x - nx*0.75, neck_base_y - ny*0.75)
        ]
        self.canvas.create_polygon(liq_pts, fill="#d97706", outline="")
        
        # 3. Étiquette réaliste au centre de la bouteille ("WHISKY 80°")
        lbl_cx = (neck_base_x + b_base_x) / 2.0
        lbl_cy = (neck_base_y + b_base_y) / 2.0
        self.canvas.create_oval(lbl_cx - 15, lbl_cy - 12, lbl_cx + 15, lbl_cy + 12, fill="#fef3c7", outline="#92400e", width=1.5)
        self.canvas.create_text(lbl_cx, lbl_cy - 3, text="WHISKY", font=("Impact", 6, "bold"), fill="#78350f")
        self.canvas.create_text(lbl_cx, lbl_cy + 4, text="80° ★", font=("Impact", 6, "bold"), fill="#b45309")
        
        # 4. Goulot en verre
        neck_pts = [
            (bottle_tip_x + nnx, bottle_tip_y + nny),
            (neck_base_x + nnx, neck_base_y + nny),
            (neck_base_x - nnx, neck_base_y - nny),
            (bottle_tip_x - nnx, bottle_tip_y - nny)
        ]
        self.canvas.create_polygon(neck_pts, fill="#92400e", outline="#451a03", width=2)
        # Bague dorée autour du goulot
        collar_x = bottle_tip_x - b_cos * 10
        collar_y = bottle_tip_y - b_sin * 10
        self.canvas.create_line(collar_x + nnx*1.3, collar_y + nny*1.3, collar_x - nnx*1.3, collar_y - nny*1.3, fill="#f59e0b", width=3)
        
        # 5. Reflet spéculaire ultra-réaliste sur le verre (ligne blanche lustrée bombée)
        self.canvas.create_line(
            neck_base_x + nx*0.85, neck_base_y + ny*0.85,
            b_base_x + nx*0.85, b_base_y + ny*0.85,
            fill="#ffffff", width=2.5, capstyle=tk.ROUND
        )
        self.canvas.create_line(
            bottle_tip_x + nnx*0.8, bottle_tip_y + nny*0.8,
            neck_base_x + nnx*0.8, neck_base_y + nny*0.8,
            fill="#ffffff", width=1.5, capstyle=tk.ROUND
        )
        
        # 6. Jet de liqueur et gouttes qui coulent directement sur la pointe du curseur !
        self.canvas.create_line(bottle_tip_x, bottle_tip_y, mx, my, fill="#f59e0b", width=4, capstyle=tk.ROUND)
        self.canvas.create_line(bottle_tip_x, bottle_tip_y, mx, my, fill="#fef08a", width=2, capstyle=tk.ROUND)
        # Éclaboussures d'alcool doré
        for d in range(3):
            dx = mx + math.sin(self.phase * 4.0 + d) * 7.0
            dy = my + math.cos(self.phase * 4.0 + d) * 4.0
            self.canvas.create_oval(dx - 2, dy - 2, dx + 2, dy + 2, fill="#facc15", outline="#b45309", width=1)
            
        # Bulles d'alcool qui s'échappent
        if random.random() < 0.35:
            self.bubbles.append({
                "x": bottle_tip_x + random.uniform(-6, 6),
                "y": bottle_tip_y + random.uniform(-4, 4),
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(-2.0, -0.6),
                "r": random.uniform(2.5, 5.5),
                "life": 1.0
            })
            
        new_b = []
        for b in self.bubbles:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            b["life"] -= 0.05
            if b["life"] > 0:
                self.canvas.create_oval(b["x"] - b["r"], b["y"] - b["r"], b["x"] + b["r"], b["y"] + b["r"], fill="", outline="#fef08a", width=1.5)
                new_b.append(b)
        self.bubbles = new_b
        
        # =====================================================================
        # 4. ORBITE 3D D'ÉTOILES ET TRUCS QUI TOURNENT AUTOUR DE LA TÊTE (AVANT)
        # =====================================================================
        for i in range(star_count):
            ang = self.phase * 1.8 + i * (2 * math.pi / star_count)
            sin_a = math.sin(ang)
            if sin_a >= 0:
                sx = head_x + math.cos(ang) * orbit_rx
                sy = head_y + sin_a * orbit_ry
                scale = 0.75 + 0.25 * (sin_a + 1.0) / 2.0
                font_sz = max(8, int(15 * scale))
                sym = "⭐" if i % 2 == 0 else "💫"
                self.canvas.create_text(sx, sy, text=sym, font=("Segoe UI Emoji", font_sz))
                
        # Bulle comique d'ivresse
        hic_y = head_y - 45 + math.sin(self.phase * 2.0) * 4
        self.canvas.create_text(mx + 38, hic_y, text="*HIC !* 🍾🥴", font=("Impact", 12, "bold"), fill="#f59e0b")

if __name__ == "__main__":
    app = DrunkMouseTest()
    app.root.mainloop()

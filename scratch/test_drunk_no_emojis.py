import tkinter as tk
import math
import random

class TestDrunkNoEmojis:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Drunk Mouse - No Emojis, No Text, Stops Drinking")
        self.root.geometry("600x500")
        self.root.configure(bg="#0f172a")
        
        self.canvas = tk.Canvas(self.root, width=580, height=480, bg="#020617", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.phase = 0.0
        self.t = 0.0
        self.mx = 290
        self.my = 260
        self.bubbles = []
        self.start_time = 0.0
        
        # Bouton pour tester le basculement boit -> ivre
        self.mode = "drunk" # ou "drinking"
        btn_frame = tk.Frame(self.root, bg="#0f172a")
        btn_frame.pack(fill="x", side="bottom")
        tk.Button(btn_frame, text="Mode: Boit (2 sec)", command=self._set_drinking).pack(side="left", padx=10, pady=5)
        tk.Button(btn_frame, text="Mode: Ivre (Sans bouteille, étoiles)", command=self._set_drunk).pack(side="left", padx=10, pady=5)
        
        self._tick()
        
    def _set_drinking(self):
        self.mode = "drinking"
        self.t = 0.0
        
    def _set_drunk(self):
        self.mode = "drunk"
        
    def _tick(self):
        self.phase += 0.18
        self.t += 0.035
        
        if self.mode == "drinking" and self.t > 2.2:
            self.mode = "drunk"
            
        # Déplacement physique de la souris
        if self.mode == "drinking":
            # Boit : petits tremblements sur place
            cur_mx = self.mx + math.sin(self.phase * 8.0) * 1.5
            cur_my = self.my + math.cos(self.phase * 8.0) * 1.5
        else:
            # Ivre : vacillement comique de la souris
            cur_mx = self.mx + math.sin(self.t * 1.5) * 18.0 + math.cos(self.t * 0.7) * 8.0
            cur_my = self.my + math.cos(self.t * 1.3) * 12.0 + math.sin(self.t * 0.8) * 6.0
            
        self._draw(cur_mx, cur_my, is_drinking=(self.mode == "drinking"))
        self.root.after(20, self._tick)
        
    def _draw_star(self, cx, cy, radius, spin):
        pts = []
        r_in = radius * 0.42
        for i in range(10):
            r = radius if i % 2 == 0 else r_in
            ang = spin + i * (math.pi / 5.0) - (math.pi / 2.0)
            pts.append(cx + math.cos(ang) * r)
            pts.append(cy + math.sin(ang) * r)
        # Étoile dorée cartoon nette
        self.canvas.create_polygon(pts, fill="#fbbf24", outline="#b45309", width=1.5)
        # Éclat blanc au centre
        cr = max(1.5, radius * 0.22)
        self.canvas.create_oval(cx - cr, cy - cr, cx + cr, cy + cr, fill="#ffffff", outline="")

    def _draw(self, mx, my, is_drinking=False):
        self.canvas.delete("all")
        
        # Angle de vacillement de la souris
        if is_drinking:
            sway_angle = math.sin(self.phase * 2.5) * 8.0 - 10.0 # Légère inclinaison vers la bouteille
        else:
            # Tête qui tourne et vacillement comique prononcé
            sway_angle = math.sin(self.phase * 1.8) * 34.0 + math.cos(self.phase * 0.8) * 14.0
            
        sway_rad = math.radians(sway_angle)
        cos_r = math.cos(sway_rad)
        sin_r = math.sin(sway_rad)
        
        # Position de la "tête" du curseur
        head_x = mx + (6 * cos_r - 10 * sin_r)
        head_y = my + (6 * sin_r + 10 * cos_r)
        
        # =====================================================================
        # 1. ÉTOILES 3D QUI TOURNENT AUTOUR DE LA TÊTE (ARRIÈRE-PLAN)
        # =====================================================================
        star_count = 5
        orbit_rx = 38.0
        orbit_ry = 13.0
        
        if not is_drinking:
            for i in range(star_count):
                ang = self.phase * 1.6 + i * (2.0 * math.pi / star_count)
                sin_a = math.sin(ang)
                if sin_a < 0:
                    cos_a = math.cos(ang)
                    sx = head_x + cos_a * orbit_rx
                    sy = head_y + sin_a * orbit_ry - 12.0
                    scale = 0.70 + 0.30 * (sin_a + 1.0) / 2.0
                    spin = self.phase * 2.5 + i
                    self._draw_star(sx, sy, 8.0 * scale, spin)
                    
        # =====================================================================
        # 2. LA SOURIS (CURSEUR FLÈCHE) AVEC SA TÊTE QUI TOURNE
        # =====================================================================
        base_pts = [
            (0, 0),       # Pointe
            (0, 28),      # Bord gauche
            (7, 21),      # Coin intérieur gauche
            (14, 32),     # Patte extérieure
            (19, 30),     # Patte bas
            (12, 18),     # Coin intérieur droit
            (21, 18)      # Bord droit
        ]
        
        rot_pts = []
        for px, py in base_pts:
            rx = mx + (px * cos_r - py * sin_r)
            ry = my + (px * sin_r + py * cos_r)
            rot_pts.append((rx, ry))
            
        # Corps du curseur flèche blanc à contour noir net
        self.canvas.create_polygon(rot_pts, fill="#ffffff", outline="#000000", width=2.5)
        
        # Joues rouges d'ébriété
        cheek_x = mx + (6 * cos_r - 18 * sin_r)
        cheek_y = my + (6 * sin_r + 18 * cos_r)
        self.canvas.create_oval(cheek_x - 5, cheek_y - 4, cheek_x + 5, cheek_y + 4, fill="#fb7185", outline="")
        
        # Yeux de la souris
        if is_drinking:
            # Yeux fermés de délectation pendant qu'elle boit (petits arcs heureux)
            for ox in [3, 9]:
                ex = mx + (ox * cos_r - 10 * sin_r)
                ey = my + (ox * sin_r + 10 * cos_r)
                self.canvas.create_arc(ex - 3, ey - 3, ex + 3, ey + 3, start=0, extent=180, style="arc", outline="#000000", width=2)
        else:
            # YEUX EN SPIRALE HYPNOTIQUE VECTORIELLE (SA TÊTE QUI TOURNE !)
            # Spirale vectorielle animée qui tourne en continu
            for ox in [3, 9]:
                ex = mx + (ox * cos_r - 10 * sin_r)
                ey = my + (ox * sin_r + 10 * cos_r)
                pts_sp = []
                for deg in range(0, 480, 40):
                    rad = math.radians(deg + self.phase * 220)
                    r = 0.5 + (deg / 480.0) * 3.2
                    pts_sp.append((ex + math.cos(rad) * r, ey + math.sin(rad) * r))
                for idx in range(len(pts_sp) - 1):
                    self.canvas.create_line(pts_sp[idx][0], pts_sp[idx][1], pts_sp[idx+1][0], pts_sp[idx+1][1], fill="#0f172a", width=1.5)
                    
        # =====================================================================
        # 3. LA BOUTEILLE D'ALCOOL (UNIQUEMENT LORS DE LA PHASE BOISSON !)
        # Quand elle est ivre, LA SOURIS ARRÊTE DE BOIRE (zéro bouteille).
        # =====================================================================
        if is_drinking:
            gulp_bob = math.sin(self.phase * 5.0) * 3.0
            bottle_tip_x = mx - 2
            bottle_tip_y = my - 6 + gulp_bob
            
            b_ang = math.radians(-44.0 + math.sin(self.phase * 2.0) * 5.0)
            b_cos = math.cos(b_ang)
            b_sin = math.sin(b_ang)
            
            b_len = 82.0
            b_w = 26.0
            b_base_x = bottle_tip_x - b_cos * b_len
            b_base_y = bottle_tip_y - b_sin * b_len
            
            nx = -b_sin * (b_w / 2.0)
            ny = b_cos * (b_w / 2.0)
            
            neck_len = 28.0
            neck_w = 11.0
            nnx = -b_sin * (neck_w / 2.0)
            nny = b_cos * (neck_w / 2.0)
            
            neck_base_x = bottle_tip_x - b_cos * neck_len
            neck_base_y = bottle_tip_y - b_sin * neck_len
            
            # Corps en verre ambré
            body_pts = [
                (neck_base_x + nx, neck_base_y + ny),
                (b_base_x + nx, b_base_y + ny),
                (b_base_x - nx, b_base_y - ny),
                (neck_base_x - nx, neck_base_y - ny)
            ]
            self.canvas.create_polygon(body_pts, fill="#78350f", outline="#451a03", width=2.5)
            self.canvas.create_oval(b_base_x - 14, b_base_y - 14, b_base_x + 14, b_base_y + 14, fill="#451a03", outline="")
            
            # Liquide ambré doré
            liq_base_x = b_base_x + b_cos * 6
            liq_base_y = b_base_y + b_sin * 6
            liq_pts = [
                (neck_base_x + nx*0.75, neck_base_y + ny*0.75),
                (liq_base_x + nx*0.75, liq_base_y + ny*0.75),
                (liq_base_x - nx*0.75, liq_base_y - ny*0.75),
                (neck_base_x - nx*0.75, neck_base_y - ny*0.75)
            ]
            self.canvas.create_polygon(liq_pts, fill="#d97706", outline="")
            
            # Étiquette
            lbl_cx = (neck_base_x + b_base_x) / 2.0
            lbl_cy = (neck_base_y + b_base_y) / 2.0
            self.canvas.create_oval(lbl_cx - 15, lbl_cy - 12, lbl_cx + 15, lbl_cy + 12, fill="#fef3c7", outline="#92400e", width=1.5)
            
            # Goulot
            neck_pts = [
                (bottle_tip_x + nnx, bottle_tip_y + nny),
                (neck_base_x + nnx, neck_base_y + nny),
                (neck_base_x - nnx, neck_base_y - nny),
                (bottle_tip_x - nnx, bottle_tip_y - nny)
            ]
            self.canvas.create_polygon(neck_pts, fill="#92400e", outline="#451a03", width=2)
            
            collar_x = bottle_tip_x - b_cos * 10
            collar_y = bottle_tip_y - b_sin * 10
            self.canvas.create_line(collar_x + nnx*1.3, collar_y + nny*1.3, collar_x - nnx*1.3, collar_y - nny*1.3, fill="#f59e0b", width=3)
            
            # Reflets blancs
            self.canvas.create_line(neck_base_x + nx*0.85, neck_base_y + ny*0.85, b_base_x + nx*0.85, b_base_y + ny*0.85, fill="#ffffff", width=2.5, capstyle=tk.ROUND)
            self.canvas.create_line(bottle_tip_x + nnx*0.8, bottle_tip_y + nny*0.8, neck_base_x + nnx*0.8, neck_base_y + nny*0.8, fill="#ffffff", width=1.5, capstyle=tk.ROUND)
            
            # Jet d'alcool dans la pointe
            self.canvas.create_line(bottle_tip_x, bottle_tip_y, mx, my, fill="#f59e0b", width=4, capstyle=tk.ROUND)
            self.canvas.create_line(bottle_tip_x, bottle_tip_y, mx, my, fill="#fef08a", width=2, capstyle=tk.ROUND)
            
            # Gouttes d'éclaboussure
            for d in range(3):
                dx = mx + math.sin(self.phase * 5.0 + d) * 6.0
                dy = my + math.cos(self.phase * 5.0 + d) * 3.5
                self.canvas.create_oval(dx - 2, dy - 2, dx + 2, dy + 2, fill="#facc15", outline="#b45309", width=1)
                
            # Bulles
            if random.random() < 0.35:
                self.bubbles.append({
                    "x": bottle_tip_x + random.uniform(-5, 5),
                    "y": bottle_tip_y + random.uniform(-4, 4),
                    "vx": random.uniform(-1.2, 1.2),
                    "vy": random.uniform(-2.0, -0.6),
                    "r": random.uniform(2.5, 4.5),
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
        # 4. ÉTOILES 3D QUI TOURNENT AUTOUR DE LA TÊTE (PREMIER PLAN)
        # =====================================================================
        if not is_drinking:
            for i in range(star_count):
                ang = self.phase * 1.6 + i * (2.0 * math.pi / star_count)
                sin_a = math.sin(ang)
                if sin_a >= 0:
                    cos_a = math.cos(ang)
                    sx = head_x + cos_a * orbit_rx
                    sy = head_y + sin_a * orbit_ry - 12.0
                    scale = 0.70 + 0.30 * (sin_a + 1.0) / 2.0
                    spin = self.phase * 2.5 + i
                    self._draw_star(sx, sy, 8.0 * scale, spin)

if __name__ == "__main__":
    app = TestDrunkNoEmojis()
    app.root.mainloop()

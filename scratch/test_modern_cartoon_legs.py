import tkinter as tk
import math
import random
import time

class ModernCartoonLegsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Modern Cartoon Legs - Window Runner")
        self.root.geometry("640x480")
        self.root.configure(bg="#0f172a")
        
        self.w, self.h = 400, 150
        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, bg="#020617", highlightthickness=0)
        self.canvas.pack(pady=40)
        
        self.phase = 0.0
        self.is_moving = True
        self.facing = 1.0
        self.speed = 22.0
        self.dust_clouds = []
        self.speed_streaks = []
        
        # Contrôles de test
        ctrl_frame = tk.Frame(self.root, bg="#0f172a")
        ctrl_frame.pack(fill="x", side="bottom", pady=10)
        
        tk.Button(ctrl_frame, text="Course Droite ->", command=lambda: self._set_motion(True, 1.0)).pack(side="left", padx=10)
        tk.Button(ctrl_frame, text="<- Course Gauche", command=lambda: self._set_motion(True, -1.0)).pack(side="left", padx=10)
        tk.Button(ctrl_frame, text="Pause / Attente Impatiente (Idle)", command=lambda: self._set_motion(False, self.facing)).pack(side="left", padx=10)
        
        self._tick()
        
    def _set_motion(self, moving, facing):
        self.is_moving = moving
        self.facing = facing
        
    def _tick(self):
        if self.is_moving:
            self.phase += 0.28
            # Émission de nuages de poussière au sol
            if random.random() < 0.35:
                # Nuage émis vers l'arrière
                cloud_x = (self.w // 2) - self.facing * (35 + random.uniform(5, 25))
                cloud_y = self.h - 18 + random.uniform(-4, 4)
                self.dust_clouds.append({
                    "x": cloud_x, "y": cloud_y,
                    "r": random.uniform(6, 11),
                    "vx": -self.facing * random.uniform(1.2, 3.2),
                    "vy": random.uniform(-1.0, -0.2),
                    "life": 1.0
                })
        else:
            self.phase += 0.08
            
        self._draw()
        self.root.after(20, self._tick)

    def _draw_sneaker(self, fx, fy, facing, angle_deg, is_planted=False, scale=1.0):
        """
        Dessine une sneaker de basket cartoon ultra-détaillée (style Air Jordan / Chuck Taylor).
        Comprend :
        - Semelle épaisse en caoutchouc blanc avec rainures de crampons noires
        - Embout avant arrondi renforcé blanc
        - Tige en toile rouge vif avec découpes noires et col montant
        - Logo étoile cartoon doré sur la cheville
        - Lacet blanc avec boucles et nœud flottant
        - Onde de choc / impact si au sol
        """
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        def rot(px, py):
            # px, py relatifs à la cheville (0, 0)
            # facing inverse les X
            lx = px * facing
            ly = py
            rx = fx + (lx * cos_a - ly * sin_a) * scale
            ry = fy + (lx * sin_a + ly * cos_a) * scale
            return rx, ry
            
        # 1. Chaussette de sport blanche montante avec rayures rétro rouge/bleu
        sock_pts = [rot(-8, -14), rot(7, -14), rot(6, -2), rot(-7, -2)]
        self.canvas.create_polygon(sock_pts, fill="#ffffff", outline="#0f172a", width=2)
        # Rayure rouge et bleue sur la chaussette
        s1a, s1b = rot(-8, -10), rot(7, -10)
        s2a, s2b = rot(-7, -7), rot(6, -7)
        self.canvas.create_line(s1a[0], s1a[1], s1b[0], s1b[1], fill="#ef4444", width=2)
        self.canvas.create_line(s2a[0], s2a[1], s2b[0], s2b[1], fill="#2563eb", width=2)

        # 2. Corps de la sneaker (chaussure haute montante)
        body_pts = [
            rot(-12, -4),   # Haut talon
            rot(6, -4),     # Haut languette
            rot(14, 2),     # Coup-de-pied
            rot(26, 6),     # Dessus orteils
            rot(28, 14),    # Bout avant semelle
            rot(-13, 14),   # Bout arrière semelle
            rot(-14, 4)     # Talon médian
        ]
        self.canvas.create_polygon(body_pts, fill="#dc2626", outline="#0f172a", width=2.5)
        
        # 3. Empiècement noir contrasté de sport à l'arrière
        heel_pts = [rot(-14, 4), rot(-12, -4), rot(-4, -4), rot(-4, 14), rot(-13, 14)]
        self.canvas.create_polygon(heel_pts, fill="#1e293b", outline="#0f172a", width=1.5)

        # 4. Patch logo circulaire avec étoile sur la cheville
        patch_cx, patch_cy = rot(-2, 2)
        pr = 4.5 * scale
        self.canvas.create_oval(patch_cx - pr, patch_cy - pr, patch_cx + pr, patch_cy + pr, fill="#ffffff", outline="#0f172a", width=1.5)
        self.canvas.create_text(patch_cx, patch_cy, text="★", font=("Arial", int(5 * scale), "bold"), fill="#dc2626")

        # 5. Embout en caoutchouc blanc protecteur à l'avant
        toe_pts = [rot(18, 5), rot(26, 6), rot(28, 14), rot(18, 14)]
        self.canvas.create_polygon(toe_pts, fill="#f8fafc", outline="#0f172a", width=2)

        # 6. Semelle épaisse blanche crantée (caoutchouc premium)
        sole_pts = [rot(-13, 11), rot(28, 11), rot(27, 16), rot(-12, 16)]
        self.canvas.create_polygon(sole_pts, fill="#f8fafc", outline="#0f172a", width=2)
        # Ligne de bande noire le long de la semelle (style Converse)
        s_line1, s_line2 = rot(-12, 13.5), rot(27, 13.5)
        self.canvas.create_line(s_line1[0], s_line1[1], s_line2[0], s_line2[1], fill="#0f172a", width=1.5)

        # 7. Lacets blancs croisés et nœud papillon dynamique qui flotte
        for ly in [-1, 2, 5]:
            l1, l2 = rot(3, ly), rot(13, ly + 2)
            self.canvas.create_line(l1[0], l1[1], l2[0], l2[1], fill="#ffffff", width=2)
            
        # Nœud de lacets avec boucles qui volent
        bow_c = rot(6, -3)
        loop1 = rot(2, -9 - math.sin(self.phase * 3.0) * 3)
        loop2 = rot(14, -7 + math.cos(self.phase * 3.0) * 3)
        self.canvas.create_line(bow_c[0], bow_c[1], loop1[0], loop1[1], fill="#ffffff", width=2, capstyle=tk.ROUND)
        self.canvas.create_line(bow_c[0], bow_c[1], loop2[0], loop2[1], fill="#ffffff", width=2, capstyle=tk.ROUND)

    def _draw(self):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = 14
        
        # 0. Support d'accroche cartoon sous la fenêtre (plaque en métal boulonnée / ceinture)
        # Donne l'impression que les jambes sont solidement fixées au bas de la fenêtre
        bracket_w = 120
        bracket_h = 10
        self.canvas.create_rectangle(cx - bracket_w//2, cy - bracket_h, cx + bracket_w//2, cy, fill="#334155", outline="#0f172a", width=2)
        # Rivets argentés
        for rx in [-50, -25, 0, 25, 50]:
            self.canvas.create_oval(cx + rx - 2.5, cy - 7, cx + rx + 2.5, cy - 2, fill="#94a3b8", outline="#0f172a", width=1)
            
        # 1. Poussière cartoon billowing
        new_clouds = []
        for c in self.dust_clouds:
            c["x"] += c["vx"]
            c["y"] += c["vy"]
            c["r"] += 0.8
            c["life"] -= 0.05
            if c["life"] > 0:
                alpha_col = "#e2e8f0" if c["life"] > 0.6 else ("#cbd5e1" if c["life"] > 0.3 else "#94a3b8")
                # Cercle principal de fumée
                r = c["r"]
                self.canvas.create_oval(c["x"] - r, c["y"] - r*0.7, c["x"] + r, c["y"] + r*0.7, fill=alpha_col, outline="")
                # Petit lobe secondaire pour effet cartoon nuage
                self.canvas.create_oval(c["x"] - r*0.5, c["y"] - r*0.9, c["x"] + r*0.3, c["y"] - r*0.2, fill=alpha_col, outline="")
                new_clouds.append(c)
        self.dust_clouds = new_clouds
        
        # 2. Lignes de vitesse aérodynamiques cartoon derrière les jambes
        if self.is_moving:
            for l in range(3):
                streak_y = cy + 45 + l * 20
                streak_start = cx - self.facing * (45 + l * 12)
                streak_len = 35 + math.sin(self.phase * 2.0 + l) * 15
                streak_end = streak_start - self.facing * streak_len
                self.canvas.create_line(streak_start, streak_y, streak_end, streak_y, fill="#94a3b8", width=2, dash=(4, 3))

        # 3. Paramètres cinématiques des jambes
        leg_spacing = 34
        offsets = [-leg_spacing, leg_spacing]
        
        # Déterminer l'ordre de profondeur (la jambe arrière est dessinée en premier)
        # Lors de la course, l'ordre de profondeur alterne
        if self.is_moving:
            # Cycle complet de course cartoon avec cinématique inverse réaliste
            for i in [1, 0]: # 1 = arrière-plan, 0 = premier plan
                leg_idx = i
                offset = offsets[leg_idx]
                leg_phase = self.phase + (math.pi if leg_idx == 1 else 0.0)
                
                # Bobbing vertical naturel de la hanche
                hip_bob = math.sin(self.phase * 2.0) * 4.0
                hip_x = cx + offset * 0.75 + (self.facing * math.sin(self.phase) * 6.0)
                hip_y = cy + hip_bob
                
                # Formule de course cartoon stylisée (High-knee drive, ground strike, push-off)
                # Phase 0 à PI : foulée aérienne (kick avant -> atterrissage)
                # Phase PI à 2PI : propulsion arrière au sol
                sin_p = math.sin(leg_phase)
                cos_p = math.cos(leg_phase)
                
                # foulée horizontale
                stride_x = sin_p * 44.0 * self.facing
                
                # levée verticale (trajectoire ovoïde asymétrique)
                if cos_p > 0:
                    # En l'air : flexion et genou haut
                    lift_y = cos_p * 34.0
                    knee_flex = 18.0
                    foot_angle = -self.facing * (15.0 + cos_p * 30.0) # pied qui pointe vers l'avant/bas
                else:
                    # Au sol : propulsion
                    lift_y = 0.0
                    knee_flex = 4.0
                    foot_angle = self.facing * (abs(cos_p) * 28.0) # talon qui décolle
                    
                knee_x = hip_x + (stride_x * 0.5) + (self.facing * (16.0 - abs(sin_p)*4.0))
                knee_y = hip_y + 36.0 - (lift_y * 0.45)
                
                foot_x = hip_x + stride_x
                foot_y = hip_y + 82.0 - lift_y
                
                # Nuance de couleur selon la profondeur (jambe arrière légèrement assombrie)
                jean_main = "#2563eb" if leg_idx == 0 else "#1d4ed8"
                jean_dark = "#0f172a"
                jean_light = "#60a5fa" if leg_idx == 0 else "#3b82f6"
                
                # Cuisse volumétrique cartoon
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_dark, width=16, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_main, width=11, capstyle=tk.ROUND)
                # Reflet tissu sur la cuisse
                self.canvas.create_line(hip_x + self.facing*2, hip_y + 2, knee_x + self.facing*2, knee_y - 2, fill=jean_light, width=3, capstyle=tk.ROUND)
                
                # Genouillère anatomique renforcée
                self.canvas.create_oval(knee_x - 7, knee_y - 7, knee_x + 7, knee_y + 7, fill=jean_main, outline=jean_dark, width=2)
                self.canvas.create_oval(knee_x - 4, knee_y - 4, knee_x + 2, knee_y + 2, fill=jean_light, outline="")
                
                # Mollet volumétrique cartoon galbé
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_dark, width=13, capstyle=tk.ROUND)
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_main, width=8, capstyle=tk.ROUND)
                
                # Ourlet de jean retroussé
                cuff_dx = self.facing * 3
                self.canvas.create_oval(foot_x - 8 + cuff_dx, foot_y - 8, foot_x + 8 + cuff_dx, foot_y + 1, fill="#93c5fd", outline=jean_dark, width=2)
                
                # Dessin de la sneaker ultra-réaliste
                self._draw_sneaker(foot_x, foot_y, self.facing, foot_angle, is_planted=(lift_y < 2.0), scale=0.95 if leg_idx == 1 else 1.05)
                
        else:
            # POSTURE D'ATTENTE CARTOON (IDLE IMPATIENT & VIBRANT)
            # La fenêtre trépigne d'impatience prête à déguerpir :
            # - La jambe gauche supporte le poids
            # - La jambe droite tapote nerveusement le sol (tap-tap-tap rythmé !)
            # - Petite respiration élastique
            breath = math.sin(self.phase * 3.0) * 2.0
            tap_phase = math.sin(self.phase * 8.0)
            
            for leg_idx in [1, 0]:
                offset = offsets[leg_idx]
                hip_x = cx + offset
                hip_y = cy + breath
                
                if leg_idx == 0:
                    # Jambe avant qui tapote nerveusement le sol
                    is_tapping = tap_phase > 0.3
                    toe_lift = tap_phase * 12.0 if is_tapping else 0.0
                    knee_x = hip_x + (self.facing * 8.0)
                    knee_y = hip_y + 36.0 - (toe_lift * 0.2)
                    foot_x = hip_x + (self.facing * 12.0)
                    foot_y = hip_y + 82.0 - toe_lift
                    foot_angle = -self.facing * (toe_lift * 2.5)
                else:
                    # Jambe arrière solide en appui
                    knee_x = hip_x - (self.facing * 6.0)
                    knee_y = hip_y + 37.0
                    foot_x = hip_x - (self.facing * 8.0)
                    foot_y = hip_y + 82.0
                    foot_angle = self.facing * 5.0
                    
                jean_main = "#2563eb" if leg_idx == 0 else "#1d4ed8"
                jean_dark = "#0f172a"
                jean_light = "#60a5fa" if leg_idx == 0 else "#3b82f6"
                
                # Cuisse
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_dark, width=16, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_main, width=11, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x + self.facing*2, hip_y + 2, knee_x + self.facing*2, knee_y - 2, fill=jean_light, width=3, capstyle=tk.ROUND)
                
                # Genou
                self.canvas.create_oval(knee_x - 7, knee_y - 7, knee_x + 7, knee_y + 7, fill=jean_main, outline=jean_dark, width=2)
                
                # Mollet
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_dark, width=13, capstyle=tk.ROUND)
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_main, width=8, capstyle=tk.ROUND)
                
                # Ourlet
                self.canvas.create_oval(foot_x - 8, foot_y - 8, foot_x + 8, foot_y + 1, fill="#93c5fd", outline=jean_dark, width=2)
                
                # Sneaker
                self._draw_sneaker(foot_x, foot_y, self.facing, foot_angle, is_planted=True, scale=0.95 if leg_idx == 1 else 1.05)

if __name__ == "__main__":
    app = ModernCartoonLegsApp()
    app.root.mainloop()

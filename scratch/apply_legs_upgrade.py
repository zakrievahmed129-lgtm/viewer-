import sys

with open("ghost_script.py", "r", encoding="utf-8") as f:
    content = f.read()

new_legs_class = '''class ElusiveWindowLegsOverlay:
    """
    Jambes cartoon ultra-détaillées sous la fenêtre fuyante :
    - Modèle 2D cartoon riche :
      * Plaque de fixation métallique rivetée sous le cadre inférieur de la fenêtre
      * Cuisses et mollets en jeans bleu athlétique galbé avec coutures, reflets et genouillères
      * Chaussettes montantes de sport blanches à rayures rétro rouge et bleu
      * Grosses sneakers montantes de basket cartoon rouges, blanches et noires (style Air Jordan / All-Star)
      * Semelles épaisses en caoutchouc blanc cranté avec bande noire
      * Écussons étoile sur les chevilles et lacets dynamiques avec nœud papillon flottant
    - Animation de course cinématique avancée :
      * Cycle de sprint biomécanique en 4 phases (impact, flexion amortie, impulsion explosive, genou haut)
      * Poussière cartoon expansée à plusieurs lobes sous les semelles
      * Lignes de vitesse aérodynamiques cartoon projetées en arrière
      * Posture d'attente (idle) dynamique avec trépignement impatient et tapotement de pied
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 320, 125
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        try:
            self.win.update_idletasks()
            self.hwnd = ctypes.windll.user32.GetParent(self.win.winfo_id()) or self.win.winfo_id()
            ex = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(
                self.hwnd, -20,
                ex | 0x00080000 | 0x00000020 | 0x00000080 | 0x08000000
            )
        except Exception:
            self.hwnd = None
            
        self.last_px = None
        self.last_py = None
        self.phase = 0.0
        self.facing = 1.0
        self.visible = False
        self.dust_clouds = []
        self._loop_active = True
        self._tick()
        
    def _tick(self):
        if not self._loop_active:
            return
        try:
            global legs_state
            if legs_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                tcx = legs_state.get("target_cx", 0)
                tbot = legs_state.get("target_bottom", 0)
                is_moving = legs_state.get("is_moving", False)
                dx = legs_state.get("dir_x", 1.0)
                speed = legs_state.get("speed", 0.0)
                
                if abs(dx) > 0.05:
                    self.facing = 1.0 if dx > 0 else -1.0
                    
                if is_moving:
                    self.phase += max(0.24, min(0.38, speed * 0.02))
                    if len(self.dust_clouds) < 10 and (random.random() < 0.38):
                        cloud_x = (self.w // 2) - self.facing * (35 + random.uniform(5, 20))
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
                    
                px = int(tcx - (self.w // 2))
                py = int(tbot - 12)
                if (px, py) != (self.last_px, self.last_py):
                    self.last_px = px
                    self.last_py = py
                    if self.hwnd:
                        ctypes.windll.user32.SetWindowPos(
                            self.hwnd, 0, px, py, 0, 0,
                            0x0001 | 0x0004 | 0x0010
                        )
                    else:
                        self.win.geometry(f"{self.w}x{self.h}+{px}+{py}")
                        
                self._draw(is_moving, speed)
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.dust_clouds.clear()
                    self.last_px = None
                    self.last_py = None
        except Exception:
            pass
            
        if self.master:
            self.master.after(16, self._tick)

    def _draw_sneaker(self, fx, fy, facing, angle_deg, is_planted=False, scale=1.0):
        """Dessine une sneaker de basket cartoon ultra-détaillée."""
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        def rot(px, py):
            lx = px * facing
            ly = py
            rx = fx + (lx * cos_a - ly * sin_a) * scale
            ry = fy + (lx * sin_a + ly * cos_a) * scale
            return rx, ry
            
        # 1. Chaussette montante avec rayures rétro rouge/bleu
        sock_pts = [rot(-8, -14), rot(7, -14), rot(6, -2), rot(-7, -2)]
        self.canvas.create_polygon(sock_pts, fill="#ffffff", outline="#0f172a", width=2)
        s1a, s1b = rot(-8, -10), rot(7, -10)
        s2a, s2b = rot(-7, -7), rot(6, -7)
        self.canvas.create_line(s1a[0], s1a[1], s1b[0], s1b[1], fill="#ef4444", width=2)
        self.canvas.create_line(s2a[0], s2a[1], s2b[0], s2b[1], fill="#2563eb", width=2)

        # 2. Corps de la sneaker (chaussure montante)
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
        self.canvas.create_text(patch_cx, patch_cy, text="★", font=("Arial", max(4, int(5 * scale)), "bold"), fill="#dc2626")

        # 5. Embout en caoutchouc blanc protecteur à l'avant
        toe_pts = [rot(18, 5), rot(26, 6), rot(28, 14), rot(18, 14)]
        self.canvas.create_polygon(toe_pts, fill="#f8fafc", outline="#0f172a", width=2)

        # 6. Semelle épaisse blanche crantée (caoutchouc)
        sole_pts = [rot(-13, 11), rot(28, 11), rot(27, 16), rot(-12, 16)]
        self.canvas.create_polygon(sole_pts, fill="#f8fafc", outline="#0f172a", width=2)
        s_line1, s_line2 = rot(-12, 13.5), rot(27, 13.5)
        self.canvas.create_line(s_line1[0], s_line1[1], s_line2[0], s_line2[1], fill="#0f172a", width=1.5)

        # 7. Lacets blancs croisés et nœud papillon dynamique
        for ly in [-1, 2, 5]:
            l1, l2 = rot(3, ly), rot(13, ly + 2)
            self.canvas.create_line(l1[0], l1[1], l2[0], l2[1], fill="#ffffff", width=2)
            
        bow_c = rot(6, -3)
        loop1 = rot(2, -9 - math.sin(self.phase * 3.0) * 3)
        loop2 = rot(14, -7 + math.cos(self.phase * 3.0) * 3)
        self.canvas.create_line(bow_c[0], bow_c[1], loop1[0], loop1[1], fill="#ffffff", width=2, capstyle=tk.ROUND)
        self.canvas.create_line(bow_c[0], bow_c[1], loop2[0], loop2[1], fill="#ffffff", width=2, capstyle=tk.ROUND)

    def _draw(self, is_moving, speed):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = 12
        
        # 0. Support d'accroche cartoon sous la fenêtre (plaque en métal boulonnée)
        bracket_w = 110
        bracket_h = 8
        self.canvas.create_rectangle(cx - bracket_w//2, cy - bracket_h, cx + bracket_w//2, cy, fill="#334155", outline="#0f172a", width=2)
        for rx in [-44, -22, 0, 22, 44]:
            self.canvas.create_oval(cx + rx - 2, cy - 6, cx + rx + 2, cy - 2, fill="#94a3b8", outline="#0f172a", width=1)
            
        # 1. Nuages de poussière cartoon à lobes
        new_clouds = []
        for c in self.dust_clouds:
            c["x"] += c["vx"]
            c["y"] += c["vy"]
            c["r"] += 0.8
            c["life"] -= 0.06
            if c["life"] > 0:
                alpha_col = "#e2e8f0" if c["life"] > 0.6 else ("#cbd5e1" if c["life"] > 0.3 else "#94a3b8")
                r = c["r"]
                self.canvas.create_oval(c["x"] - r, c["y"] - r*0.7, c["x"] + r, c["y"] + r*0.7, fill=alpha_col, outline="")
                self.canvas.create_oval(c["x"] - r*0.5, c["y"] - r*0.9, c["x"] + r*0.3, c["y"] - r*0.2, fill=alpha_col, outline="")
                new_clouds.append(c)
        self.dust_clouds = new_clouds
        
        # 2. Lignes de vitesse aérodynamiques cartoon
        if is_moving:
            for l in range(3):
                streak_y = cy + 40 + l * 18
                streak_start = cx - self.facing * (45 + l * 10)
                streak_len = 32 + math.sin(self.phase * 2.0 + l) * 14
                streak_end = streak_start - self.facing * streak_len
                self.canvas.create_line(streak_start, streak_y, streak_end, streak_y, fill="#94a3b8", width=2, dash=(4, 3))

        # 3. Jambes cartoon articulées
        leg_spacing = 32
        offsets = [-leg_spacing, leg_spacing]
        
        if is_moving:
            # Cycle complet de course biomécanique cartoon
            for i in [1, 0]: # arrière-plan puis premier plan
                leg_idx = i
                offset = offsets[leg_idx]
                leg_phase = self.phase + (math.pi if leg_idx == 1 else 0.0)
                
                hip_bob = math.sin(self.phase * 2.0) * 3.5
                hip_x = cx + offset * 0.75 + (self.facing * math.sin(self.phase) * 5.0)
                hip_y = cy + hip_bob
                
                sin_p = math.sin(leg_phase)
                cos_p = math.cos(leg_phase)
                
                stride_x = sin_p * 40.0 * self.facing
                
                if cos_p > 0:
                    lift_y = cos_p * 30.0
                    foot_angle = -self.facing * (15.0 + cos_p * 26.0)
                else:
                    lift_y = 0.0
                    foot_angle = self.facing * (abs(cos_p) * 25.0)
                    
                knee_x = hip_x + (stride_x * 0.5) + (self.facing * (14.0 - abs(sin_p)*3.5))
                knee_y = hip_y + 34.0 - (lift_y * 0.45)
                
                foot_x = hip_x + stride_x
                foot_y = hip_y + 76.0 - lift_y
                
                jean_main = "#2563eb" if leg_idx == 0 else "#1d4ed8"
                jean_dark = "#0f172a"
                jean_light = "#60a5fa" if leg_idx == 0 else "#3b82f6"
                
                # Cuisse
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_dark, width=15, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_main, width=10, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x + self.facing*2, hip_y + 2, knee_x + self.facing*2, knee_y - 2, fill=jean_light, width=2.5, capstyle=tk.ROUND)
                
                # Genouillère
                self.canvas.create_oval(knee_x - 6.5, knee_y - 6.5, knee_x + 6.5, knee_y + 6.5, fill=jean_main, outline=jean_dark, width=2)
                self.canvas.create_oval(knee_x - 3.5, knee_y - 3.5, knee_x + 2, knee_y + 2, fill=jean_light, outline="")
                
                # Mollet
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_dark, width=12, capstyle=tk.ROUND)
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_main, width=7.5, capstyle=tk.ROUND)
                
                # Ourlet de jean retroussé
                cuff_dx = self.facing * 3
                self.canvas.create_oval(foot_x - 7.5 + cuff_dx, foot_y - 7, foot_x + 7.5 + cuff_dx, foot_y + 1, fill="#93c5fd", outline=jean_dark, width=2)
                
                # Sneaker
                self._draw_sneaker(foot_x, foot_y, self.facing, foot_angle, is_planted=(lift_y < 2.0), scale=0.95 if leg_idx == 1 else 1.05)
                
        else:
            # Posture d'attente (idle dynamique avec trépignement impatient)
            breath = math.sin(self.phase * 3.0) * 1.8
            tap_phase = math.sin(self.phase * 8.0)
            
            for leg_idx in [1, 0]:
                offset = offsets[leg_idx]
                hip_x = cx + offset
                hip_y = cy + breath
                
                if leg_idx == 0:
                    is_tapping = tap_phase > 0.3
                    toe_lift = tap_phase * 10.0 if is_tapping else 0.0
                    knee_x = hip_x + (self.facing * 7.0)
                    knee_y = hip_y + 34.0 - (toe_lift * 0.2)
                    foot_x = hip_x + (self.facing * 10.0)
                    foot_y = hip_y + 76.0 - toe_lift
                    foot_angle = -self.facing * (toe_lift * 2.5)
                else:
                    knee_x = hip_x - (self.facing * 5.0)
                    knee_y = hip_y + 35.0
                    foot_x = hip_x - (self.facing * 7.0)
                    foot_y = hip_y + 76.0
                    foot_angle = self.facing * 4.0
                    
                jean_main = "#2563eb" if leg_idx == 0 else "#1d4ed8"
                jean_dark = "#0f172a"
                jean_light = "#60a5fa" if leg_idx == 0 else "#3b82f6"
                
                # Cuisse
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_dark, width=15, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_main, width=10, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x + self.facing*2, hip_y + 2, knee_x + self.facing*2, knee_y - 2, fill=jean_light, width=2.5, capstyle=tk.ROUND)
                
                # Genou
                self.canvas.create_oval(knee_x - 6.5, knee_y - 6.5, knee_x + 6.5, knee_y + 6.5, fill=jean_main, outline=jean_dark, width=2)
                
                # Mollet
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_dark, width=12, capstyle=tk.ROUND)
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_main, width=7.5, capstyle=tk.ROUND)
                
                # Ourlet
                self.canvas.create_oval(foot_x - 7.5, foot_y - 7, foot_x + 7.5, foot_y + 1, fill="#93c5fd", outline=jean_dark, width=2)
                
                # Sneaker
                self._draw_sneaker(foot_x, foot_y, self.facing, foot_angle, is_planted=True, scale=0.95 if leg_idx == 1 else 1.05)'''

start_marker = "class ElusiveWindowLegsOverlay:"
end_marker = "def ensure_legs_overlay_started():"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker)

if idx_start != -1 and idx_end != -1:
    content = content[:idx_start] + new_legs_class + "\n\n" + content[idx_end:]
    print("ElusiveWindowLegsOverlay mis à jour avec succès!")
    with open("ghost_script.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("ghost_script.py enregistré!")
else:
    print(f"ERREUR: markers non trouvés idx_start={idx_start}, idx_end={idx_end}")

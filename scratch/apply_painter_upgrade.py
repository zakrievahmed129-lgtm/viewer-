# -*- coding: utf-8 -*-
"""
Mise à jour de CartoonPainterOverlay dans ghost_script.py avec l'animation théâtrale de dessin animé allongée et enrichie :
- 7 étapes de dessin animé classique.
- Jusqu'à 10 pinceaux plantés simultanément avec coulures sous gravité.
"""

import sys
import py_compile

SCRIPT_PATH = "ghost_script.py"

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    content = f.read()

target_start = "class CartoonPainterOverlay:"
idx_start = content.find(target_start)
if idx_start == -1:
    print("ERREUR: Impossible de trouver target_start")
    sys.exit(1)

target_end = "class CartoonKeysOverlay:"
idx_end = content.find(target_end, idx_start)
if idx_end == -1:
    print("ERREUR: Impossible de trouver target_end")
    sys.exit(1)

new_painter_class = '''class CartoonPainterOverlay:
    """
    Peintre cartoon de dessin animé classique (style Looney Tunes / Disney vintage) :
    Animation allongée théâtrale ultra réaliste digne d'un vrai dessin animé :
    1. INSPECT : Vise l'écran avec son pouce levé et ferme un œil d'artiste en jaugeant la composition.
    2. DIP : Trempe son pinceau dans la palette avec émulsion de gouttelettes liquides.
    3. WINDUP : Moulinet olympique à 360° avec buste cambré, poussière au sol et yeux déterminés.
    4. THROW : Coup de fouet balistique brutal avec lignes de vitesse.
    5. FLIGHT : Pinceau 3D en rotation avec traînée de peinture en spirale.
    6. IMPACT : SPLAT laqué 3D, manche planté vibrant avec oscillation harmonique amortie.
    7. DRIPS : Coulures réalistes épaisses sous gravité avec renflement en poire.
    8. CRITIQUE : Petite danse de cabri et commentaire d'artiste passionné avant le pinceau suivant !
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.sw = self.win.winfo_screenwidth()
        self.sh = self.win.winfo_screenheight()
        self.w, self.h = self.sw, self.sh
        self.win.geometry(f"{self.w}x{self.h}+0+0")
        
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
            
        self.phase = 0.0
        self.visible = False
        self._loop_active = True
        
        # Position du peintre (en bas à droite)
        self.base_px = float(self.sw - 180)
        self.base_py = float(self.sh - 135)
        self.px = self.base_px
        self.py = self.base_py
        
        # Machine à états théâtrale de dessin animé
        self.anim_state = "INSPECT"
        self.state_timer = 0
        self.current_color = "#ef4444"
        self.windup_angle = 0.0
        self.speech_text = "Mmh... ce bureau a besoin d'ART ! 🎨"
        self.speech_timer = 60
        
        # Palette de couleurs vives d'artiste
        self.palette_colors = [
            "#ef4444", "#3b82f6", "#f59e0b", "#10b981",
            "#8b5cf6", "#ec4899", "#06b6d4", "#f97316", "#e11d48"
        ]
        
        # Objets animés
        self.flying_brushes = []
        self.stuck_brushes = []
        self.palette_splashes = []
        self.flight_droplets = []
        self.shockwaves = []
        self.comic_texts = []
        self.dust_puffs = []
        
        self._tick()

    def _trigger_new_throw(self):
        """Lance un pinceau avec trajectoire 3D hyperbolique vers l'écran."""
        tx = random.randint(120, self.sw - 220)
        ty = random.randint(90, self.sh - 180)
        
        self.flying_brushes.append({
            "sx": self.px - 35,
            "sy": self.py - 50,
            "tx": tx,
            "ty": ty,
            "color": self.current_color,
            "t": 0.0,
            "speed": random.uniform(0.042, 0.058),
            "rot": random.uniform(0, 360),
            "spin": random.choice([-26.0, 26.0, -32.0, 32.0]),
            "arc": random.uniform(-160, -90)
        })

    def _tick(self):
        if not self._loop_active:
            return
        try:
            global painter_state
            if painter_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                self.phase += 0.12
                self.state_timer += 1
                
                # Respiration et rebond corporel organique
                self.px = self.base_px + math.sin(self.phase * 0.6) * 12
                self.py = self.base_py + math.cos(self.phase * 0.9) * 6
                
                # MACHINE À ÉTATS CINÉMATIQUE DU PEINTRE
                if self.anim_state == "INSPECT":
                    if self.state_timer == 1:
                        self.speech_text = random.choice([
                            "Mmh... quelle horreur ! 🎨",
                            "Ce bureau manque d'inspiration ! ✨",
                            "Un coup de génie s'impose ! 🖌️",
                            "Regardez-moi ce cadrage ! 👀"
                        ])
                        self.speech_timer = 50
                        self.current_color = random.choice(self.palette_colors)
                        
                    if self.state_timer > 55:  # ~1.2 seconde de cadrage
                        self.anim_state = "DIP"
                        self.state_timer = 0
                        
                elif self.anim_state == "DIP":
                    if self.state_timer == 1:
                        self.speech_text = "Une touche de couleur fraîche ! 🧪"
                        self.speech_timer = 40
                        
                    if self.state_timer % 4 == 0:
                        pal_x = self.px - 45
                        pal_y = self.py + 5
                        self.palette_splashes.append({
                            "x": pal_x + random.uniform(-10, 10),
                            "y": pal_y + random.uniform(-8, 8),
                            "vx": random.uniform(-3, 3),
                            "vy": random.uniform(-5, -2),
                            "color": self.current_color,
                            "r": random.uniform(2.5, 4.5),
                            "life": 1.0
                        })
                        
                    if self.state_timer > 45:  # ~1.0 seconde de trempage
                        self.anim_state = "WINDUP"
                        self.state_timer = 0
                        
                elif self.anim_state == "WINDUP":
                    self.windup_angle += 35.0
                    if self.state_timer == 1:
                        self.speech_text = "ATTENTION LES YEUX ! HOOO-ISSE ! 💥"
                        self.speech_timer = 45
                        for _ in range(4):
                            self.dust_puffs.append({
                                "x": self.px + random.uniform(-25, 25),
                                "y": self.py + 38,
                                "r": random.uniform(8, 16),
                                "life": 1.0
                            })
                            
                    if self.state_timer > 40:  # ~0.9 seconde de moulinet héroïque
                        self.anim_state = "THROW"
                        self.state_timer = 0
                        self._trigger_new_throw()
                        
                elif self.anim_state == "THROW":
                    if self.state_timer > 14:
                        self.anim_state = "CELEBRATE"
                        self.state_timer = 0
                        
                elif self.anim_state == "CELEBRATE":
                    if self.state_timer == 1:
                        self.speech_text = random.choice([
                            "MAGNIFIQUE ! QUEL CHEF-D'ŒUVRE ! 🎨✨",
                            "ET BIM ! EN PLEIN DANS LE MILLE ! 💥",
                            "C'EST DE TOUTE BEAUTÉ ! 🖌️",
                            "UN VRAI PICASSO ! HO HO ! 🎭"
                        ])
                        self.speech_timer = 65
                        
                    jump = abs(math.sin(self.state_timer * 0.25)) * 14.0
                    self.py = (self.base_py + math.cos(self.phase * 0.9) * 6) - jump
                    
                    if self.state_timer > 65:  # ~1.4 seconde de réjouissance
                        self.anim_state = "INSPECT"
                        self.state_timer = 0
                        
                # GESTION DES PINCEAUX EN PLEIN VOL
                new_flying = []
                for b in self.flying_brushes:
                    b["t"] += b["speed"]
                    b["rot"] += b["spin"]
                    t = b["t"]
                    
                    cur_x = b["sx"] + (b["tx"] - b["sx"]) * t
                    cur_y = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc"] * t * (1 - t))
                    
                    if random.random() < 0.75:
                        self.flight_droplets.append({
                            "x": cur_x + random.uniform(-8, 8),
                            "y": cur_y + random.uniform(-8, 8),
                            "color": b["color"],
                            "r": random.uniform(3, 5.5),
                            "vy": random.uniform(0.5, 2.5),
                            "life": 1.0
                        })
                        
                    if t >= 1.0:
                        tx = b["tx"]
                        ty = b["ty"]
                        col = b["color"]
                        
                        self.stuck_brushes.append({
                            "x": tx,
                            "y": ty,
                            "color": col,
                            "base_angle": random.uniform(-38, 38),
                            "vib_t": 0.0,
                            "vib_amp": random.uniform(28.0, 42.0),
                            "life": random.uniform(18.0, 30.0),
                            "splat_r": random.uniform(32, 54),
                            "drips": [
                                {
                                    "ox": random.uniform(-14, 14),
                                    "oy": random.uniform(12, 26),
                                    "len": 0.0,
                                    "max_len": random.uniform(80, 280),
                                    "speed": random.uniform(1.4, 3.5),
                                    "width": random.uniform(4.0, 7.5)
                                } for _ in range(random.randint(2, 4))
                            ]
                        })
                        
                        self.shockwaves.append({"x": tx, "y": ty, "r": 15, "max_r": 90, "alpha": 1.0})
                        
                        self.comic_texts.append({
                            "x": tx,
                            "y": ty - 32,
                            "text": random.choice(["💥 TCHAAK !", "🎨 SPLAAT !", "✨ SPLOOSH !", "🖌️ BIM !"]),
                            "color": col,
                            "life": 1.0
                        })
                        
                        if len(self.stuck_brushes) > 10:
                            self.stuck_brushes.pop(0)
                    else:
                        new_flying.append(b)
                self.flying_brushes = new_flying
                
                # MISE À JOUR PARTICULES ET COULURES
                new_pal = []
                for p in self.palette_splashes:
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vy"] += 0.4
                    p["life"] -= 0.06
                    if p["life"] > 0:
                        new_pal.append(p)
                self.palette_splashes = new_pal
                
                new_f_drops = []
                for fd in self.flight_droplets:
                    fd["y"] += fd["vy"]
                    fd["life"] -= 0.04
                    if fd["life"] > 0:
                        new_f_drops.append(fd)
                self.flight_droplets = new_f_drops
                
                new_dust = []
                for du in self.dust_puffs:
                    du["r"] += 0.8
                    du["life"] -= 0.05
                    if du["life"] > 0:
                        new_dust.append(du)
                self.dust_puffs = new_dust
                
                new_shk = []
                for shk in self.shockwaves:
                    shk["r"] += 5.0
                    shk["alpha"] -= 0.06
                    if shk["alpha"] > 0 and shk["r"] < shk["max_r"]:
                        new_shk.append(shk)
                self.shockwaves = new_shk
                
                new_txts = []
                for txt in self.comic_texts:
                    txt["life"] -= 0.035
                    txt["y"] -= 0.7
                    if txt["life"] > 0:
                        new_txts.append(txt)
                self.comic_texts = new_txts
                
                new_stuck = []
                for sb in self.stuck_brushes:
                    sb["life"] -= 0.025
                    sb["vib_t"] += 0.15
                    for dr in sb["drips"]:
                        if dr["len"] < dr["max_len"]:
                            dr["len"] += dr["speed"]
                    if sb["life"] > 0:
                        new_stuck.append(sb)
                self.stuck_brushes = new_stuck
                
                if self.speech_timer > 0:
                    self.speech_timer -= 1
                    
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.flying_brushes.clear()
                    self.stuck_brushes.clear()
                    self.flight_droplets.clear()
                    self.palette_splashes.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        
        # 1. Gouttelettes en vol
        for fd in self.flight_droplets:
            r = fd["r"] * fd["life"]
            self.canvas.create_oval(fd["x"] - r, fd["y"] - r, fd["x"] + r, fd["y"] + r, fill=fd["color"], outline="")
            
        # 2. Éclaboussures de palette
        for p in self.palette_splashes:
            r = p["r"] * p["life"]
            self.canvas.create_oval(p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r, fill=p["color"], outline="")
            
        # 3. Ondes de choc d'impact sur la vitre
        for shk in self.shockwaves:
            r = shk["r"]
            self.canvas.create_oval(shk["x"] - r, shk["y"] - r*0.6, shk["x"] + r, shk["y"] + r*0.6, outline="#ffffff", width=3)
            
        # 4. Coulures et taches 3D des pinceaux plantés
        for sb in self.stuck_brushes:
            sx, sy, scolor = sb["x"], sb["y"], sb["color"]
            sr = sb["splat_r"]
            
            for dr in sb["drips"]:
                dx = sx + dr["ox"]
                dy = sy + dr["oy"]
                dlen = dr["len"]
                dw = dr["width"]
                if dlen > 2:
                    self.canvas.create_line(dx, dy, dx, dy + dlen, fill=scolor, width=int(dw), capstyle=tk.ROUND)
                    gy = dy + dlen
                    self.canvas.create_oval(dx - dw*0.9, gy - dw*0.9, dx + dw*0.9, gy + dw*1.3, fill=scolor, outline="")
                    self.canvas.create_oval(dx - dw*0.35, gy - dw*0.3, dx + dw*0.25, gy + dw*0.4, fill="#ffffff", outline="")
            
            # Énorme tache de peinture 3D bombée
            self.canvas.create_oval(sx - sr - 4, sy - sr - 4, sx + sr + 4, sy + sr + 4, fill="#0f172a", outline="")
            
            pts = []
            for deg in range(0, 360, 20):
                rad = math.radians(deg)
                lobe = 1.0 + 0.42 * math.sin(deg * 3.2) + 0.18 * math.cos(deg * 2.5)
                rr = sr * lobe
                pts.append((sx + math.cos(rad) * rr, sy + math.sin(rad) * rr))
            self.canvas.create_polygon(pts, fill=scolor, outline="", smooth=True)
            
            # Reflet laqué blanc brillant 3D
            self.canvas.create_arc(
                sx - sr * 0.70, sy - sr * 0.70, sx + sr * 0.30, sy + sr * 0.30,
                start=35, extent=100, style="arc", outline="#ffffff", width=max(3, int(sr * 0.12))
            )
            
            # Éclaboussures satellites radiales
            for ed in [20, 65, 115, 160, 215, 260, 310, 345]:
                erad = math.radians(ed)
                dist = sr * 1.65
                ex = sx + math.cos(erad) * dist
                ey = sy + math.sin(erad) * dist
                self.canvas.create_oval(ex - 4, ey - 4, ex + 4, ey + 4, fill=scolor, outline="")
                
        # 5. Manches des pinceaux plantés (AVEC VIBRATION AMORTIE SPECTACULAIRE !)
        for sb in self.stuck_brushes:
            sx, sy, scolor = sb["x"], sb["y"], sb["color"]
            
            vt = sb["vib_t"]
            damping = math.exp(-vt * 3.5)
            vib_angle = sb["vib_amp"] * damping * math.sin(vt * 30.0)
            total_angle = sb["base_angle"] + vib_angle
            rad = math.radians(total_angle - 90)
            
            handle_len = 92.0
            hx2 = sx + math.cos(rad) * handle_len
            hy2 = sy + math.sin(rad) * handle_len
            
            vx1 = sx + math.cos(rad) * 14
            vy1 = sy + math.sin(rad) * 14
            self.canvas.create_line(sx, sy, vx1, vy1, fill=scolor, width=11, capstyle=tk.ROUND)
            
            vx2 = sx + math.cos(rad) * 28
            vy2 = sy + math.sin(rad) * 28
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#94a3b8", width=9)
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#f8fafc", width=3)
            
            self.canvas.create_line(vx2, vy2, hx2, hy2, fill="#b45309", width=7, capstyle=tk.ROUND)
            self.canvas.create_line(vx2 + math.cos(rad)*6, vy2 + math.sin(rad)*6, hx2 - math.cos(rad)*12, hy2 - math.sin(rad)*12, fill="#d97706", width=3)
            self.canvas.create_oval(hx2 - 5, hy2 - 5, hx2 + 5, hy2 + 5, fill="#78350f", outline="")
            
        # 6. Pinceaux en plein vol
        for b in self.flying_brushes:
            t = b["t"]
            bx = b["sx"] + (b["tx"] - b["sx"]) * t
            by = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc"] * t * (1 - t))
            
            scale = 0.45 + 1.0 * t
            rot_rad = math.radians(b["rot"])
            b_len = 78.0 * scale
            
            x_tip = bx - math.cos(rot_rad) * (b_len * 0.4)
            y_tip = by - math.sin(rot_rad) * (b_len * 0.4)
            x_end = bx + math.cos(rot_rad) * (b_len * 0.6)
            y_end = by + math.sin(rot_rad) * (b_len * 0.6)
            
            self.canvas.create_line(bx, by, x_end, y_end, fill="#92400e", width=max(3, int(7 * scale)), capstyle=tk.ROUND)
            v_mid_x = bx - math.cos(rot_rad) * (b_len * 0.15)
            v_mid_y = by - math.sin(rot_rad) * (b_len * 0.15)
            self.canvas.create_line(bx, by, v_mid_x, v_mid_y, fill="#e2e8f0", width=max(4, int(8 * scale)))
            self.canvas.create_line(v_mid_x, v_mid_y, x_tip, y_tip, fill=b["color"], width=max(5, int(10 * scale)), capstyle=tk.ROUND)
            
            tail_x = bx + math.cos(rot_rad) * (b_len * 1.0)
            tail_y = by + math.sin(rot_rad) * (b_len * 1.0)
            self.canvas.create_line(x_end, y_end, tail_x, tail_y, fill="#f8fafc", width=2, dash=(4, 4))
            
        # 7. Textes et étoiles de BD
        for cs in self.comic_texts:
            cx, cy = cs["x"], cs["y"]
            star_pts = []
            for sa_deg in range(0, 360, 30):
                sa = math.radians(sa_deg)
                sr = 25 if (sa_deg // 30) % 2 == 0 else 12
                star_pts.append((cx + math.cos(sa) * sr, cy + math.sin(sa) * sr))
            self.canvas.create_polygon(star_pts, fill="#facc15", outline="#ea580c", width=2)
            self.canvas.create_text(cx, cy, text=cs["text"], font=("Impact", 13, "bold"), fill="#dc2626")
            
        # 8. Poussière cartoon au sol
        for du in self.dust_puffs:
            dr = du["r"]
            self.canvas.create_oval(du["x"] - dr, du["y"] - dr*0.5, du["x"] + dr, du["y"] + dr*0.5, fill="#cbd5e1", outline="")
            
        # 9. Le Personnage du Peintre
        self._draw_theatrical_painter()

    def _draw_theatrical_painter(self):
        px = self.px
        py = self.py
        
        self.canvas.create_oval(px - 42, py + 34, px + 42, py + 48, fill="#0f172a", outline="")
        self.canvas.create_oval(px - 32, py + 28, px - 6, py + 44, fill="#0f172a", outline="")
        self.canvas.create_oval(px + 6, py + 28, px + 32, py + 44, fill="#0f172a", outline="")
        self.canvas.create_rectangle(px - 24, py + 18, px + 24, py + 34, fill="#1e293b", outline="#0f172a", width=2)
        
        self.canvas.create_polygon([
            (px - 22, py - 10), (px + 22, py - 10),
            (px + 26, py + 24), (px - 26, py + 24)
        ], fill="#f1f5f9", outline="#0f172a", width=2)
        self.canvas.create_oval(px - 10, py + 4, px - 4, py + 10, fill="#ef4444", outline="")
        self.canvas.create_oval(px + 8, py + 8, px + 14, py + 14, fill="#3b82f6", outline="")
        self.canvas.create_oval(px - 4, py + 14, px + 2, py + 20, fill="#facc15", outline="")
        
        lean = 0.0
        if self.anim_state == "WINDUP":
            lean = 18.0
        elif self.anim_state == "THROW":
            lean = -16.0
        elif self.anim_state == "INSPECT":
            lean = 6.0
            
        body_x = px + lean * 0.6
        self.canvas.create_oval(body_x - 32, py - 26, body_x + 32, py + 24, fill="#ffffff", outline="#0f172a", width=3)
        for ry in range(-16, 22, 9):
            self.canvas.create_line(body_x - 28, py + ry, body_x + 28, py + ry, fill="#1d4ed8", width=4)
            
        self.canvas.create_polygon([
            (body_x - 16, py - 24), (body_x, py - 18), (body_x + 16, py - 24),
            (body_x + 8, py - 10), (body_x - 8, py - 10)
        ], fill="#dc2626", outline="#7f1d1d", width=1)
        
        pal_x = body_x - 46
        pal_y = py + 4
        self.canvas.create_oval(pal_x - 28, pal_y - 20, pal_x + 28, pal_y + 20, fill="#d97706", outline="#78350f", width=3)
        self.canvas.create_oval(pal_x - 18, pal_y - 7, pal_x - 8, pal_y + 7, fill="#fed7aa", outline="#78350f", width=2)
        for pi, pc in enumerate(["#ef4444", "#3b82f6", "#facc15", "#10b981", "#a855f7"]):
            pdeg = math.radians(pi * 48 - 25)
            self.canvas.create_oval(pal_x + math.cos(pdeg)*16 - 5, pal_y + math.sin(pdeg)*11 - 5,
                                    pal_x + math.cos(pdeg)*16 + 5, pal_y + math.sin(pdeg)*11 + 5,
                                    fill=pc, outline="")
                                    
        arm_start_x = body_x + 22
        arm_start_y = py - 14
        
        if self.anim_state == "INSPECT":
            hand_x = body_x - 18
            hand_y = py - 42
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 8, hand_y - 8, hand_x + 8, hand_y + 8, fill="#fed7aa", outline="#c2410c", width=2)
            self.canvas.create_line(hand_x, hand_y, hand_x, hand_y - 18, fill="#fed7aa", width=6, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y, hand_x - 15, hand_y + 18, fill="#92400e", width=4)
            self.canvas.create_line(hand_x - 15, hand_y + 18, hand_x - 22, hand_y + 26, fill=self.current_color, width=6, capstyle=tk.ROUND)
            
        elif self.anim_state == "DIP":
            hand_x = pal_x + 8
            hand_y = pal_y - 12
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y - 18, hand_x, hand_y + 10, fill="#92400e", width=4)
            self.canvas.create_line(hand_x, hand_y + 10, hand_x, hand_y + 20, fill=self.current_color, width=7, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 6, hand_y - 6, hand_x + 6, hand_y + 6, fill="#fed7aa", outline="#c2410c", width=2)
            
        elif self.anim_state == "WINDUP":
            w_rad = math.radians(self.windup_angle)
            w_len = 55.0
            hand_x = arm_start_x + math.cos(w_rad) * w_len
            hand_y = arm_start_y + math.sin(w_rad) * w_len
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(arm_start_x - w_len, arm_start_y - w_len, arm_start_x + w_len, arm_start_y + w_len, outline="#f8fafc", width=2, dash=(6, 4))
            px2 = hand_x + math.cos(w_rad + math.pi/2) * 32
            py2 = hand_y + math.sin(w_rad + math.pi/2) * 32
            self.canvas.create_line(hand_x, hand_y, px2, py2, fill="#92400e", width=4)
            self.canvas.create_line(px2, py2, px2 + math.cos(w_rad + math.pi/2)*14, py2 + math.sin(w_rad + math.pi/2)*14, fill=self.current_color, width=7, capstyle=tk.ROUND)
            
        elif self.anim_state == "THROW":
            hand_x = body_x - 38
            hand_y = py - 46
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            for offy in [-8, 0, 8]:
                self.canvas.create_line(hand_x, hand_y + offy, hand_x - 45, hand_y + offy - 12, fill="#ffffff", width=3, dash=(4, 4))
                
        elif self.anim_state == "CELEBRATE":
            hand_x = body_x + 28
            hand_y = py - 52
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 6, hand_y - 6, hand_x + 6, hand_y + 6, fill="#fed7aa", outline="#c2410c", width=2)
            
        head_x = body_x
        head_y = py - 44
        self.canvas.create_oval(head_x - 24, head_y - 24, head_x + 24, head_y + 24, fill="#fed7aa", outline="#c2410c", width=2)
        
        beret_tilt = -6 if self.anim_state == "WINDUP" else 0
        self.canvas.create_oval(head_x - 32, head_y - 34 + beret_tilt, head_x + 24, head_y - 14 + beret_tilt, fill="#dc2626", outline="#7f1d1d", width=3)
        self.canvas.create_line(head_x - 5, head_y - 34 + beret_tilt, head_x - 5, head_y - 40 + beret_tilt, fill="#7f1d1d", width=3)
        
        if self.anim_state == "INSPECT":
            self.canvas.create_line(head_x + 4, head_y - 6, head_x + 15, head_y - 6, fill="#0f172a", width=3)
            self.canvas.create_oval(head_x - 17, head_y - 13, head_x - 3, head_y + 3, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 13, head_y - 10, head_x - 7, head_y - 4, fill="#ffffff", outline="")
        elif self.anim_state == "WINDUP":
            self.canvas.create_oval(head_x - 16, head_y - 11, head_x - 4, head_y + 1, fill="#f59e0b", outline="#713f12", width=2)
            self.canvas.create_oval(head_x + 4, head_y - 11, head_x + 16, head_y + 1, fill="#f59e0b", outline="#713f12", width=2)
            self.canvas.create_line(head_x - 10, head_y - 9, head_x - 10, head_y - 1, fill="#0f172a", width=3)
            self.canvas.create_line(head_x + 10, head_y - 9, head_x + 10, head_y - 1, fill="#0f172a", width=3)
        else:
            self.canvas.create_oval(head_x - 16, head_y - 10, head_x - 4, head_y + 2, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x + 4, head_y - 10, head_x + 16, head_y + 2, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 13, head_y - 8, head_x - 8, head_y - 4, fill="#ffffff", outline="")
            self.canvas.create_oval(head_x + 8, head_y - 8, head_x + 13, head_y - 4, fill="#ffffff", outline="")
            
        m_pts = [
            (head_x - 28, head_y + 6), (head_x - 12, head_y + 12),
            (head_x, head_y + 10), (head_x + 12, head_y + 12), (head_x + 28, head_y + 6)
        ]
        self.canvas.create_line(m_pts, fill="#0f172a", width=4, smooth=True)
        self.canvas.create_oval(head_x - 6, head_y - 2, head_x + 6, head_y + 8, fill="#fca5a5", outline="#c2410c", width=1)
        
        if self.speech_timer > 0:
            bx = body_x - 50
            by = py - 95
            self.canvas.create_rectangle(bx - 140, by - 16, bx + 140, by + 16, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_polygon([(bx + 20, by + 16), (bx + 10, by + 28), (bx, by + 16)], fill="#fef08a", outline="#ca8a04", width=1)
            self.canvas.create_text(bx, by, text=self.speech_text, font=("Impact", 11, "bold"), fill="#0f172a")


'''

content = content[:idx_start] + new_painter_class + content[idx_end:]

with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Compilation et validation de {SCRIPT_PATH}...")
py_compile.compile(SCRIPT_PATH, doraise=True)
print("SUCCESS: CartoonPainterOverlay ultra-réaliste et théâtral intégré avec succès !")

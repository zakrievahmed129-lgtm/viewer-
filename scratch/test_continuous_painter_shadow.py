import math
import random
import tkinter as tk
import time

class TestContinuousPainter:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        
        self.sw = 1920
        self.sh = 1080
        self.w, self.h = self.sw, self.sh
        self.win.geometry(f"{self.w}x{self.h}+0+0")
        
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.phase = 0.0
        self.visible = True
        self._loop_active = True
        
        self.base_px = float(self.sw - 190)
        self.base_py = float(self.sh - 145)
        self.px = self.base_px
        self.py = self.base_py
        self.floor_y = self.base_py + 44
        
        self.palette_colors = [
            "#dc2626", # Rouge Cadmium
            "#2563eb", # Bleu Outremer
            "#facc15", # Jaune Chrome
            "#059669", # Vert Émeraude
            "#9333ea", # Violet Impérial
            "#db2777", # Rose Magenta
            "#0891b2", # Cyan Azur
            "#ea580c", # Orange Brûlé
            "#e11d48", # Cramoisi
            "#0d9488"  # Turquoise
        ]
        self.color_index = 0
        self.current_color = self.palette_colors[0]
        
        # INTRO FAITE UNE SEULE FOIS !
        self.intro_done = False
        self.anim_state = "ENTER"
        self.state_timer = 0
        self.windup_angle = 0.0
        self.windup_speed = 14.0
        self.speech_text = "Place au Maestro ! 🎨"
        self.speech_timer = 60
        self.target_x = self.sw // 2
        self.target_y = self.sh // 3
        self.throw_count = 0
        
        self.flying_brushes = []
        self.stuck_brushes = []
        self.palette_splashes = []
        self.flight_droplets = []
        self.shockwaves = []
        self.comic_texts = []
        self.dust_puffs = []
        self.music_notes = []
        self.sweat_drops = []
        self.lightbulb_rays = []

    def _trigger_throw(self):
        tx = random.randint(140, self.sw - 260)
        ty = random.randint(100, self.sh - 220)
        self.target_x = tx
        self.target_y = ty
        self.throw_count += 1
        
        self.flying_brushes.append({
            "sx": self.px - 40,
            "sy": self.py - 60,
            "tx": tx,
            "ty": ty,
            "color": self.current_color,
            "t": 0.0,
            "speed": random.uniform(0.045, 0.065),
            "rot": random.uniform(0, 360),
            "spin": random.choice([-24.0, 24.0, -32.0, 32.0]),
            "arc": random.uniform(-180, -110)
        })

    def tick_frame(self):
        self.phase += 0.12
        self.state_timer += 1
        
        # Respiration subtile
        self.px = self.base_px + math.sin(self.phase * 0.5) * 5
        self.py = self.base_py + math.cos(self.phase * 0.8) * 3
        
        # =========================================================================
        # PHASE D'INTRO (EXÉCUTÉE UNE SEULE FOIS AU DÉPART)
        # =========================================================================
        if not self.intro_done:
            if self.anim_state == "ENTER":
                if self.state_timer == 1:
                    self.speech_text = "Silence dans l'atelier ! Le Maître arrive... 🎨"
                    self.speech_timer = 50
                    self.current_color = self.palette_colors[self.color_index % len(self.palette_colors)]
                step_offset = max(0, 40 - self.state_timer) * 3.5
                self.px += step_offset
                if self.state_timer > 45:
                    self.anim_state = "MEASURE"
                    self.state_timer = 0
                    
            elif self.anim_state == "MEASURE":
                if self.state_timer == 1:
                    self.speech_text = "Mmh... quelle horreur spatiale ! Jaugeons la composition... 📐"
                    self.speech_timer = 55
                tilt = math.sin(self.state_timer * 0.1) * 7
                self.px += tilt
                if self.state_timer > 60:
                    self.anim_state = "EUREKA"
                    self.state_timer = 0
                    
            elif self.anim_state == "EUREKA":
                if self.state_timer == 1:
                    self.speech_text = "💡 EURÊKA ! L'ILLUMINATION DIVINE ! ATTENTION LES YEUX !"
                    self.speech_timer = 45
                    for _ in range(6):
                        self.lightbulb_rays.append({
                            "x": self.px - 6,
                            "y": self.py - 90,
                            "ang": random.uniform(0, 2 * math.pi),
                            "len": random.uniform(18, 35),
                            "life": 1.0
                        })
                self.py -= abs(math.sin(self.state_timer * 0.3)) * 8
                if self.state_timer > 40:
                    self.anim_state = "MIX"
                    self.state_timer = 0
                    
            elif self.anim_state == "MIX":
                if self.state_timer == 1:
                    self.speech_text = "Préparons la première touche de génie... 🧪"
                    self.speech_timer = 45
                if self.state_timer % 3 == 0:
                    pal_x = self.px - 48
                    pal_y = self.py + 4
                    self.palette_splashes.append({
                        "x": pal_x + random.uniform(-12, 12),
                        "y": pal_y + random.uniform(-10, 10),
                        "vx": random.uniform(-4, 3),
                        "vy": random.uniform(-6, -2),
                        "color": self.current_color,
                        "r": random.uniform(3.0, 5.5),
                        "life": 1.0
                    })
                if self.state_timer > 50:
                    self.anim_state = "WINDUP"
                    self.state_timer = 0
                    self.windup_angle = 0.0
                    self.windup_speed = 14.0
                    
            elif self.anim_state == "WINDUP":
                self.windup_speed = min(50.0, self.windup_speed + 1.2)
                self.windup_angle += self.windup_speed
                if self.state_timer == 1:
                    self.speech_text = "PREMIÈRE SALVE ! HOOO-ISSE ! 🚀"
                    self.speech_timer = 50
                if self.state_timer % 4 == 0:
                    self.dust_puffs.append({
                        "x": self.px + random.uniform(-25, 25),
                        "y": self.floor_y - 2,
                        "r": random.uniform(8, 16),
                        "life": 1.0
                    })
                if self.state_timer > 45:
                    self.anim_state = "THROW"
                    self.state_timer = 0
                    self._trigger_throw()
                    
            elif self.anim_state == "THROW":
                if self.state_timer > 14:
                    # L'INTRO EST TERMINÉE ! ON PASSE EN MODE SALVE CONTINUE !
                    self.intro_done = True
                    self.anim_state = "RELOAD"
                    self.state_timer = 0

        # =========================================================================
        # MODE SALVES CONTINUES (LANCE DES PINCEAUX EN RAFALE RÉALISTE SANS RECOMMENCER !)
        # =========================================================================
        else:
            if self.anim_state == "RELOAD":
                if self.state_timer == 1:
                    self.color_index += 1
                    self.current_color = self.palette_colors[self.color_index % len(self.palette_colors)]
                    self.speech_text = random.choice([
                        "ET UN AUTRE ! 🎨",
                        "PRENDS ÇA ! 💥",
                        "ENCORE UNE COULEUR ! ✨",
                        "DANS LE MILLE ! 🎯",
                        "ET HOP LÀ ! 🖌️",
                        "CHEF-D'ŒUVRE SUIVANT ! 🔥",
                        "ATTENTION LA VAGUE ! 🌊",
                        "EN PLEIN DEDANS ! ⚡"
                    ])
                    self.speech_timer = 30
                    
                # Trempage rapide et dynamique dans la palette
                if self.state_timer % 3 == 0:
                    pal_x = self.px - 48
                    pal_y = self.py + 4
                    self.palette_splashes.append({
                        "x": pal_x + random.uniform(-10, 10),
                        "y": pal_y + random.uniform(-8, 8),
                        "vx": random.uniform(-3, 3),
                        "vy": random.uniform(-5, -2),
                        "color": self.current_color,
                        "r": random.uniform(2.5, 5.0),
                        "life": 1.0
                    })
                    
                # Trempage éclair de 18 frames (~0.35 seconde)
                if self.state_timer > 18:
                    self.anim_state = "WINDUP"
                    self.state_timer = 0
                    self.windup_angle = 0.0
                    self.windup_speed = 18.0
                    
            elif self.anim_state == "WINDUP":
                self.windup_speed = min(54.0, self.windup_speed + 1.4)
                self.windup_angle += self.windup_speed
                
                if self.state_timer % 3 == 0:
                    self.dust_puffs.append({
                        "x": self.px + random.uniform(-25, 25),
                        "y": self.floor_y - 2,
                        "r": random.uniform(8, 16),
                        "life": 1.0
                    })
                    self.sweat_drops.append({
                        "x": self.px + random.uniform(-14, 14),
                        "y": self.py - 55,
                        "vx": random.uniform(-3, -1),
                        "vy": random.uniform(-4, -1),
                        "life": 1.0
                    })
                    
                # Moulinet rapide et nerveux de 32 frames (~0.6 seconde)
                if self.state_timer > 32:
                    self.anim_state = "THROW"
                    self.state_timer = 0
                    self._trigger_throw()
                    
            elif self.anim_state == "THROW":
                if self.state_timer > 12:  # Détente rapide (~0.24s)
                    self.anim_state = "RELOAD"
                    self.state_timer = 0

        # GESTION DES PINCEAUX EN PLEIN VOL
        new_flying = []
        for b in self.flying_brushes:
            b["t"] += b["speed"]
            b["rot"] += b["spin"]
            t = b["t"]
            
            cur_x = b["sx"] + (b["tx"] - b["sx"]) * t
            cur_y = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc"] * t * (1 - t))
            
            if random.random() < 0.85:
                self.flight_droplets.append({
                    "x": cur_x + random.uniform(-9, 9),
                    "y": cur_y + random.uniform(-9, 9),
                    "color": b["color"],
                    "r": random.uniform(3.2, 6.0),
                    "vy": random.uniform(0.6, 2.8),
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
                    "base_angle": random.uniform(-42, 42),
                    "vib_t": 0.0,
                    "vib_amp": random.uniform(32.0, 48.0),
                    "life": random.uniform(35.0, 60.0),
                    "splat_r": random.uniform(38, 62),
                    "drips": [
                        {
                            "ox": random.uniform(-18, 18),
                            "oy": random.uniform(14, 30),
                            "len": 0.0,
                            "max_len": random.uniform(90, 320),
                            "speed": random.uniform(1.2, 3.8),
                            "width": random.uniform(4.5, 8.5)
                        } for _ in range(random.randint(2, 5))
                    ]
                })
                
                self.shockwaves.append({"x": tx, "y": ty, "r": 12, "max_r": 95, "alpha": 1.0})
                self.shockwaves.append({"x": tx, "y": ty, "r": 5, "max_r": 65, "alpha": 1.0})
                
                self.comic_texts.append({
                    "x": tx,
                    "y": ty - 38,
                    "text": random.choice(["💥 TCHAAK !", "🎨 SPLAAT !", "✨ SPLOOSH !", "🖌️ BIM DANS LE MILLE !"]),
                    "color": col,
                    "life": 1.0
                })
                
                if len(self.stuck_brushes) > 15:
                    self.stuck_brushes.pop(0)
            else:
                new_flying.append(b)
        self.flying_brushes = new_flying
        
        self._update_particles()
        self._draw()

    def _update_particles(self):
        new_rays = []
        for r in self.lightbulb_rays:
            r["life"] -= 0.04
            r["len"] += 0.8
            if r["life"] > 0:
                new_rays.append(r)
        self.lightbulb_rays = new_rays
        
        new_sw = []
        for s in self.sweat_drops:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.3
            s["life"] -= 0.05
            if s["life"] > 0:
                new_sw.append(s)
        self.sweat_drops = new_sw
        
        new_mus = []
        for mn in self.music_notes:
            mn["y"] -= 1.2
            mn["x"] += math.sin(mn["y"] * 0.1) * 0.8
            mn["life"] -= 0.03
            if mn["life"] > 0:
                new_mus.append(mn)
        self.music_notes = new_mus
        
        new_pal = []
        for p in self.palette_splashes:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.38
            p["life"] -= 0.05
            if p["life"] > 0:
                new_pal.append(p)
        self.palette_splashes = new_pal
        
        new_f_drops = []
        for fd in self.flight_droplets:
            fd["y"] += fd["vy"]
            fd["life"] -= 0.035
            if fd["life"] > 0:
                new_f_drops.append(fd)
        self.flight_droplets = new_f_drops
        
        new_dust = []
        for du in self.dust_puffs:
            du["r"] += 0.7
            du["life"] -= 0.045
            if du["life"] > 0:
                new_dust.append(du)
        self.dust_puffs = new_dust
        
        new_shk = []
        for shk in self.shockwaves:
            shk["r"] += 5.2
            shk["alpha"] -= 0.05
            if shk["alpha"] > 0 and shk["r"] < shk["max_r"]:
                new_shk.append(shk)
        self.shockwaves = new_shk
        
        new_txts = []
        for txt in self.comic_texts:
            txt["life"] -= 0.03
            txt["y"] -= 0.6
            if txt["life"] > 0:
                new_txts.append(txt)
        self.comic_texts = new_txts
        
        new_stuck = []
        for sb in self.stuck_brushes:
            sb["life"] -= 0.015
            sb["vib_t"] += 0.14
            for dr in sb["drips"]:
                if dr["len"] < dr["max_len"]:
                    dr["len"] += dr["speed"]
            if sb["life"] > 0:
                new_stuck.append(sb)
        self.stuck_brushes = new_stuck
        
        if self.speech_timer > 0:
            self.speech_timer -= 1

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
            
        # 3. Ondes de choc de verre
        for shk in self.shockwaves:
            r = shk["r"]
            self.canvas.create_oval(shk["x"] - r, shk["y"] - r*0.6, shk["x"] + r, shk["y"] + r*0.6, outline="#ffffff", width=3)
            for f_ang in [0.3, 1.2, 2.5, 3.8, 5.1]:
                fx2 = shk["x"] + math.cos(f_ang) * (r * 0.85)
                fy2 = shk["y"] + math.sin(f_ang) * (r * 0.55)
                self.canvas.create_line(shk["x"], shk["y"], fx2, fy2, fill="#e2e8f0", width=1)
                
        # 4. Coulures et taches de peinture 3D bombées
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
                    self.canvas.create_oval(dx - dw*0.95, gy - dw*0.95, dx + dw*0.95, gy + dw*1.35, fill=scolor, outline="")
                    self.canvas.create_oval(dx - dw*0.35, gy - dw*0.3, dx + dw*0.25, gy + dw*0.4, fill="#ffffff", outline="")
            
            self.canvas.create_oval(sx - sr - 5, sy - sr - 5, sx + sr + 5, sy + sr + 5, fill="#0f172a", outline="")
            
            pts = []
            for deg in range(0, 360, 18):
                rad = math.radians(deg)
                lobe = 1.0 + 0.44 * math.sin(deg * 3.3) + 0.20 * math.cos(deg * 2.4)
                rr = sr * lobe
                pts.append((sx + math.cos(rad) * rr, sy + math.sin(rad) * rr))
            self.canvas.create_polygon(pts, fill=scolor, outline="", smooth=True)
            
            self.canvas.create_arc(
                sx - sr * 0.72, sy - sr * 0.72, sx + sr * 0.32, sy + sr * 0.32,
                start=35, extent=105, style="arc", outline="#ffffff", width=max(3, int(sr * 0.13))
            )
            
            for ed in [18, 58, 105, 155, 210, 255, 305, 342]:
                erad = math.radians(ed)
                dist = sr * 1.68
                ex = sx + math.cos(erad) * dist
                ey = sy + math.sin(erad) * dist
                self.canvas.create_oval(ex - 4.5, ey - 4.5, ex + 4.5, ey + 4.5, fill=scolor, outline="")
                
        # 5. Manches des pinceaux plantés avec vibration harmonique amortie
        for sb in self.stuck_brushes:
            sx, sy, scolor = sb["x"], sb["y"], sb["color"]
            
            vt = sb["vib_t"]
            damping = math.exp(-vt * 3.2)
            vib_angle = sb["vib_amp"] * damping * math.sin(vt * 28.0)
            total_angle = sb["base_angle"] + vib_angle
            rad = math.radians(total_angle - 90)
            
            handle_len = 96.0
            hx2 = sx + math.cos(rad) * handle_len
            hy2 = sy + math.sin(rad) * handle_len
            
            vx1 = sx + math.cos(rad) * 15
            vy1 = sy + math.sin(rad) * 15
            self.canvas.create_line(sx, sy, vx1, vy1, fill=scolor, width=12, capstyle=tk.ROUND)
            
            vx2 = sx + math.cos(rad) * 30
            vy2 = sy + math.sin(rad) * 30
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#94a3b8", width=10)
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#f8fafc", width=3)
            
            self.canvas.create_line(vx2, vy2, hx2, hy2, fill="#b45309", width=8, capstyle=tk.ROUND)
            self.canvas.create_line(vx2 + math.cos(rad)*6, vy2 + math.sin(rad)*6, hx2 - math.cos(rad)*14, hy2 - math.sin(rad)*14, fill="#d97706", width=3)
            self.canvas.create_oval(hx2 - 5, hy2 - 5, hx2 + 5, hy2 + 5, fill="#78350f", outline="")
            
        # 6. Pinceau en plein vol 3D
        for b in self.flying_brushes:
            t = b["t"]
            bx = b["sx"] + (b["tx"] - b["sx"]) * t
            by = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc"] * t * (1 - t))
            
            scale = 0.45 + 1.35 * t
            rot_rad = math.radians(b["rot"])
            b_len = 82.0 * scale
            
            x_tip = bx - math.cos(rot_rad) * (b_len * 0.42)
            y_tip = by - math.sin(rot_rad) * (b_len * 0.42)
            x_end = bx + math.cos(rot_rad) * (b_len * 0.58)
            y_end = by + math.sin(rot_rad) * (b_len * 0.58)
            
            self.canvas.create_line(bx, by, x_end, y_end, fill="#92400e", width=max(3, int(8 * scale)), capstyle=tk.ROUND)
            v_mid_x = bx - math.cos(rot_rad) * (b_len * 0.16)
            v_mid_y = by - math.sin(rot_rad) * (b_len * 0.16)
            self.canvas.create_line(bx, by, v_mid_x, v_mid_y, fill="#cbd5e1", width=max(4, int(9 * scale)))
            self.canvas.create_line(v_mid_x, v_mid_y, x_tip, y_tip, fill=b["color"], width=max(5, int(12 * scale)), capstyle=tk.ROUND)
            
            tail_x = bx + math.cos(rot_rad) * (b_len * 1.1)
            tail_y = by + math.sin(rot_rad) * (b_len * 1.1)
            self.canvas.create_line(x_end, y_end, tail_x, tail_y, fill="#f8fafc", width=2, dash=(4, 4))
            
        # 7. Textes de bande dessinée
        for cs in self.comic_texts:
            cx, cy = cs["x"], cs["y"]
            star_pts = []
            for sa_deg in range(0, 360, 30):
                sa = math.radians(sa_deg)
                sr = 28 if (sa_deg // 30) % 2 == 0 else 14
                star_pts.append((cx + math.cos(sa) * sr, cy + math.sin(sa) * sr))
            self.canvas.create_polygon(star_pts, fill="#facc15", outline="#ea580c", width=2)
            self.canvas.create_text(cx, cy, text=cs["text"], font=("Impact", 13, "bold"), fill="#dc2626")
            
        # 8. Poussière cartoon au sol
        for du in self.dust_puffs:
            dr = du["r"]
            self.canvas.create_oval(du["x"] - dr, du["y"] - dr*0.5, du["x"] + dr, du["y"] + dr*0.5, fill="#cbd5e1", outline="")
            
        # 9. Gouttes de sueur cartoon
        for s in self.sweat_drops:
            self.canvas.create_oval(s["x"] - 4, s["y"] - 6, s["x"] + 4, s["y"] + 6, fill="#38bdf8", outline="#0284c7", width=1)
            
        # 10. Notes de musique
        for mn in self.music_notes:
            self.canvas.create_text(mn["x"], mn["y"], text=mn["symbol"], font=("Impact", 16, "bold"), fill=mn["color"])
            
        # 11. Rayons d'illumination Eurêka
        for lr in self.lightbulb_rays:
            x2 = lr["x"] + math.cos(lr["ang"]) * lr["len"]
            y2 = lr["y"] + math.sin(lr["ang"]) * lr["len"]
            self.canvas.create_line(lr["x"], lr["y"], x2, y2, fill="#facc15", width=2)
            
        # 12. Réticule de visée lors du WINDUP
        if self.anim_state == "WINDUP":
            cx, cy = self.target_x, self.target_y
            ret_r = 24 + math.sin(self.phase * 4.0) * 4
            self.canvas.create_oval(cx - ret_r, cy - ret_r, cx + ret_r, cy + ret_r, outline="#ef4444", width=2, dash=(4, 4))
            self.canvas.create_line(cx - ret_r - 10, cy, cx + ret_r + 10, cy, fill="#ef4444", width=2)
            self.canvas.create_line(cx, cy - ret_r - 10, cx, cy + ret_r + 10, fill="#ef4444", width=2)
            self.canvas.create_text(cx, cy - ret_r - 14, text="🎯 CIBLE D'ARTISTE !", font=("Impact", 11, "bold"), fill="#ef4444")
            
        # 13. Le Personnage du Peintre Cartoon de Dessin Animé
        self._draw_theatrical_painter()

    def _draw_theatrical_painter(self):
        px = self.px
        py = self.py
        
        # CALCUL DE L'INCLINAISON ET DE L'ALTITUDE
        lean = 0.0
        if self.anim_state == "WINDUP":
            lean = 22.0
        elif self.anim_state == "THROW":
            lean = -20.0
        elif self.anim_state == "MEASURE":
            lean = 8.0
            
        body_x = px + lean * 0.65
        altitude = max(0.0, self.base_py - py)
        shadow_scale = max(0.48, 1.0 - altitude * 0.022)
        floor_y = self.floor_y
        
        # =========================================================================
        # VRAIE OMBRE CARTOON PORTÉE AU SOL (MULTI-COUCHES, PERSPECTIVE ET DIFFUSION)
        # =========================================================================
        # 1. Centre de projection de l'ombre au sol selon l'angle de la lumière et l'inclinaison
        sh_x = px + 8 + (lean * 0.75)
        sh_y = floor_y
        
        # 2. Pénombre externe douce (halo d'ombre diffus)
        p_rx = 54 * shadow_scale
        p_ry = 18 * shadow_scale
        self.canvas.create_oval(sh_x - p_rx, sh_y - p_ry, sh_x + p_rx, sh_y + p_ry, fill="#1e293b", outline="")
        
        # 3. Ombre portée du corps et du torse
        b_rx = 40 * shadow_scale
        b_ry = 14 * shadow_scale
        self.canvas.create_oval(sh_x - b_rx, sh_y - b_ry, sh_x + b_rx, sh_y + b_ry, fill="#0f172a", outline="")
        
        # 4. Ombre portée de la tête et du béret (projetée vers l'arrière selon le lean)
        h_sh_x = sh_x + (lean * 0.45) + 6
        h_sh_y = sh_y - 2
        h_rx = 24 * shadow_scale
        h_ry = 10 * shadow_scale
        self.canvas.create_oval(h_sh_x - h_rx, h_sh_y - h_ry, h_sh_x + h_rx, h_sh_y + h_ry, fill="#0f172a", outline="")
        
        # 5. Ombre portée de la palette sur le côté gauche
        pal_sh_x = sh_x - (36 * shadow_scale)
        pal_sh_y = sh_y + 1
        pal_rx = 18 * shadow_scale
        pal_ry = 9 * shadow_scale
        self.canvas.create_oval(pal_sh_x - pal_rx, pal_sh_y - pal_ry, pal_sh_x + pal_rx, pal_sh_y + pal_ry, fill="#0f172a", outline="")
        
        # 6. Cœur d'ombre profond d'occlusion au sol (Umbra centrale sous le centre de masse)
        core_rx = 26 * shadow_scale
        core_ry = 8 * shadow_scale
        self.canvas.create_oval(sh_x - core_rx, sh_y - core_ry, sh_x + core_rx, sh_y + core_ry, fill="#020617", outline="")
        
        # 7. Ombres de contact direct sous les semelles des chaussures (quand au sol)
        if altitude < 4.0:
            # Pied gauche
            self.canvas.create_oval(px - 34, floor_y - 3, px - 6, floor_y + 5, fill="#000000", outline="")
            # Pied droit
            self.canvas.create_oval(px + 6, floor_y - 3, px + 34, floor_y + 5, fill="#000000", outline="")
            
        # =========================================================================
        # LE PERSONNAGE DU PEINTRE
        # =========================================================================
        # CHAUSSURES D'ARTISTE EN CUIR
        self.canvas.create_oval(px - 34, py + 30, px - 6, py + 46, fill="#78350f", outline="#451a03", width=2)
        self.canvas.create_oval(px + 6, py + 30, px + 34, py + 46, fill="#78350f", outline="#451a03", width=2)
        self.canvas.create_rectangle(px - 22, py + 34, px - 16, py + 40, outline="#facc15", width=2)
        self.canvas.create_rectangle(px + 16, py + 34, px + 22, py + 40, outline="#facc15", width=2)
        
        # PANTALON EN VELOURS CÔTELÉ ANTHRACITE
        self.canvas.create_rectangle(px - 26, py + 18, px + 26, py + 36, fill="#1e293b", outline="#0f172a", width=2)
        
        # TABLIER D'ARTISTE PEINTRE AVEC POCHE VENTRALE ET TÂCHES
        self.canvas.create_polygon([
            (px - 24, py - 10), (px + 24, py - 10),
            (px + 28, py + 26), (px - 28, py + 26)
        ], fill="#f8fafc", outline="#0f172a", width=2)
        self.canvas.create_rectangle(px - 16, py + 8, px + 16, py + 24, fill="#e2e8f0", outline="#94a3b8", width=1)
        self.canvas.create_line(px - 8, py + 12, px - 12, py - 4, fill="#b45309", width=3)
        self.canvas.create_oval(px - 14, py - 8, px - 10, py - 4, fill="#3b82f6", outline="")
        self.canvas.create_oval(px - 12, py + 2, px - 6, py + 8, fill="#ef4444", outline="")
        self.canvas.create_oval(px + 8, py + 10, px + 14, py + 16, fill="#3b82f6", outline="")
        self.canvas.create_oval(px - 4, py + 16, px + 2, py + 22, fill="#facc15", outline="")
        self.canvas.create_oval(px + 6, py + 2, px + 11, py + 7, fill="#10b981", outline="")
        
        # MARINIÈRE BRETONNE RAYÉE BLEUE ET BLANCHE
        self.canvas.create_oval(body_x - 34, py - 28, body_x + 34, py + 26, fill="#ffffff", outline="#0f172a", width=3)
        for ry in range(-18, 24, 8):
            self.canvas.create_line(body_x - 30, py + ry, body_x + 30, py + ry, fill="#1d4ed8", width=4)
            
        # FOULARD / CRAVATE ROUGE DE SOIE
        self.canvas.create_polygon([
            (body_x - 18, py - 26), (body_x, py - 18), (body_x + 18, py - 26),
            (body_x + 8, py - 8), (body_x - 8, py - 8)
        ], fill="#dc2626", outline="#7f1d1d", width=2)
        self.canvas.create_polygon([(body_x - 4, py - 8), (body_x - 10, py + 2), (body_x, py - 2)], fill="#dc2626", outline="")
        self.canvas.create_polygon([(body_x + 4, py - 8), (body_x + 10, py + 2), (body_x, py - 2)], fill="#dc2626", outline="")
        
        # PALETTE DE PEINTRE EN BOIS
        pal_x = body_x - 50
        pal_y = py + 6
        self.canvas.create_oval(pal_x - 30, pal_y - 22, pal_x + 30, pal_y + 22, fill="#d97706", outline="#78350f", width=3)
        self.canvas.create_oval(pal_x - 20, pal_y - 8, pal_x - 10, pal_y + 8, fill="#fed7aa", outline="#78350f", width=2)
        palette_spots = ["#ef4444", "#3b82f6", "#facc15", "#10b981", "#a855f7", "#ea580c"]
        for pi, pc in enumerate(palette_spots):
            pdeg = math.radians(pi * 44 - 30)
            spot_x = pal_x + math.cos(pdeg) * 18
            spot_y = pal_y + math.sin(pdeg) * 12
            self.canvas.create_oval(spot_x - 5, spot_y - 5, spot_x + 5, spot_y + 5, fill=pc, outline="")
            self.canvas.create_oval(spot_x - 2, spot_y - 3, spot_x + 1, spot_y, fill="#ffffff", outline="")
            
        # BRAS ET GESTUELLE
        arm_start_x = body_x + 24
        arm_start_y = py - 16
        
        if self.anim_state in ("ENTER", "MEASURE"):
            hand_x = body_x - 20
            hand_y = py - 46
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 8, hand_y - 8, hand_x + 8, hand_y + 8, fill="#fed7aa", outline="#c2410c", width=2)
            self.canvas.create_line(hand_x, hand_y, hand_x, hand_y - 20, fill="#fed7aa", width=6, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y, hand_x - 16, hand_y + 20, fill="#92400e", width=4)
            self.canvas.create_line(hand_x - 16, hand_y + 20, hand_x - 24, hand_y + 28, fill=self.current_color, width=6, capstyle=tk.ROUND)
            
        elif self.anim_state == "EUREKA":
            hand_x = body_x - 6
            hand_y = py - 65
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 7, hand_y - 7, hand_x + 7, hand_y + 7, fill="#fed7aa", outline="#c2410c", width=2)
            self.canvas.create_line(hand_x, hand_y, hand_x, hand_y - 15, fill="#fed7aa", width=5, capstyle=tk.ROUND)
            bulb_y = py - 95
            self.canvas.create_oval(hand_x - 12, bulb_y - 12, hand_x + 12, bulb_y + 12, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_rectangle(hand_x - 5, bulb_y + 10, hand_x + 5, bulb_y + 16, fill="#94a3b8", outline="#475569", width=1)
            self.canvas.create_text(hand_x, bulb_y, text="💡", font=("Segoe UI Emoji", 14))
            
        elif self.anim_state in ("MIX", "RELOAD"):
            # Bras qui plonge dans la palette pour charger la peinture
            hand_x = pal_x + 10
            hand_y = pal_y - 10
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y - 16, hand_x, hand_y + 12, fill="#92400e", width=4)
            self.canvas.create_line(hand_x, hand_y + 12, hand_x, hand_y + 22, fill=self.current_color, width=8, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 6, hand_y - 6, hand_x + 6, hand_y + 6, fill="#fed7aa", outline="#c2410c", width=2)
            
        elif self.anim_state == "WINDUP":
            w_rad = math.radians(self.windup_angle)
            w_len = 58.0
            hand_x = arm_start_x + math.cos(w_rad) * w_len
            hand_y = arm_start_y + math.sin(w_rad) * w_len
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(arm_start_x - w_len, arm_start_y - w_len, arm_start_x + w_len, arm_start_y + w_len, outline="#f8fafc", width=2, dash=(6, 4))
            px2 = hand_x + math.cos(w_rad + math.pi/2) * 34
            py2 = hand_y + math.sin(w_rad + math.pi/2) * 34
            self.canvas.create_line(hand_x, hand_y, px2, py2, fill="#92400e", width=5)
            self.canvas.create_line(px2, py2, px2 + math.cos(w_rad + math.pi/2)*16, py2 + math.sin(w_rad + math.pi/2)*16, fill=self.current_color, width=8, capstyle=tk.ROUND)
            
        elif self.anim_state == "THROW":
            hand_x = body_x - 44
            hand_y = py - 48
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            for offy in [-10, 0, 10]:
                self.canvas.create_line(hand_x, hand_y + offy, hand_x - 55, hand_y + offy - 14, fill="#ffffff", width=3, dash=(4, 4))
                
        # TÊTE EXPRESSIVE
        head_x = body_x
        head_y = py - 46
        self.canvas.create_oval(head_x - 25, head_y - 25, head_x + 25, head_y + 25, fill="#fed7aa", outline="#c2410c", width=2)
        self.canvas.create_oval(head_x - 22, head_y + 2, head_x - 12, head_y + 12, fill="#fca5a5", outline="")
        self.canvas.create_oval(head_x + 12, head_y + 2, head_x + 22, head_y + 12, fill="#fca5a5", outline="")
        
        # BÉRET ROUGE
        beret_tilt = -10 if self.anim_state == "WINDUP" else (6 if self.anim_state == "MEASURE" else 0)
        if self.anim_state == "THROW":
            beret_tilt = -18
        self.canvas.create_oval(head_x - 34, head_y - 36 + beret_tilt, head_x + 26, head_y - 14 + beret_tilt, fill="#dc2626", outline="#7f1d1d", width=3)
        self.canvas.create_line(head_x - 6, head_y - 36 + beret_tilt, head_x - 6, head_y - 43 + beret_tilt, fill="#7f1d1d", width=3)
        
        # YEUX
        if self.anim_state == "MEASURE":
            self.canvas.create_line(head_x + 4, head_y - 6, head_x + 16, head_y - 6, fill="#0f172a", width=3)
            self.canvas.create_oval(head_x - 18, head_y - 14, head_x - 4, head_y + 2, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 14, head_y - 11, head_x - 8, head_y - 5, fill="#ffffff", outline="")
        elif self.anim_state == "WINDUP":
            self.canvas.create_oval(head_x - 18, head_y - 13, head_x - 3, head_y + 2, fill="#f59e0b", outline="#713f12", width=2)
            self.canvas.create_oval(head_x + 3, head_y - 13, head_x + 18, head_y + 2, fill="#f59e0b", outline="#713f12", width=2)
            self.canvas.create_line(head_x - 11, head_y - 11, head_x - 11, head_y, fill="#0f172a", width=3)
            self.canvas.create_line(head_x + 11, head_y - 11, head_x + 11, head_y, fill="#0f172a", width=3)
        elif self.anim_state == "EUREKA":
            self.canvas.create_oval(head_x - 18, head_y - 16, head_x - 2, head_y, fill="#ffffff", outline="#0f172a", width=2)
            self.canvas.create_oval(head_x + 2, head_y - 16, head_x + 18, head_y, fill="#ffffff", outline="#0f172a", width=2)
            self.canvas.create_oval(head_x - 12, head_y - 11, head_x - 6, head_y - 5, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x + 6, head_y - 11, head_x + 12, head_y - 5, fill="#0f172a", outline="")
        else:
            self.canvas.create_oval(head_x - 16, head_y - 11, head_x - 4, head_y + 1, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x + 4, head_y - 11, head_x + 16, head_y + 1, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 13, head_y - 9, head_x - 8, head_y - 5, fill="#ffffff", outline="")
            self.canvas.create_oval(head_x + 8, head_y - 9, head_x + 13, head_y - 5, fill="#ffffff", outline="")
            
        # SOURCILS
        if self.anim_state == "WINDUP":
            self.canvas.create_line(head_x - 18, head_y - 14, head_x - 4, head_y - 18, fill="#451a03", width=3)
            self.canvas.create_line(head_x + 4, head_y - 18, head_x + 18, head_y - 14, fill="#451a03", width=3)
        elif self.anim_state == "MEASURE":
            self.canvas.create_line(head_x - 18, head_y - 17, head_x - 4, head_y - 17, fill="#451a03", width=3)
            self.canvas.create_line(head_x + 4, head_y - 15, head_x + 18, head_y - 12, fill="#451a03", width=3)
        else:
            self.canvas.create_arc(head_x - 18, head_y - 20, head_x - 4, head_y - 10, start=30, extent=120, style="arc", outline="#451a03", width=3)
            self.canvas.create_arc(head_x + 4, head_y - 20, head_x + 18, head_y - 10, start=30, extent=120, style="arc", outline="#451a03", width=3)
            
        # NEZ
        self.canvas.create_oval(head_x - 6, head_y - 3, head_x + 6, head_y + 7, fill="#fca5a5", outline="#c2410c", width=1)
        
        # MOUSTACHE
        mustache_bob = math.sin(self.phase * 2.0) * 1.5
        m_pts = [
            (head_x - 30, head_y + 5 - mustache_bob),
            (head_x - 14, head_y + 12 + mustache_bob),
            (head_x, head_y + 9),
            (head_x + 14, head_y + 12 + mustache_bob),
            (head_x + 30, head_y + 5 - mustache_bob)
        ]
        self.canvas.create_line(m_pts, fill="#0f172a", width=5, smooth=True)
        
        # BULLE DE DIALOGUE
        if self.speech_timer > 0:
            bx = body_x - 60
            by = py - 105
            self.canvas.create_rectangle(bx - 155, by - 18, bx + 155, by + 18, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_polygon([(bx + 20, by + 18), (bx + 10, by + 30), (bx, by + 18)], fill="#fef08a", outline="#ca8a04", width=1)
            self.canvas.create_text(bx, by, text=self.speech_text, font=("Impact", 11, "bold"), fill="#0f172a")

def run_test():
    root = tk.Tk()
    root.withdraw()
    p = TestContinuousPainter(root)
    print("Testing continuous painter with 800 frames...")
    for f in range(800):
        p.tick_frame()
        root.update_idletasks()
        root.update()
    print(f"Test completed! Throws: {p.throw_count}, Stuck brushes: {len(p.stuck_brushes)}, intro_done: {p.intro_done}")
    root.destroy()

if __name__ == "__main__":
    run_test()

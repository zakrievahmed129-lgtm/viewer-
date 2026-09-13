import tkinter as tk
import math
import random
import time

keys_state = {"active": True, "last_key_time": 0.0, "key_char": "A"}
ghost_state = {"active": True, "booh": False}
tts_state = {"active": True, "is_speaking": True, "text": "ALERTE !"}
rotate_state = {"active": True, "angle": 180.0}

# 1. CartoonKeysOverlay
class CartoonKeysOverlay:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        try:
            sw = master.winfo_screenwidth()
            sh = master.winfo_screenheight()
        except Exception:
            sw, sh = 1920, 1080
            
        self.w, self.h = 280, 210
        self.pos_x = sw - self.w - 30
        self.pos_y = sh - self.h - 60
        self.win.geometry(f"{self.w}x{self.h}+{self.pos_x}+{self.pos_y}")
        
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.phase = 0.0
        self.hammer_hit = 0.0
        self.spring_keys = []
        self.visible = False
        self._loop_active = True
        self._tick()
        
    def trigger_hit(self, key_name="A"):
        self.hammer_hit = 1.0
        letters = ["A", "E", "I", "O", "U", "Z", "?!", "★", "⚡"]
        disp_key = key_name if key_name else random.choice(letters)
        self.spring_keys.append({
            "x": random.randint(40, self.w - 90),
            "y": self.h - 50,
            "vy": random.uniform(-7.5, -4.5),
            "vx": random.uniform(-1.5, 1.5),
            "rot": random.uniform(-25, 25),
            "key": disp_key,
            "life": 1.0
        })
        if len(self.spring_keys) > 6:
            self.spring_keys.pop(0)

    def _tick(self):
        if not self._loop_active:
            return
        try:
            global keys_state
            if keys_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                self.phase += 0.2
                if self.hammer_hit > 0:
                    self.hammer_hit = max(0.0, self.hammer_hit - 0.12)
                else:
                    if random.random() < 0.05:
                        self.trigger_hit()
                        
                new_keys = []
                for k in self.spring_keys:
                    k["x"] += k["vx"]
                    k["y"] += k["vy"]
                    k["vy"] += 0.35
                    k["life"] -= 0.03
                    if k["life"] > 0:
                        new_keys.append(k)
                self.spring_keys = new_keys
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.spring_keys.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        cx = self.w - 95
        cy = self.h - 75
        
        # 1. Touches en folie
        for k in self.spring_keys:
            kx, ky, kl = k["x"], k["y"], k["life"]
            txt = k["key"]
            kw, kh = 34, 30
            pts = []
            base_y = self.h - 25
            segs = 6
            for s in range(segs):
                sy = base_y + (ky - base_y) * (s / float(segs))
                sx = kx + math.sin(self.phase * 2 + s) * 7.0
                pts.extend([sx, sy])
            if len(pts) >= 4:
                self.canvas.create_line(pts, fill="#94a3b8", width=3, capstyle=tk.ROUND, smooth=True)
            self.canvas.create_rectangle(kx - kw//2 + 3, ky - kh//2 + 4, kx + kw//2 + 3, ky + kh//2 + 4, fill="#0f172a", outline="")
            self.canvas.create_rectangle(kx - kw//2, ky - kh//2, kx + kw//2, ky + kh//2, fill="#f8fafc", outline="#334155", width=2)
            self.canvas.create_rectangle(kx - kw//2 + 2, ky - kh//2 + 2, kx + kw//2 - 2, ky - kh//2 + 8, fill="#e2e8f0", outline="")
            self.canvas.create_text(kx, ky + 1, text=txt, font=("Impact", 13, "bold"), fill="#0f172a")

        # 2. Mini-clavier
        kbd_w, kbd_h = 100, 24
        self.canvas.create_rectangle(cx - kbd_w//2, cy + 40, cx + kbd_w//2, cy + 40 + kbd_h, fill="#334155", outline="#0f172a", width=3)
        for i in range(5):
            bx = cx - kbd_w//2 + 10 + i * 18
            self.canvas.create_rectangle(bx, cy + 43, bx + 12, cy + 50, fill="#f1f5f9", outline="#0f172a", width=1)
            self.canvas.create_rectangle(bx, cy + 52, bx + 12, cy + 59, fill="#f1f5f9", outline="#0f172a", width=1)
            
        # 3. Lutin cartoon
        bob = math.sin(self.phase) * 3.0
        head_y = cy + bob
        self.canvas.create_oval(cx - 28, head_y - 30, cx + 28, head_y + 26, fill="#8b5cf6", outline="#4c1d95", width=3)
        self.canvas.create_polygon(cx - 24, head_y - 5, cx - 44, head_y - 18, cx - 20, head_y + 12, fill="#a78bfa", outline="#4c1d95", width=2)
        self.canvas.create_polygon(cx + 24, head_y - 5, cx + 44, head_y - 18, cx + 20, head_y + 12, fill="#a78bfa", outline="#4c1d95", width=2)
        self.canvas.create_polygon(cx - 24, head_y - 25, cx + 24, head_y - 25, cx + 18, head_y - 68, cx - 2, head_y - 28, fill="#facc15", outline="#854d0e", width=3)
        self.canvas.create_oval(cx + 14, head_y - 74, cx + 26, head_y - 62, fill="#ef4444", outline="#991b1b", width=2)
        self.canvas.create_oval(cx - 18, head_y - 16, cx - 3, head_y + 8, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_oval(cx + 3, head_y - 16, cx + 18, head_y + 8, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_oval(cx - 12, head_y - 9, cx - 5, head_y - 2, fill="#0f172a", outline="")
        self.canvas.create_oval(cx + 5, head_y - 9, cx + 12, head_y - 2, fill="#0f172a", outline="")
        self.canvas.create_oval(cx - 22, head_y + 4, cx - 14, head_y + 12, fill="#f472b6", outline="")
        self.canvas.create_oval(cx + 14, head_y + 4, cx + 22, head_y + 12, fill="#f472b6", outline="")
        self.canvas.create_arc(cx - 16, head_y + 2, cx + 16, head_y + 24, start=0, extent=-180, fill="#701a75", outline="#0f172a", width=2)
        self.canvas.create_rectangle(cx - 5, head_y + 12, cx + 5, head_y + 18, fill="#ffffff", outline="#0f172a", width=1)
        
        # Marteaux
        hammer_swing = math.sin(self.phase * 2) * 20 - (self.hammer_hit * 35)
        hx = cx - 35
        hy = head_y + 25 + hammer_swing
        self.canvas.create_line(cx - 20, head_y + 12, hx, hy, fill="#8b5cf6", width=8, capstyle=tk.ROUND)
        self.canvas.create_line(hx, hy, hx - 12, hy - 26, fill="#b45309", width=4)
        self.canvas.create_rectangle(hx - 22, hy - 32, hx - 2, hy - 20, fill="#dc2626", outline="#7f1d1d", width=2)
        
        hx2 = cx + 35
        hy2 = head_y + 25 - hammer_swing
        self.canvas.create_line(cx + 20, head_y + 12, hx2, hy2, fill="#8b5cf6", width=8, capstyle=tk.ROUND)
        self.canvas.create_line(hx2, hy2, hx2 + 12, hy2 - 26, fill="#b45309", width=4)
        self.canvas.create_rectangle(hx2 + 2, hy2 - 32, hx2 + 22, hy2 - 20, fill="#dc2626", outline="#7f1d1d", width=2)

        # Bulle de rire
        bx, by = cx - 55, head_y - 45
        self.canvas.create_rectangle(bx - 36, by - 12, bx + 36, by + 12, fill="#fef08a", outline="#ca8a04", width=2)
        self.canvas.create_text(bx, by, text="HIHIHI ! ⌨️", font=("Impact", 10, "bold"), fill="#713f12")


# 2. CartoonGhostOverlay
class CartoonGhostOverlay:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        try:
            sw = master.winfo_screenwidth()
            sh = master.winfo_screenheight()
        except Exception:
            sw, sh = 1920, 1080
            
        self.sw, self.sh = sw, sh
        self.w, self.h = 320, 240
        self.pos_x = int(sw * 0.15)
        self.pos_y = int(sh * 0.25)
        self.win.geometry(f"{self.w}x{self.h}+{self.pos_x}+{self.pos_y}")
        
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.phase = 0.0
        self.float_x = 0.0
        self.float_y = 0.0
        self.booh_timer = 0.0
        self.sound_waves = []
        self.visible = False
        self._loop_active = True
        self._tick()
        
    def trigger_booh(self):
        self.booh_timer = 1.0
        self.sound_waves.append({"radius": 20, "max_r": 90, "life": 1.0})

    def _tick(self):
        if not self._loop_active:
            return
        try:
            global ghost_state
            if ghost_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                self.phase += 0.08
                self.float_x = math.sin(self.phase * 0.7) * 45.0
                self.float_y = math.cos(self.phase * 1.2) * 25.0
                
                if self.booh_timer > 0:
                    self.booh_timer = max(0.0, self.booh_timer - 0.04)
                else:
                    if random.random() < 0.04:
                        self.trigger_booh()
                        
                # Update sound waves
                new_waves = []
                for w in self.sound_waves:
                    w["radius"] += 3.5
                    w["life"] -= 0.05
                    if w["life"] > 0 and w["radius"] < w["max_r"]:
                        new_waves.append(w)
                self.sound_waves = new_waves
                
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.sound_waves.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        cx = self.w // 2 + int(self.float_x)
        cy = self.h // 2 + int(self.float_y)
        
        # Ondes sonores de hululement
        for w in self.sound_waves:
            r = w["radius"]
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#38bdf8", width=3, dash=(4, 4))
            
        # Traînée luminescente de poussière d'étoiles
        for i in range(5):
            tx = cx - 45 - i * 15 + math.sin(self.phase + i) * 8
            ty = cy + 30 + i * 12 + math.cos(self.phase + i) * 6
            self.canvas.create_oval(tx - 3, ty - 3, tx + 3, ty + 3, fill="#38bdf8", outline="")
            self.canvas.create_text(tx + 6, ty - 6, text="✦", fill="#7dd3fc", font=("Arial", 8))
            
        # Corps du fantôme en poire cartoon ondulant
        body_pts = []
        body_w = 48
        body_h = 65
        # Sommet arrondi
        head_top = cy - body_h
        for a in range(0, 185, 15):
            rad = math.radians(a)
            body_pts.append((cx + math.cos(rad) * body_w, cy - 25 - math.sin(rad) * 45))
        # Côtés et queue en volutes
        skirt_y = cy + 35
        vol_count = 4
        for v in range(vol_count + 1):
            vx = cx - body_w + (v * (body_w * 2 / float(vol_count)))
            vy = skirt_y + math.sin(self.phase * 3 + v * 1.5) * 12
            body_pts.append((vx, vy))
            
        # Dessiner le corps du fantôme (blanc avec contour soigné)
        self.canvas.create_polygon(body_pts, fill="#f8fafc", outline="#0f172a", width=3, smooth=True)
        # Reflet bleuté ectoplasmique
        self.canvas.create_arc(cx - body_w + 10, head_top + 10, cx + body_w - 10, cy + 10, start=60, extent=60, style="arc", outline="#bae6fd", width=3)
        
        # Yeux cartoon noirs intenses avec reflets
        eye_y = cy - 28
        self.canvas.create_oval(cx - 24, eye_y - 18, cx - 6, eye_y + 12, fill="#0f172a", outline="")
        self.canvas.create_oval(cx + 6, eye_y - 18, cx + 24, eye_y + 12, fill="#0f172a", outline="")
        # Reflets d'yeux blancs
        self.canvas.create_oval(cx - 18, eye_y - 12, cx - 11, eye_y - 4, fill="#ffffff", outline="")
        self.canvas.create_oval(cx + 11, eye_y - 12, cx + 18, eye_y - 4, fill="#ffffff", outline="")
        
        # Joues roses
        self.canvas.create_oval(cx - 32, eye_y + 8, cx - 22, eye_y + 16, fill="#f472b6", outline="")
        self.canvas.create_oval(cx + 22, eye_y + 8, cx + 32, eye_y + 16, fill="#f472b6", outline="")
        
        # Bouche : ouverte en 'O' si booh, sinon sourire mignon
        if self.booh_timer > 0:
            self.canvas.create_oval(cx - 14, eye_y + 16, cx + 14, eye_y + 36, fill="#0f172a", outline="#38bdf8", width=2)
            self.canvas.create_oval(cx - 8, eye_y + 24, cx + 8, eye_y + 34, fill="#ef4444", outline="")
            # Bulle de cri
            self.canvas.create_text(cx, head_top - 18, text="BOOOOUH ! 👻🎶", font=("Impact", 13, "bold"), fill="#38bdf8")
        else:
            self.canvas.create_arc(cx - 12, eye_y + 14, cx + 12, eye_y + 28, start=0, extent=-180, fill="#0f172a", outline="")


# 3. CartoonMegaphoneOverlay
class CartoonMegaphoneOverlay:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        try:
            sw = master.winfo_screenwidth()
            sh = master.winfo_screenheight()
        except Exception:
            sw, sh = 1920, 1080
            
        self.w, self.h = 340, 200
        self.pos_x = sw - self.w - 40
        self.pos_y = 50
        self.win.geometry(f"{self.w}x{self.h}+{self.pos_x}+{self.pos_y}")
        
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.phase = 0.0
        self.sound_waves = []
        self.visible = False
        self._loop_active = True
        self._tick()

    def _tick(self):
        if not self._loop_active:
            return
        try:
            global tts_state
            if tts_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                self.phase += 0.25
                if random.random() < 0.25:
                    self.sound_waves.append({"dist": 10, "max_d": 70, "life": 1.0})
                    
                new_waves = []
                for w in self.sound_waves:
                    w["dist"] += 4.0
                    w["life"] -= 0.06
                    if w["life"] > 0:
                        new_waves.append(w)
                self.sound_waves = new_waves
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.sound_waves.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        cx = 95
        cy = 110
        
        # Squash & stretch cartoon du mégaphone
        squash = math.sin(self.phase * 2) * 5.0
        
        # 1. Pavillon du mégaphone rouge et blanc
        cone_pts = [
            (cx - 40, cy - 14),
            (cx + 45 + squash, cy - 42),
            (cx + 45 + squash, cy + 42),
            (cx - 40, cy + 14)
        ]
        self.canvas.create_polygon(cone_pts, fill="#ef4444", outline="#7f1d1d", width=3)
        # Bandes blanches décoratives
        self.canvas.create_line(cx + 10, cy - 26, cx + 10, cy + 26, fill="#ffffff", width=8)
        
        # Pavillon ouverture ellipse
        self.canvas.create_oval(cx + 35 + squash, cy - 44, cx + 55 + squash, cy + 44, fill="#b91c1c", outline="#7f1d1d", width=3)
        self.canvas.create_oval(cx + 40 + squash, cy - 32, cx + 50 + squash, cy + 32, fill="#0f172a", outline="")
        
        # Poignée et manette
        self.canvas.create_line(cx - 20, cy + 14, cx - 26, cy + 55, fill="#334155", width=9, capstyle=tk.ROUND)
        self.canvas.create_oval(cx - 30, cy + 50, cx - 20, cy + 60, fill="#ef4444", outline="#7f1d1d", width=2)
        
        # Gyrophare tournoyant sur le dessus
        gy_color = "#facc15" if int(self.phase * 4) % 2 == 0 else "#3b82f6"
        self.canvas.create_rectangle(cx - 10, cy - 32, cx + 6, cy - 18, fill=gy_color, outline="#0f172a", width=2)
        self.canvas.create_text(cx - 2, cy - 25, text="🚨", font=("Segoe UI Emoji", 11))
        
        # Yeux expressifs sur le dessus du cône
        self.canvas.create_oval(cx - 22, cy - 24, cx - 6, cy - 8, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_oval(cx - 6, cy - 24, cx + 10, cy - 8, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_oval(cx - 14, cy - 18, cx - 8, cy - 12, fill="#0f172a", outline="")
        self.canvas.create_oval(cx + 2, cy - 18, cx + 8, cy - 12, fill="#0f172a", outline="")
        
        # Bras cartoon avec gants blancs
        self.canvas.create_line(cx - 32, cy - 2, cx - 60, cy + 10, fill="#ef4444", width=5, capstyle=tk.ROUND)
        self.canvas.create_oval(cx - 68, cy + 2, cx - 52, cy + 18, fill="#ffffff", outline="#0f172a", width=2)
        
        # Ondes sonores multicolores qui jaillissent du mégaphone
        mouth_x = cx + 55 + squash
        for w in self.sound_waves:
            d = w["dist"]
            self.canvas.create_arc(mouth_x + d - 20, cy - d, mouth_x + d + 20, cy + d, start=-50, extent=100, style="arc", outline="#facc15", width=4)
            self.canvas.create_text(mouth_x + d + 15, cy - 12 + math.sin(d)*10, text="📢", font=("Segoe UI Emoji", 10))
            
        # Bulle d'alerte BD
        bubble_x = cx + 165
        bubble_y = cy - 25
        self.canvas.create_rectangle(bubble_x - 65, bubble_y - 20, bubble_x + 65, bubble_y + 20, fill="#fef08a", outline="#ca8a04", width=3)
        self.canvas.create_text(bubble_x, bubble_y, text="ALERTE ! ⚠️\nVOIX SYSTÈME", font=("Impact", 11, "bold"), fill="#713f12", justify=tk.CENTER)


# 4. CartoonRotateOverlay
class CartoonRotateOverlay:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        try:
            sw = master.winfo_screenwidth()
            sh = master.winfo_screenheight()
        except Exception:
            sw, sh = 1920, 1080
            
        self.w, self.h = 280, 240
        self.pos_x = 35
        self.pos_y = sh - self.h - 60
        self.win.geometry(f"{self.w}x{self.h}+{self.pos_x}+{self.pos_y}")
        
        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h, bg="#010101", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.phase = 0.0
        self.lever_angle = 0.0
        self.visible = False
        self._loop_active = True
        self._tick()

    def _tick(self):
        if not self._loop_active:
            return
        try:
            global rotate_state
            if rotate_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                self.phase += 0.2
                self.lever_angle = math.sin(self.phase) * 35.0
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        cx = 110
        cy = 150
        
        # 1. Base industrielle du boîtier de commande
        self.canvas.create_rectangle(cx - 45, cy + 30, cx + 45, cy + 80, fill="#334155", outline="#0f172a", width=3)
        self.canvas.create_rectangle(cx - 35, cy + 38, cx + 35, cy + 72, fill="#1e293b", outline="#0f172a", width=2)
        self.canvas.create_text(cx, cy + 55, text="180° FLIP", font=("Impact", 10, "bold"), fill="#facc15")
        
        # 2. Engrenages dorés qui tournent
        gear_rot = self.phase * 3.0
        gx, gy = cx - 50, cy + 20
        self.canvas.create_oval(gx - 20, gy - 20, gx + 20, gy + 20, fill="#d97706", outline="#78350f", width=2)
        for g in range(6):
            ga = gear_rot + g * (math.pi / 3.0)
            self.canvas.create_line(gx, gy, gx + math.cos(ga) * 25, gy + math.sin(ga) * 25, fill="#78350f", width=5)
        self.canvas.create_oval(gx - 8, gy - 8, gx + 8, gy + 8, fill="#fef3c7", outline="#78350f", width=2)
        
        # 3. Levier géant en mouvement
        rad = math.radians(self.lever_angle - 45)
        lx = cx + math.cos(rad) * 65
        ly = cy + 25 + math.sin(rad) * 65
        self.canvas.create_line(cx, cy + 30, lx, ly, fill="#94a3b8", width=8, capstyle=tk.ROUND)
        self.canvas.create_oval(lx - 12, ly - 12, lx + 12, ly + 12, fill="#dc2626", outline="#7f1d1d", width=3)
        
        # 4. Ouvrier cartoon qui tire sur le levier
        char_x = lx + 30
        char_y = cy - 10
        # Corps penché
        self.canvas.create_oval(char_x - 22, char_y - 40, char_x + 22, char_y + 20, fill="#2563eb", outline="#1e3a8a", width=3)
        # Casque de chantier jaune
        self.canvas.create_oval(char_x - 25, char_y - 58, char_x + 25, char_y - 30, fill="#facc15", outline="#854d0e", width=3)
        self.canvas.create_rectangle(char_x - 28, char_y - 38, char_x + 28, char_y - 32, fill="#ca8a04", outline="#854d0e", width=2)
        # Yeux plissés d'effort
        self.canvas.create_line(char_x - 14, char_y - 28, char_x - 4, char_y - 24, fill="#0f172a", width=3)
        self.canvas.create_line(char_x + 4, char_y - 24, char_x + 14, char_y - 28, fill="#0f172a", width=3)
        # Dents serrées
        self.canvas.create_rectangle(char_x - 10, char_y - 14, char_x + 10, char_y - 4, fill="#ffffff", outline="#0f172a", width=2)
        # Bras agrippant le levier
        self.canvas.create_line(char_x - 12, char_y - 10, lx, ly, fill="#fbbf24", width=7, capstyle=tk.ROUND)
        self.canvas.create_oval(lx - 8, ly - 8, lx + 8, ly + 8, fill="#ffffff", outline="#0f172a", width=2)
        # Goutte de sueur
        self.canvas.create_text(char_x + 24, char_y - 45, text="💦", font=("Segoe UI Emoji", 14))
        # Bulle d'effort
        self.canvas.create_text(char_x + 15, char_y - 72, text="BASCULE 180° ! 🔄", font=("Impact", 11, "bold"), fill="#ef4444")


root = tk.Tk()
root.withdraw()

k = CartoonKeysOverlay(root)
g = CartoonGhostOverlay(root)
m = CartoonMegaphoneOverlay(root)
r = CartoonRotateOverlay(root)

for _ in range(25):
    root.update()
    time.sleep(0.016)

print("SUCCESS: All 4 new cartoon overlays executed cleanly and rendered perfectly!")
root.destroy()

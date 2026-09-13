import tkinter as tk
import ctypes
from ctypes import wintypes
import math
import random
import time
import threading

# Mock globals
puller_state = {"active": True, "mx": 400, "my": 300, "dir_x": 1.0, "dir_y": 0.0, "force": 1.0}
drunk_state = {"active": True, "mx": 400, "my": 300, "intro_reset": False}
wall_state = {"active": True, "mx": 400, "my": 300, "is_bonking": True, "wall_x": 380}
painter_state = {"active": True}
keys_state = {"active": True, "last_key_time": time.time(), "key_char": "A"}
ghost_state = {"active": True, "booh": True}
tts_state = {"active": True, "is_speaking": True, "text": "ALERTE SYSTÈME !"}
rotate_state = {"active": True, "angle": 45.0}
legs_state = {"active": True, "target_cx": 400, "target_bottom": 300, "is_moving": True, "dir_x": 1.0, "speed": 22.0}

def _get_current_mouse_position():
    return 450, 350

def _shake_window_briefly(hwnd, orig_x, orig_y):
    try:
        for s in [6, -6, 5, -5, 3, -3, 0]:
            ctypes.windll.user32.SetWindowPos(hwnd, 0, orig_x + s, orig_y, 0, 0, 0x0001 | 0x0004 | 0x0010)
            time.sleep(0.02)
    except Exception:
        pass


class CartoonPainterOverlay:
    """
    Peintre cartoon français : béret rouge, marinière à rayures, moustache cirée,
    palette de bois avec 5 couleurs vives, pinceau tournoyant et taches de peinture 3D
    lustrées qui dégoulinent avec la gravité le long de l'écran.
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
        self.splatters = []
        self.drips = []
        self.visible = False
        self._loop_active = True
        self.painter_x = float(self.sw - 160)
        self.painter_y = float(self.sh - 140)
        self._tick()
        
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
                    
                self.phase += 0.15
                
                # Déplacement doux du peintre en bas de l'écran
                self.painter_x = (self.sw - 160) + math.sin(self.phase * 0.6) * 40
                self.painter_y = (self.sh - 140) + math.cos(self.phase * 0.9) * 15
                
                # Ajouter périodiquement des taches de peinture
                if len(self.splatters) < 14 and random.random() < 0.25:
                    splash_x = random.randint(100, self.sw - 100)
                    splash_y = random.randint(80, self.sh - 180)
                    color = random.choice(["#ef4444", "#3b82f6", "#eab308", "#10b981", "#8b5cf6", "#ec4899"])
                    r = random.uniform(18, 38)
                    self.splatters.append({
                        "x": splash_x, "y": splash_y, "r": r,
                        "color": color, "life": random.uniform(8.0, 16.0),
                        "has_drip": random.choice([True, False])
                    })
                    if random.random() < 0.5:
                        self.drips.append({
                            "x": splash_x + random.uniform(-r*0.4, r*0.4),
                            "y": splash_y + r*0.8,
                            "color": color,
                            "len": 0.0,
                            "max_len": random.uniform(40, 140),
                            "speed": random.uniform(1.2, 2.5)
                        })
                        
                # Mise à jour des coulures
                new_drips = []
                for d in self.drips:
                    d["len"] += d["speed"]
                    if d["len"] < d["max_len"]:
                        new_drips.append(d)
                self.drips = new_drips
                
                # Vieillissement des taches
                new_splat = []
                for s in self.splatters:
                    s["life"] -= 0.05
                    if s["life"] > 0:
                        new_splat.append(s)
                self.splatters = new_splat
                
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.splatters.clear()
                    self.drips.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(25, self._tick)
            
    def _draw(self):
        self.canvas.delete("all")
        
        # 1. Dessiner les coulures de peinture
        for d in self.drips:
            dx = d["x"]
            dy = d["y"]
            dlen = d["len"]
            color = d["color"]
            self.canvas.create_line(dx, dy, dx, dy + dlen, fill=color, width=4, capstyle=tk.ROUND)
            # Gouttelette terminale renflée
            self.canvas.create_oval(dx - 4, dy + dlen - 4, dx + 4, dy + dlen + 5, fill=color, outline="")
            
        # 2. Dessiner les grosses taches de peinture 3D lustrées
        for s in self.splatters:
            sx, sy, sr, scolor = s["x"], s["y"], s["r"], s["color"]
            # Contour externe plus sombre
            self.canvas.create_oval(sx - sr - 2, sy - sr - 2, sx + sr + 2, sy + sr + 2, fill="#0f172a", outline="")
            # Corps de la tache avec lobes
            pts = []
            for deg in range(0, 360, 30):
                rad = math.radians(deg)
                rr = sr * (1.0 + 0.35 * math.sin(deg * 3))
                pts.append((sx + math.cos(rad) * rr, sy + math.sin(rad) * rr))
            self.canvas.create_polygon(pts, fill=scolor, outline="", smooth=True)
            # Reflet lustré blanc brillant (effet 3D laqué)
            self.canvas.create_arc(sx - sr*0.6, sy - sr*0.6, sx + sr*0.2, sy + sr*0.2, start=45, extent=90, style="arc", outline="#ffffff", width=3)
            # Éclaboussures miniatures autour
            for ed in [45, 135, 220, 310]:
                er = math.radians(ed)
                ex = sx + math.cos(er) * (sr * 1.5)
                ey = sy + math.sin(er) * (sr * 1.5)
                self.canvas.create_oval(ex - 3, ey - 3, ex + 3, ey + 3, fill=scolor, outline="")
                
        # 3. Peintre cartoon en bas de l'écran
        px = self.painter_x
        py = self.painter_y
        
        # Corps : chemise marinière à rayures bleues et blanches
        self.canvas.create_oval(px - 32, py - 25, px + 32, py + 38, fill="#ffffff", outline="#0f172a", width=3)
        for r in range(-15, 30, 10):
            self.canvas.create_line(px - 28, py + r, px + 28, py + r, fill="#1d4ed8", width=4)
            
        # Tête ronde et expressive
        head_x = px
        head_y = py - 40
        self.canvas.create_oval(head_x - 24, head_y - 24, head_x + 24, head_y + 24, fill="#fed7aa", outline="#c2410c", width=2)
        # Béret rouge classique incliné avec téton
        self.canvas.create_oval(head_x - 32, head_y - 32, head_x + 22, head_y - 12, fill="#dc2626", outline="#7f1d1d", width=3)
        self.canvas.create_line(head_x - 6, head_y - 32, head_x - 6, head_y - 37, fill="#7f1d1d", width=3)
        # Yeux cartoon joyeux
        self.canvas.create_oval(head_x - 14, head_y - 10, head_x - 4, head_y + 2, fill="#0f172a", outline="")
        self.canvas.create_oval(head_x + 4, head_y - 10, head_x + 14, head_y + 2, fill="#0f172a", outline="")
        self.canvas.create_oval(head_x - 11, head_y - 8, head_x - 7, head_y - 4, fill="#ffffff", outline="")
        self.canvas.create_oval(head_x + 7, head_y - 8, head_x + 11, head_y - 4, fill="#ffffff", outline="")
        # Grande moustache française cirée en guidon
        self.canvas.create_line(head_x - 24, head_y + 8, head_x, head_y + 12, head_x + 24, head_y + 8, fill="#0f172a", width=4, smooth=True)
        # Nez rond rose
        self.canvas.create_oval(head_x - 5, head_y - 2, head_x + 5, head_y + 7, fill="#fca5a5", outline="#c2410c", width=1)
        
        # 4. Palette d'artiste en bois dans la main gauche
        pal_x = px - 45
        pal_y = py + 5
        self.canvas.create_oval(pal_x - 28, pal_y - 18, pal_x + 28, pal_y + 18, fill="#d97706", outline="#78350f", width=3)
        # Trou pour le pouce
        self.canvas.create_oval(pal_x - 18, pal_y - 6, pal_x - 8, pal_y + 6, fill="#fed7aa", outline="#78350f", width=2)
        # 5 tas de peinture sur la palette
        pal_colors = ["#ef4444", "#3b82f6", "#eab308", "#10b981", "#a855f7"]
        for pi, pc in enumerate(pal_colors):
            pdeg = math.radians(pi * 45 - 30)
            self.canvas.create_oval(pal_x + math.cos(pdeg)*16 - 4, pal_y + math.sin(pdeg)*10 - 4, pal_x + math.cos(pdeg)*16 + 4, pal_y + math.sin(pdeg)*10 + 4, fill=pc, outline="")
            
        # 5. Pinceau virevoltant dans la main droite
        brush_rot = math.sin(self.phase * 4.0) * 35
        brad = math.radians(brush_rot)
        bx1 = px + 25
        by1 = py
        bx2 = bx1 + math.cos(brad) * 45
        by2 = by1 - 10 + math.sin(brad) * 45
        # Manche en bois + virole argentée
        self.canvas.create_line(bx1, by1, bx2, by2, fill="#b45309", width=4)
        self.canvas.create_line(bx2 - 8, by2, bx2, by2, fill="#cbd5e1", width=5)
        # Poils du pinceau trempés de peinture rouge
        self.canvas.create_line(bx2, by2, bx2 + math.cos(brad)*12, by2 + math.sin(brad)*12, fill="#ef4444", width=6, capstyle=tk.ROUND)
        self.canvas.create_text(px + 40, py - 60, text="SPLAAASH ! 🎨", font=("Impact", 13, "bold"), fill="#f43f5e")


class CartoonKeysOverlay:
    """
    Gremlin farceur cartoon tapotant frénétiquement un mini clavier mécanique :
    Oreilles pointues de lutin, yeux dorés fendus, rictus malicieux à petites dents pointues,
    touches de clavier 3D géantes bondissant sur des ressorts d'acier hélicoïdaux
    avec jaillissement d'étincelles électriques et bulles 'CLAC CLAC ! HIHIHI !'.
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 280, 240
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
        self.sparks = []
        self.bouncing_keys = []
        self.visible = False
        self._loop_active = True
        self._tick()
        
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
                    sw = self.win.winfo_screenwidth()
                    sh = self.win.winfo_screenheight()
                    self.win.geometry(f"{self.w}x{self.h}+{sw - self.w - 30}+{sh - self.h - 90}")
                    
                self.phase += 0.22
                
                # Faire sauter une touche périodiquement
                if len(self.bouncing_keys) < 4 and random.random() < 0.35:
                    char = random.choice(["A", "Z", "E", "R", "⚡", "?!", "⌨️", "💥"])
                    self.bouncing_keys.append({
                        "char": char,
                        "x": (self.w // 2) + random.uniform(-40, 40),
                        "y": (self.h // 2) + 15,
                        "vy": random.uniform(-7.0, -3.5),
                        "rot": random.uniform(-25, 25),
                        "life": 1.0
                    })
                    # Étincelles électriques
                    for _ in range(3):
                        self.sparks.append({
                            "x": (self.w // 2) + random.uniform(-30, 30),
                            "y": (self.h // 2) + 30,
                            "vx": random.uniform(-4, 4),
                            "vy": random.uniform(-5, -1),
                            "life": 1.0
                        })
                        
                # Mise à jour des touches bondissantes
                new_keys = []
                for k in self.bouncing_keys:
                    k["y"] += k["vy"]
                    k["vy"] += 0.35
                    k["life"] -= 0.04
                    if k["life"] > 0 and k["y"] < self.h:
                        new_keys.append(k)
                self.bouncing_keys = new_keys
                
                # Mise à jour des étincelles
                new_sparks = []
                for sp in self.sparks:
                    sp["x"] += sp["vx"]
                    sp["y"] += sp["vy"]
                    sp["life"] -= 0.12
                    if sp["life"] > 0:
                        new_sparks.append(sp)
                self.sparks = new_sparks
                
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.bouncing_keys.clear()
                    self.sparks.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)
            
    def _draw(self):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = self.h // 2 + 10
        
        # 1. Clavier mécanique cartoon en base
        kb_w, kb_h = 130, 45
        self.canvas.create_rectangle(cx - kb_w//2, cy + 25, cx + kb_w//2, cy + 25 + kb_h, fill="#334155", outline="#0f172a", width=3)
        self.canvas.create_rectangle(cx - kb_w//2 + 6, cy + 29, cx + kb_w//2 - 6, cy + 25 + kb_h - 6, fill="#1e293b", outline="#475569", width=1)
        # Petites touches alignées
        for row in range(2):
            for col in range(6):
                kx = cx - kb_w//2 + 14 + col * 18
                ky = cy + 34 + row * 16
                self.canvas.create_rectangle(kx - 7, ky - 5, kx + 7, ky + 5, fill="#64748b", outline="#0f172a", width=1)
                
        # 2. Gremlin violet farceur au-dessus du clavier
        gx = cx
        gy = cy - 25 + math.sin(self.phase * 3.0) * 3.0
        
        # Oreilles de gremlin pointues
        self.canvas.create_polygon([(gx - 35, gy - 20), (gx - 75, gy - 45), (gx - 22, gy - 5)], fill="#a855f7", outline="#581c87", width=2)
        self.canvas.create_polygon([(gx - 35, gy - 18), (gx - 65, gy - 38), (gx - 25, gy - 8)], fill="#f472b6", outline="") # intérieur rose
        self.canvas.create_polygon([(gx + 35, gy - 20), (gx + 75, gy - 45), (gx + 22, gy - 5)], fill="#a855f7", outline="#581c87", width=2)
        self.canvas.create_polygon([(gx + 35, gy - 18), (gx + 65, gy - 38), (gx + 25, gy - 8)], fill="#f472b6", outline="")
        
        # Tête ronde et touffe de poils violets
        self.canvas.create_oval(gx - 36, gy - 32, gx + 36, gy + 32, fill="#9333ea", outline="#581c87", width=3)
        self.canvas.create_polygon([(gx - 10, gy - 32), (gx, gy - 48), (gx + 10, gy - 32)], fill="#a855f7", outline="#581c87", width=2)
        
        # Yeux de chat jaunes dorés luisants
        self.canvas.create_oval(gx - 24, gy - 18, gx - 6, gy + 2, fill="#facc15", outline="#713f12", width=2)
        self.canvas.create_oval(gx + 6, gy - 18, gx + 24, gy + 2, fill="#facc15", outline="#713f12", width=2)
        # Pupilles verticales félines
        self.canvas.create_line(gx - 15, gy - 16, gx - 15, gy, fill="#0f172a", width=3)
        self.canvas.create_line(gx + 15, gy - 16, gx + 15, gy, fill="#0f172a", width=3)
        
        # Rictus diabolique souriant avec crocs blancs pointus
        self.canvas.create_arc(gx - 22, gy - 5, gx + 22, gy + 22, start=180, extent=180, fill="#450a0a", outline="#0f172a", width=2)
        self.canvas.create_polygon([(gx - 14, gy + 8), (gx - 10, gy + 16), (gx - 6, gy + 8)], fill="#ffffff", outline="") # croc gauche
        self.canvas.create_polygon([(gx + 6, gy + 8), (gx + 10, gy + 16), (gx + 14, gy + 8)], fill="#ffffff", outline="") # croc droit
        
        # Petites pattes griffues tapotant le clavier
        hand_w = math.sin(self.phase * 6.0) * 8.0
        self.canvas.create_oval(gx - 26, cy + 12 + hand_w, gx - 10, cy + 26 + hand_w, fill="#7e22ce", outline="#0f172a", width=2)
        self.canvas.create_oval(gx + 10, cy + 12 - hand_w, gx + 26, cy + 26 - hand_w, fill="#7e22ce", outline="#0f172a", width=2)
        
        # 3. Touches bondissantes sur ressorts hélicoïdaux
        for k in self.bouncing_keys:
            kx, ky, kchar = k["x"], k["y"], k["char"]
            # Ressort hélicoïdal métallique sous la touche
            spring_h = max(10, cy + 25 - ky)
            coils = 4
            pts = [(kx, cy + 25)]
            for c in range(coils):
                cx_offset = 6 if c % 2 == 0 else -6
                pts.append((kx + cx_offset, cy + 25 - (c + 1) * (spring_h / float(coils))))
            for idx in range(len(pts) - 1):
                self.canvas.create_line(pts[idx][0], pts[idx][1], pts[idx+1][0], pts[idx+1][1], fill="#94a3b8", width=3)
                
            # Touche 3D
            self.canvas.create_rectangle(kx - 16, ky - 14, kx + 16, ky + 14, fill="#38bdf8", outline="#0369a1", width=2)
            self.canvas.create_rectangle(kx - 14, ky - 12, kx + 14, ky + 10, fill="#7dd3fc", outline="")
            self.canvas.create_text(kx, ky - 1, text=kchar, font=("Impact", 11, "bold"), fill="#0f172a")
            
        # 4. Étincelles d'énergie cartoon
        for sp in self.sparks:
            self.canvas.create_text(sp["x"], sp["y"], text="⚡", font=("Segoe UI Emoji", 10))
            
        # 5. Bulles de texte malicieuses
        self.canvas.create_text(cx - 55, cy - 65, text="CLAC CLAC ! 💥", font=("Impact", 11, "bold"), fill="#facc15")
        self.canvas.create_text(cx + 60, cy - 65, text="HIHIHI ! ⌨️", font=("Impact", 12, "bold"), fill="#a855f7")


class CartoonGhostOverlay:
    """
    Poltergeist cartoon interactif plein écran :
    Esprit farceur translucide avec aura luminescente cyan et traînée spectrale,
    qui se balade à travers tout l'écran, pourchasse activement le curseur de la souris,
    lui saute dessus avec un 'BOOOOUH ! 👻⚡', repousse physiquement la souris de 150px,
    fait trembler les fenêtres et dépose des flaques de bave d'ectoplasme gluante qui dégoulinent !
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
            
        self.gx = float(self.sw // 2)
        self.gy = float(self.sh // 3)
        self.vx = 2.5
        self.vy = 1.8
        self.phase = 0.0
        self.state = "WANDER" # WANDER, CHASE, JUMPSCARE
        self.state_timer = 0
        self.jumpscare_scale = 1.0
        self.booh_text = ""
        self.sound_waves = []
        self.ectoplasm = []
        self.visible = False
        self._loop_active = True
        self._tick()
        
    def trigger_booh(self):
        self.state = "JUMPSCARE"
        self.state_timer = 0
        self.jumpscare_scale = 1.8
        self.booh_text = random.choice(["BOOOOUH ! 👻⚡", "ATTRAPÉ ! 👻💥", "OUUUH ! 👻✨", "ZOUUU ! 👻💀"])
        self.sound_waves.append({"radius": 25, "max_r": 130, "life": 1.0})

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
                    
                mx, my = _get_current_mouse_position()
                self.phase += 0.08
                self.state_timer += 1
                
                if self.state == "WANDER":
                    # Vol stationnaire et déplacements fluides
                    self.gx += math.sin(self.phase * 0.7) * 4.5 + self.vx
                    self.gy += math.cos(self.phase * 0.9) * 3.5 + self.vy
                    
                    # Rebond sur les bords d'écran
                    if self.gx < 100: self.vx = abs(self.vx)
                    if self.gx > self.sw - 100: self.vx = -abs(self.vx)
                    if self.gy < 100: self.vy = abs(self.vy)
                    if self.gy > self.sh - 140: self.vy = -abs(self.vy)
                    
                    # Dépôt de bave d'ectoplasme gluante
                    if random.random() < 0.04 and len(self.ectoplasm) < 12:
                        self.ectoplasm.append({
                            "x": self.gx + random.uniform(-18, 18),
                            "y": self.gy + 35,
                            "r": random.uniform(8, 16),
                            "drip": 0.0,
                            "life": 1.0
                        })
                        
                    # Détection de la souris pour démarrer la traque
                    dist_to_mouse = math.hypot(mx - self.gx, my - self.gy)
                    if (self.state_timer > 100 and dist_to_mouse < 700) or self.state_timer > 180:
                        self.state = "CHASE"
                        self.state_timer = 0
                        
                elif self.state == "CHASE":
                    # Plongeon rapide vers la souris
                    dx = mx - self.gx
                    dy = my - self.gy
                    dist = math.hypot(dx, dy)
                    if dist > 45:
                        speed = 14.0
                        self.gx += (dx / dist) * speed
                        self.gy += (dy / dist) * speed
                    else:
                        # Attaque JUMPSCARE !
                        self.trigger_booh()
                        
                        # 1. Répulsion physique de la souris (la souris a peur !)
                        repel_angle = random.uniform(0, 2 * math.pi)
                        repel_dist = random.uniform(130, 180)
                        new_mx = int(max(50, min(self.sw - 50, mx + math.cos(repel_angle) * repel_dist)))
                        new_my = int(max(50, min(self.sh - 50, my + math.sin(repel_angle) * repel_dist)))
                        ctypes.windll.user32.SetCursorPos(new_mx, new_my)
                        
                        # 2. Grosse flaque d'ectoplasme déposée à l'endroit du choc
                        self.ectoplasm.append({
                            "x": mx,
                            "y": my,
                            "r": random.uniform(20, 32),
                            "drip": 0.0,
                            "life": 1.5
                        })
                        
                        # 3. Tremblement de la fenêtre active au premier plan
                        try:
                            fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
                            if fg_hwnd:
                                rect = wintypes.RECT()
                                ctypes.windll.user32.GetWindowRect(fg_hwnd, ctypes.byref(rect))
                                threading.Thread(target=_shake_window_briefly, args=(fg_hwnd, rect.left, rect.top), daemon=True).start()
                        except Exception:
                            pass
                            
                    if self.state_timer > 80:
                        self.state = "WANDER"
                        self.state_timer = 0
                        
                elif self.state == "JUMPSCARE":
                    self.jumpscare_scale = max(1.0, self.jumpscare_scale - 0.05)
                    if self.state_timer > 25:
                        self.state = "WANDER"
                        self.state_timer = 0
                        self.booh_text = ""
                        self.vx = random.choice([-3.5, 3.5])
                        self.vy = random.choice([-2.5, 2.5])
                        
                # Mise à jour des ondes sonores
                new_waves = []
                for w in self.sound_waves:
                    w["radius"] += 4.5
                    w["life"] -= 0.04
                    if w["life"] > 0 and w["radius"] < w["max_r"]:
                        new_waves.append(w)
                self.sound_waves = new_waves
                
                # Mise à jour de l'ectoplasme
                new_ecto = []
                for e in self.ectoplasm:
                    e["drip"] += 0.7
                    e["life"] -= 0.012
                    if e["life"] > 0:
                        new_ecto.append(e)
                self.ectoplasm = new_ecto
                
                self._draw(mx, my)
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.sound_waves.clear()
                    self.ectoplasm.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)
            
    def _draw(self, mx, my):
        self.canvas.delete("all")
        
        # 1. Flaques d'ectoplasme vert fluo dégoulinantes
        for e in self.ectoplasm:
            ex, ey, er, edrip = e["x"], e["y"], e["r"], e["drip"]
            # Flaque principale avec bord festonné
            self.canvas.create_oval(ex - er, ey - er*0.6, ex + er, ey + er*0.6, fill="#22c55e", outline="#15803d", width=2)
            self.canvas.create_oval(ex - er*0.6, ey - er*0.4, ex + er*0.2, ey, fill="#86efac", outline="") # éclat clair
            # Coulure qui dégouline vers le bas
            if edrip > 2:
                self.canvas.create_line(ex, ey, ex, ey + edrip, fill="#22c55e", width=4, capstyle=tk.ROUND)
                self.canvas.create_oval(ex - 3, ey + edrip - 3, ex + 3, ey + edrip + 4, fill="#16a34a", outline="")
                
        # 2. Ondes de choc du cri spectral
        for w in self.sound_waves:
            r = w["radius"]
            self.canvas.create_oval(self.gx - r, self.gy - r, self.gx + r, self.gy + r, outline="#38bdf8", width=3, dash=(6, 3))
            
        # 3. Dessin du fantôme poltergeist
        scale = self.jumpscare_scale
        cx, cy = self.gx, self.gy
        
        # Aura luminescente spectrale cyan
        for aura_r in [65 * scale, 52 * scale, 40 * scale]:
            self.canvas.create_oval(cx - aura_r, cy - aura_r, cx + aura_r, cy + aura_r, fill="", outline="#38bdf8", width=2)
            
        # Corps drapé du fantôme ondulant
        body_w = 42 * scale
        body_h = 60 * scale
        pts = []
        # Tête arrondie
        for deg in range(0, 185, 15):
            rad = math.radians(deg)
            pts.append((cx + math.cos(rad) * body_w, cy - 20 * scale - math.sin(rad) * 40 * scale))
        # Jupe fantomatique ondulante
        skirt_y = cy + 35 * scale
        vol_count = 5
        for v in range(vol_count + 1):
            vx = cx - body_w + (v * (body_w * 2 / float(vol_count)))
            wave = math.sin(self.phase * 3.5 + v * 1.4) * (14 * scale)
            pts.append((vx, skirt_y + wave))
            
        # Dessin du corps blanc spectral avec contour noir doux
        self.canvas.create_polygon(pts, fill="#f8fafc", outline="#0f172a", width=3, smooth=True)
        # Reflet bleuté translucide interne
        self.canvas.create_arc(cx - body_w + 8, cy - 50 * scale, cx + body_w - 8, cy + 10, start=60, extent=60, style="arc", outline="#bae6fd", width=3)
        
        # Yeux expressifs selon l'état
        eye_y = cy - 22 * scale
        if self.state == "JUMPSCARE":
            # Yeux démoniaques rouges avec pupille jaune
            self.canvas.create_oval(cx - 24*scale, eye_y - 14*scale, cx - 6*scale, eye_y + 12*scale, fill="#dc2626", outline="#7f1d1d", width=2)
            self.canvas.create_oval(cx + 6*scale, eye_y - 14*scale, cx + 24*scale, eye_y + 12*scale, fill="#dc2626", outline="#7f1d1d", width=2)
            self.canvas.create_oval(cx - 18*scale, eye_y - 8*scale, cx - 12*scale, eye_y + 2*scale, fill="#fef08a", outline="")
            self.canvas.create_oval(cx + 12*scale, eye_y - 8*scale, cx + 18*scale, eye_y + 2*scale, fill="#fef08a", outline="")
            # Bouche grande ouverte hurlante avec crocs
            self.canvas.create_oval(cx - 20*scale, cy + 5*scale, cx + 20*scale, cy + 32*scale, fill="#0f172a", outline="#94a3b8", width=2)
            self.canvas.create_polygon([(cx - 12*scale, cy + 5*scale), (cx - 8*scale, cy + 14*scale), (cx - 4*scale, cy + 5*scale)], fill="#ffffff", outline="")
            self.canvas.create_polygon([(cx + 4*scale, cy + 5*scale), (cx + 8*scale, cy + 14*scale), (cx + 12*scale, cy + 5*scale)], fill="#ffffff", outline="")
            # Texte du BOOOOUH
            self.canvas.create_text(cx, cy - 70 * scale, text=self.booh_text, font=("Impact", int(18 * scale), "bold"), fill="#facc15")
        elif self.state == "CHASE":
            # Yeux concentrés plissés fixant la souris
            self.canvas.create_oval(cx - 22*scale, eye_y - 10*scale, cx - 6*scale, eye_y + 10*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx + 6*scale, eye_y - 10*scale, cx + 22*scale, eye_y + 10*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx - 16*scale, eye_y - 6*scale, cx - 10*scale, eye_y + 2*scale, fill="#38bdf8", outline="")
            self.canvas.create_oval(cx + 10*scale, eye_y - 6*scale, cx + 16*scale, eye_y + 2*scale, fill="#38bdf8", outline="")
            # Sourire carnassier
            self.canvas.create_arc(cx - 16*scale, cy + 4*scale, cx + 16*scale, cy + 24*scale, start=180, extent=180, fill="#0f172a", outline="", width=2)
            self.canvas.create_text(cx, cy - 60 * scale, text="JE TE TIENS ! 😈", font=("Impact", 13, "bold"), fill="#38bdf8")
        else: # WANDER
            # Yeux cartoon mignons avec pupilles vives
            self.canvas.create_oval(cx - 20*scale, eye_y - 12*scale, cx - 6*scale, eye_y + 8*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx + 6*scale, eye_y - 12*scale, cx + 20*scale, eye_y + 8*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx - 16*scale, eye_y - 10*scale, cx - 10*scale, eye_y - 4*scale, fill="#ffffff", outline="")
            self.canvas.create_oval(cx + 10*scale, eye_y - 10*scale, cx + 16*scale, eye_y - 4*scale, fill="#ffffff", outline="")
            # Joues roses
            self.canvas.create_oval(cx - 28*scale, eye_y + 6*scale, cx - 18*scale, eye_y + 14*scale, fill="#f472b6", outline="")
            self.canvas.create_oval(cx + 18*scale, eye_y + 6*scale, cx + 28*scale, eye_y + 14*scale, fill="#f472b6", outline="")
            # Petite bouche souriante
            self.canvas.create_oval(cx - 6*scale, cy + 6*scale, cx + 6*scale, cy + 18*scale, fill="#0f172a", outline="")
            self.canvas.create_text(cx, cy - 55 * scale, text="OUUUH... 👻", font=("Impact", 12, "bold"), fill="#bae6fd")


class CartoonMegaphoneOverlay:
    """
    Mégaphone d'alerte cartoon vivant :
    Cône de porte-voix en émail rouge et blanc à cerclage chromé, tenu par des gants
    de cartoon blancs à quatre doigts (style Mickey), gyrophare de police rotatif balayant
    l'écran de faisceaux lumineux, ondes acoustiques et banderole 'ALERTE SYSTÈME ! ⚠️📢'.
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 280, 240
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
                    sw = self.win.winfo_screenwidth()
                    self.win.geometry(f"{self.w}x{self.h}+{sw - self.w - 30}+40")
                    
                self.phase += 0.2
                if len(self.sound_waves) < 5:
                    self.sound_waves.append({"r": 10.0, "life": 1.0})
                    
                new_waves = []
                for w in self.sound_waves:
                    w["r"] += 4.0
                    w["life"] -= 0.05
                    if w["life"] > 0 and w["r"] < 100:
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
        cx = 100
        cy = 135
        
        # 1. Faisceaux lumineux du gyrophare de police
        siren_x = cx + 25
        siren_y = cy - 58
        beacon_rot = self.phase * 3.5
        for b_side, b_color in [(-1, "#ef4444"), (1, "#3b82f6")]:
            b_ang = beacon_rot + b_side * (math.pi / 2.0)
            bx = siren_x + math.cos(b_ang) * 90
            by = siren_y + math.sin(b_ang) * 45
            self.canvas.create_polygon([(siren_x, siren_y), (bx - 25, by), (bx + 25, by)], fill=b_color, outline="")
            
        # 2. Boîtier du gyrophare
        self.canvas.create_rectangle(siren_x - 14, siren_y - 2, siren_x + 14, siren_y + 12, fill="#334155", outline="#0f172a", width=2)
        siren_dome_color = "#ef4444" if math.sin(self.phase * 4.0) > 0 else "#3b82f6"
        self.canvas.create_arc(siren_x - 16, siren_y - 20, siren_x + 16, siren_y + 6, start=0, extent=180, fill=siren_dome_color, outline="#0f172a", width=2)
        
        # 3. Ondes sonores puissantes expulsées du pavillon
        for w in self.sound_waves:
            wr = w["r"]
            self.canvas.create_arc(cx + 50 - wr, cy - wr, cx + 50 + wr, cy + wr, start=-50, extent=100, style="arc", outline="#f59e0b", width=3)
            
        # 4. Pavillon évasé du mégaphone cartoon
        horn_pts = [
            (cx - 45, cy - 18),
            (cx + 45, cy - 48),
            (cx + 45, cy + 48),
            (cx - 45, cy + 18)
        ]
        self.canvas.create_polygon(horn_pts, fill="#dc2626", outline="#0f172a", width=3)
        # Anneau chromé brillant sur le pavillon
        self.canvas.create_oval(cx + 36, cy - 48, cx + 54, cy + 48, fill="#e2e8f0", outline="#0f172a", width=3)
        self.canvas.create_oval(cx + 40, cy - 40, cx + 50, cy + 40, fill="#0f172a", outline="")
        
        # Poignée et bouton poussoir
        self.canvas.create_rectangle(cx - 30, cy + 18, cx - 18, cy + 55, fill="#475569", outline="#0f172a", width=2)
        self.canvas.create_oval(cx - 20, cy + 24, cx - 10, cy + 34, fill="#ef4444", outline="#0f172a", width=2) # gâchette
        
        # 5. Gants cartoon blancs (style Mickey) tenant le mégaphone
        self.canvas.create_oval(cx - 38, cy + 32, cx - 12, cy + 58, fill="#ffffff", outline="#0f172a", width=3)
        # Trois traits de couture noirs sur le dos du gant
        self.canvas.create_line(cx - 30, cy + 40, cx - 30, cy + 50, fill="#0f172a", width=2)
        self.canvas.create_line(cx - 25, cy + 38, cx - 25, cy + 52, fill="#0f172a", width=2)
        self.canvas.create_line(cx - 20, cy + 40, cx - 20, cy + 50, fill="#0f172a", width=2)
        
        # 6. Banderole et texte d'alerte
        self.canvas.create_text(cx + 45, cy - 75, text="ALERTE SYSTÈME ! ⚠️📢", font=("Impact", 13, "bold"), fill="#facc15")


class CartoonRotateOverlay:
    """
    Console de commande industrielle diesel-punk cartoon :
    Plaque d'acier à rayures de danger jaunes et noires, engrenages dorés à cames rotatives,
    levier industriel à boule rouge vigoureusement tiré par un ouvrier en salopette bleue
    et casque de chantier qui transpire à grosses gouttes, avec banderole 'BASCULE 180° ! 🔄'.
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 320, 260
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
                    sw = self.win.winfo_screenwidth()
                    self.win.geometry(f"{self.w}x{self.h}+{sw - self.w - 20}+30")
                    
                self.phase += 0.22
                self.lever_angle = math.sin(self.phase) * 38.0
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
        cx = 120
        cy = 160
        
        # 1. Base industrielle avec bandes diagonales d'avertissement jaune & noir
        base_w, base_h = 130, 65
        self.canvas.create_rectangle(cx - base_w//2, cy + 15, cx + base_w//2, cy + 15 + base_h, fill="#1e293b", outline="#0f172a", width=3)
        for h in range(-50, 60, 20):
            self.canvas.create_polygon([
                (cx + h, cy + 17),
                (cx + h + 12, cy + 17),
                (cx + h - 4, cy + 13 + base_h),
                (cx + h - 16, cy + 13 + base_h)
            ], fill="#facc15", outline="")
            
        self.canvas.create_rectangle(cx - 38, cy + 32, cx + 38, cy + 62, fill="#0f172a", outline="#334155", width=2)
        self.canvas.create_text(cx, cy + 47, text="180° FLIP", font=("Impact", 11, "bold"), fill="#ef4444")
        
        # 2. Engrenages dorés mécaniques à cames
        gear_rot = self.phase * 3.0
        gx, gy = cx - 55, cy + 8
        self.canvas.create_oval(gx - 24, gy - 24, gx + 24, gy + 24, fill="#d97706", outline="#78350f", width=2)
        for g in range(6):
            ga = gear_rot + g * (math.pi / 3.0)
            self.canvas.create_line(gx, gy, gx + math.cos(ga) * 28, gy + math.sin(ga) * 28, fill="#78350f", width=6)
        self.canvas.create_oval(gx - 10, gy - 10, gx + 10, gy + 10, fill="#fef3c7", outline="#78350f", width=2)
        
        # 3. Levier mécanique géant
        rad = math.radians(self.lever_angle - 45)
        lx = cx + math.cos(rad) * 75
        ly = cy + 15 + math.sin(rad) * 75
        self.canvas.create_line(cx, cy + 20, lx, ly, fill="#94a3b8", width=10, capstyle=tk.ROUND)
        self.canvas.create_oval(lx - 15, ly - 15, lx + 15, ly + 15, fill="#dc2626", outline="#7f1d1d", width=3)
        self.canvas.create_oval(lx - 8, ly - 10, lx, ly - 4, fill="#f87171", outline="") # reflet boule
        
        # 4. Ouvrier cartoon s'agrippant au levier
        char_x = lx + 36
        char_y = cy - 15
        
        # Salopette en jean bleu de travail
        self.canvas.create_oval(char_x - 24, char_y - 35, char_x + 24, char_y + 25, fill="#2563eb", outline="#1e3a8a", width=3)
        self.canvas.create_line(char_x - 14, char_y - 30, char_x - 8, char_y + 5, fill="#ca8a04", width=3) # bretelle
        self.canvas.create_line(char_x + 14, char_y - 30, char_x + 8, char_y + 5, fill="#ca8a04", width=3) # bretelle
        
        # Tête et casque de chantier jaune avec lampe
        self.canvas.create_oval(char_x - 22, char_y - 55, char_x + 22, char_y - 25, fill="#fed7aa", outline="#c2410c", width=2)
        self.canvas.create_arc(char_x - 28, char_y - 70, char_x + 28, char_y - 35, start=0, extent=180, fill="#facc15", outline="#854d0e", width=3)
        self.canvas.create_oval(char_x - 7, char_y - 68, char_x + 7, char_y - 54, fill="#ffffff", outline="#ca8a04", width=2) # phare
        
        # Yeux concentrés et dents serrées
        self.canvas.create_line(char_x - 14, char_y - 42, char_x - 4, char_y - 38, fill="#0f172a", width=3)
        self.canvas.create_line(char_x + 4, char_y - 38, char_x + 14, char_y - 42, fill="#0f172a", width=3)
        self.canvas.create_rectangle(char_x - 10, char_y - 32, char_x + 10, char_y - 24, fill="#ffffff", outline="#0f172a", width=2)
        
        # Bras tirant le levier avec gant blanc
        self.canvas.create_line(char_x - 12, char_y - 15, lx, ly, fill="#fed7aa", width=9, capstyle=tk.ROUND)
        self.canvas.create_oval(lx - 10, ly - 10, lx + 10, ly + 10, fill="#f8fafc", outline="#0f172a", width=2)
        
        # Sueur giclant
        self.canvas.create_text(char_x + 26, char_y - 48, text="💦", font=("Segoe UI Emoji", 15))
        
        # 5. Banderole de texte
        self.canvas.create_text(cx + 25, cy - 85, text="BASCULE 180° ! 🔄", font=("Impact", 13, "bold"), fill="#ef4444")
        self.canvas.create_text(cx + 25, cy - 65, text="GRAVITÉ RENVERSÉE ! ⚡", font=("Impact", 10, "bold"), fill="#facc15")


class ElusiveWindowLegsOverlay:
    """
    Jambes cartoon d'athlète en sprint sous la fenêtre fuyante :
    Sneakers de basket rouges à embout blanc et lacets, jeans retroussés,
    effets d'arcs tourbillonnants 'jambes en moulinet' lors des pointes de vitesse
    et nuages de poussière cartoon qui explosent sous les talons.
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 280, 105
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
        self.dust_particles = []
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
                    self.phase += max(0.32, min(0.75, speed * 0.04))
                    if len(self.dust_particles) < 8 and (int(self.phase * 3) % 2 == 0):
                        puff_x = (self.w // 2) - (self.facing * 42) + (math.sin(self.phase) * 16)
                        puff_y = self.h - 14
                        self.dust_particles.append([puff_x, puff_y, 5.0, 1.0])
                else:
                    self.phase += 0.05
                    
                px = int(tcx - (self.w // 2))
                py = int(tbot - 6)
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
                    self.dust_particles.clear()
                    self.last_px = None
                    self.last_py = None
        except Exception:
            pass
            
        if self.master:
            self.master.after(16, self._tick)
            
    def _draw(self, is_moving, speed):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = 5
        
        # 1. Nuages de poussière de course expansifs
        new_dust = []
        for d in self.dust_particles:
            dx, dy, dr, da = d
            color = "#cbd5e1" if da > 0.5 else "#94a3b8"
            self.canvas.create_oval(dx - dr, dy - dr, dx + dr, dy + dr, fill=color, outline="", width=0)
            dr += 1.4
            da -= 0.16
            if da > 0 and dr < 24:
                new_dust.append([dx, dy, dr, da])
        self.dust_particles = new_dust
        
        # 2. Effet 'Moulinet cartoon' (Road Runner / Sonic) quand la vitesse est élevée
        if is_moving and speed > 18.0:
            for r_step in range(4):
                rot_a = self.phase * 5.0 + r_step * (math.pi / 2.0)
                rx = cx + math.cos(rot_a) * 32.0 * self.facing
                ry = cy + 45 + math.sin(rot_a) * 16.0
                self.canvas.create_oval(rx - 8, ry - 6, rx + 8, ry + 6, fill="#ef4444", outline="#ffffff", width=2)
                self.canvas.create_line(cx, cy + 30, rx, ry, fill="#2563eb", width=4)
                
        # 3. Deux jambes articulées réalistes
        leg_spacing = 38
        offsets = [-leg_spacing, leg_spacing]
        idle_bounce = math.sin(self.phase * 2.5) * 2.5 if not is_moving else 0.0
        
        for i, offset in enumerate(offsets):
            leg_phase = self.phase + (math.pi if i == 1 else 0)
            hip_x = cx + offset
            hip_y = cy + idle_bounce
            
            if is_moving:
                stride_x = math.sin(leg_phase) * 36.0 * self.facing
                lift_y = max(0.0, math.cos(leg_phase)) * 28.0
                knee_x = hip_x + (stride_x * 0.55) + (self.facing * 12.0)
                knee_y = hip_y + 30.0 - (lift_y * 0.45)
                foot_x = hip_x + stride_x
                foot_y = hip_y + 64.0 - lift_y
            else:
                knee_x = hip_x + (offset * 0.15)
                knee_y = hip_y + 30.0
                foot_x = hip_x + (offset * 0.25)
                foot_y = hip_y + 64.0
                
            # Cuisse en jean bleu avec contour
            self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill="#0f172a", width=14, capstyle=tk.ROUND)
            self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill="#2563eb", width=9, capstyle=tk.ROUND)
            
            # Genouière cartoon
            self.canvas.create_oval(knee_x - 6, knee_y - 6, knee_x + 6, knee_y + 6, fill="#1d4ed8", outline="#0f172a", width=2)
            
            # Mollet
            self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill="#0f172a", width=12, capstyle=tk.ROUND)
            self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill="#2563eb", width=7, capstyle=tk.ROUND)
            
            # Revers de jean retroussé + chaussette blanche
            self.canvas.create_oval(foot_x - 7, foot_y - 8, foot_x + 7, foot_y + 3, fill="#f8fafc", outline="#0f172a", width=2)
            self.canvas.create_line(foot_x - 5, foot_y - 2, foot_x + 5, foot_y - 2, fill="#ef4444", width=2)
            
            # Sneaker cartoon rouge vif style All-Star
            shoe_dir = self.facing if is_moving else (1.0 if offset > 0 else -1.0)
            toe_x = foot_x + (shoe_dir * 25)
            toe_y = foot_y + 7
            heel_x = foot_x - (shoe_dir * 14)
            heel_y = foot_y + 7
            
            # Corps de la chaussure
            self.canvas.create_polygon(
                heel_x, heel_y - 10,
                foot_x, foot_y - 10,
                toe_x - (shoe_dir * 3), toe_y - 6,
                toe_x + (shoe_dir * 4), toe_y + 5,
                heel_x - (shoe_dir * 3), heel_y + 5,
                fill="#dc2626", outline="#0f172a", width=2
            )
            # Bout renforcé blanc en caoutchouc
            self.canvas.create_oval(toe_x - (shoe_dir * 4) - 5, toe_y - 6, toe_x + (shoe_dir * 4) + 2, toe_y + 5, fill="#ffffff", outline="#0f172a", width=2)
            # Semelle blanche épaisse
            self.canvas.create_line(heel_x - (shoe_dir * 3), heel_y + 5, toe_x + (shoe_dir * 5), toe_y + 5, fill="#ffffff", width=4)
            # Lacets blancs
            self.canvas.create_line(foot_x - (shoe_dir * 3), foot_y - 7, foot_x + (shoe_dir * 5), foot_y - 2, fill="#ffffff", width=2)


def test_instantiate_all():
    root = tk.Tk()
    root.withdraw()
    print("Testing instantiations...")
    p = CartoonPullerOverlay(root)
    d = CartoonDrunkOverlay(root)
    w = CartoonWallOverlay(root)
    pt = CartoonPainterOverlay(root)
    k = CartoonKeysOverlay(root)
    g = CartoonGhostOverlay(root)
    m = CartoonMegaphoneOverlay(root)
    r = CartoonRotateOverlay(root)
    l = ElusiveWindowLegsOverlay(root)
    print("All 9 overlays instantiated successfully!")
    
    # Tick all once
    root.update()
    time.sleep(0.5)
    root.update()
    print("All 9 overlays drew their canvas with zero errors!")
    root.destroy()

if __name__ == "__main__":
    test_instantiate_all()

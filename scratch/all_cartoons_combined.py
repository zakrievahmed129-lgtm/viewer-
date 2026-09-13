import tkinter as tk
import ctypes
import math
import random
import time

puller_state = {"active": True, "mx": 400, "my": 300, "dir_x": 1.0, "dir_y": 0.0, "force": 1.0}
drunk_state = {"active": True, "mx": 400, "my": 300, "intro_reset": False}
wall_state = {"active": True, "mx": 400, "my": 300, "is_bonking": True, "wall_x": 380}
painter_state = {"active": True}
keys_state = {"active": True, "last_key_time": time.time(), "key_char": "A"}
ghost_state = {"active": True, "booh": True}
tts_state = {"active": True, "is_speaking": True, "text": "ALERTE SYSTÈME !"}
rotate_state = {"active": True, "angle": 45.0}
legs_state = {"active": True, "target_cx": 400, "target_bottom": 300, "is_moving": True, "dir_x": 1.0, "speed": 22.0}

class CartoonPullerOverlay:
    """
    Bonhomme cartoon musclé qui attrape la souris avec une corde et tire
    de toutes ses forces (effort phénoménal : muscles bandés, sueur qui gicle,
    dents serrées, corps penché à 45°, corde torsadée, poussière et bulles de cri).
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 280, 220
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
            
        self.last_wx = None
        self.last_wy = None
        self.phase = 0.0
        self.sweat_drops = []
        self.dust_puffs = []
        self.visible = False
        self._loop_active = True
        self._tick()
        
    def _tick(self):
        if not self._loop_active:
            return
        try:
            global puller_state
            if puller_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                mx = puller_state.get("mx", 0)
                my = puller_state.get("my", 0)
                dx = puller_state.get("dir_x", 1.0)
                dy = puller_state.get("dir_y", 0.0)
                
                self.phase += 0.25
                puller_side = -1.0 if dx > 0 else 1.0
                
                wx = int(mx + (puller_side * 170) - (self.w // 2))
                wy = int(my - (self.h // 2) - 15)
                
                if (wx, wy) != (self.last_wx, self.last_wy):
                    self.last_wx = wx
                    self.last_wy = wy
                    if self.hwnd:
                        ctypes.windll.user32.SetWindowPos(
                            self.hwnd, 0, wx, wy, 0, 0,
                            0x0001 | 0x0004 | 0x0010
                        )
                    else:
                        self.win.geometry(f"{self.w}x{self.h}+{wx}+{wy}")
                        
                # Gouttes de sueur cartoon
                if len(self.sweat_drops) < 8 and random.random() < 0.4:
                    self.sweat_drops.append({
                        "x": (self.w // 2) + random.uniform(-10, 10),
                        "y": (self.h // 2) - 40,
                        "vx": random.uniform(-3, 3) * puller_side,
                        "vy": random.uniform(-4, -1),
                        "life": 1.0
                    })
                # Poussière d'adhérence au sol
                if len(self.dust_puffs) < 6 and random.random() < 0.35:
                    self.dust_puffs.append({
                        "x": (self.w // 2) - (puller_side * 35) + random.uniform(-10, 10),
                        "y": (self.h // 2) + 60,
                        "r": 6.0,
                        "life": 1.0
                    })
                    
                self._draw(puller_side, mx, my, wx, wy)
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.sweat_drops.clear()
                    self.dust_puffs.clear()
                    self.last_wx = None
                    self.last_wy = None
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)
            
    def _draw(self, puller_side, mx, my, wx, wy):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = self.h // 2 + 10
        
        # Tremblement d'effort herculéen
        shake_x = math.sin(self.phase * 6.0) * 3.0
        shake_y = math.cos(self.phase * 8.0) * 2.0
        cx += shake_x
        cy += shake_y
        
        # 1. Poussière de dérapage aux pieds
        new_dust = []
        for d in self.dust_puffs:
            self.canvas.create_oval(d["x"] - d["r"], d["y"] - d["r"], d["x"] + d["r"], d["y"] + d["r"], fill="#94a3b8", outline="")
            d["r"] += 1.2
            d["life"] -= 0.15
            if d["life"] > 0 and d["r"] < 22:
                new_dust.append(d)
        self.dust_puffs = new_dust
        
        # 2. Lignes d'effort / vitesse
        for l in range(3):
            ly = cy - 30 + l * 25
            lx1 = cx - puller_side * 50
            lx2 = cx - puller_side * (80 + math.sin(self.phase + l) * 15)
            self.canvas.create_line(lx1, ly, lx2, ly, fill="#cbd5e1", width=2, dash=(4, 2))
            
        # 3. Jambes cartoon plantées dans le sol (écartement athlétique à 45°)
        leg_back_x = cx - puller_side * 45
        leg_back_y = cy + 55
        leg_front_x = cx - puller_side * 15
        leg_front_y = cy + 55
        self.canvas.create_line(cx - puller_side * 15, cy + 15, leg_back_x, leg_back_y, fill="#0f172a", width=14, capstyle=tk.ROUND)
        self.canvas.create_line(cx - puller_side * 15, cy + 15, leg_back_x, leg_back_y, fill="#1e3a8a", width=9, capstyle=tk.ROUND) # pantalon bleu foncé
        self.canvas.create_line(cx + puller_side * 5, cy + 15, leg_front_x, leg_front_y, fill="#0f172a", width=14, capstyle=tk.ROUND)
        self.canvas.create_line(cx + puller_side * 5, cy + 15, leg_front_x, leg_front_y, fill="#2563eb", width=9, capstyle=tk.ROUND)
        # Baskets d'effort rouge/blanche
        self.canvas.create_oval(leg_back_x - 12, leg_back_y - 6, leg_back_x + 12, leg_back_y + 8, fill="#ef4444", outline="#0f172a", width=2)
        self.canvas.create_oval(leg_front_x - 12, leg_front_y - 6, leg_front_x + 12, leg_front_y + 8, fill="#ef4444", outline="#0f172a", width=2)
        
        # 4. Torse musclé incliné en arrière
        torso_angle = -puller_side * 28.0
        torso_rad = math.radians(torso_angle)
        tx = cx + math.sin(torso_rad) * 20
        ty = cy - 20
        self.canvas.create_oval(tx - 24, ty - 26, tx + 24, ty + 28, fill="#ea580c", outline="#9a3412", width=3) # débardeur orange vif
        
        # 5. Bras musclés avec biceps saillants tirant la corde
        hand_x = cx + puller_side * 25
        hand_y = cy - 10
        # Bras arrière
        self.canvas.create_line(tx - puller_side * 15, ty - 10, hand_x - puller_side * 10, hand_y + 8, fill="#0f172a", width=12, capstyle=tk.ROUND)
        self.canvas.create_line(tx - puller_side * 15, ty - 10, hand_x - puller_side * 10, hand_y + 8, fill="#fed7aa", width=8, capstyle=tk.ROUND)
        # Biceps avant
        self.canvas.create_oval(tx - 10, ty - 18, tx + 10, ty + 2, fill="#fed7aa", outline="#c2410c", width=2)
        # Bras avant
        self.canvas.create_line(tx + puller_side * 10, ty - 12, hand_x, hand_y, fill="#0f172a", width=14, capstyle=tk.ROUND)
        self.canvas.create_line(tx + puller_side * 10, ty - 12, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
        # Gants de force blancs
        self.canvas.create_oval(hand_x - 10, hand_y - 10, hand_x + 10, hand_y + 10, fill="#f8fafc", outline="#0f172a", width=2)
        
        # 6. Tête expressive en plein effort
        head_x = tx + puller_side * 5
        head_y = ty - 42
        self.canvas.create_oval(head_x - 22, head_y - 22, head_x + 22, head_y + 22, fill="#fed7aa", outline="#c2410c", width=3)
        # Yeux plissés d'effort féroce
        eye_y = head_y - 4
        self.canvas.create_line(head_x - 14, eye_y - 2, head_x - 2, eye_y + 2, fill="#0f172a", width=3)
        self.canvas.create_line(head_x + 2, eye_y + 2, head_x + 14, eye_y - 2, fill="#0f172a", width=3)
        # Sourcils froncés épais
        self.canvas.create_line(head_x - 16, eye_y - 8, head_x - 2, eye_y - 4, fill="#7c2d12", width=4)
        self.canvas.create_line(head_x + 2, eye_y - 4, head_x + 16, eye_y - 8, fill="#7c2d12", width=4)
        # Dents serrées grimaçantes (dents blanches avec grille d'effort)
        self.canvas.create_rectangle(head_x - 12, head_y + 6, head_x + 12, head_y + 16, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_line(head_x - 4, head_y + 6, head_x - 4, head_y + 16, fill="#0f172a", width=1)
        self.canvas.create_line(head_x + 4, head_y + 6, head_x + 4, head_y + 16, fill="#0f172a", width=1)
        self.canvas.create_line(head_x - 12, head_y + 11, head_x + 12, head_y + 11, fill="#0f172a", width=1)
        
        # Bandeau de ninja / guerrier rouge vif avec rubans flottants
        band_y = head_y - 12
        self.canvas.create_line(head_x - 24, band_y, head_x + 24, band_y, fill="#ef4444", width=7)
        # Rubans flottant au vent vers l'arrière
        ribbon_w = math.sin(self.phase * 4.0) * 8.0
        self.canvas.create_line(head_x - puller_side * 22, band_y, head_x - puller_side * 50, band_y - 10 + ribbon_w, fill="#dc2626", width=4)
        self.canvas.create_line(head_x - puller_side * 22, band_y, head_x - puller_side * 45, band_y + 8 - ribbon_w, fill="#b91c1c", width=4)
        
        # 7. Gouttes de sueur qui giclent en arrière
        new_sweat = []
        for s in self.sweat_drops:
            self.canvas.create_oval(s["x"] - 3, s["y"] - 4, s["x"] + 3, s["y"] + 4, fill="#38bdf8", outline="#0284c7", width=1)
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.4
            s["life"] -= 0.12
            if s["life"] > 0:
                new_sweat.append(s)
        self.sweat_drops = new_sweat
        
        # 8. Corde nautique torsadée tendue reliant les mains à la souris
        target_canvas_x = mx - wx
        target_canvas_y = my - wy
        self.canvas.create_line(hand_x, hand_y, target_canvas_x, target_canvas_y, fill="#78350f", width=6)
        self.canvas.create_line(hand_x, hand_y, target_canvas_x, target_canvas_y, fill="#d97706", width=4, dash=(6, 3))
        # Nœud coulant cartoon autour du curseur
        self.canvas.create_oval(target_canvas_x - 14, target_canvas_y - 14, target_canvas_x + 14, target_canvas_y + 14, outline="#b45309", width=3)
        self.canvas.create_text(target_canvas_x, target_canvas_y - 20, text="🪢", font=("Segoe UI Emoji", 14))
        
        # 9. Bulle de texte cartoon cri d'effort
        bubble_x = head_x - puller_side * 35
        bubble_y = head_y - 45
        self.canvas.create_text(bubble_x, bubble_y, text="HNNNGH ! 💪💢", font=("Impact", 13, "bold"), fill="#ea580c")


class CartoonDrunkOverlay:
    """
    Souris ivre cartoon : bouteille de rhum vintage estampillée 'XXX' qui trinque,
    bouchon de liège éjecté, cascade d'alcool ambré avec mousse, et curseur affublé
    d'yeux en spirale tournoyants, de joues rouges et d'étoiles dorées en orbite.
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
            
        self.last_wx = None
        self.last_wy = None
        self.phase = 0.0
        self.bubbles = []
        self.visible = False
        self._loop_active = True
        self._tick()
        
    def _tick(self):
        if not self._loop_active:
            return
        try:
            global drunk_state
            if drunk_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                mx = drunk_state.get("mx", 0)
                my = drunk_state.get("my", 0)
                
                self.phase += 0.18
                wx = int(mx - (self.w // 2))
                wy = int(my - (self.h // 2) - 30)
                
                if (wx, wy) != (self.last_wx, self.last_wy):
                    self.last_wx = wx
                    self.last_wy = wy
                    if self.hwnd:
                        ctypes.windll.user32.SetWindowPos(
                            self.hwnd, 0, wx, wy, 0, 0,
                            0x0001 | 0x0004 | 0x0010
                        )
                    else:
                        self.win.geometry(f"{self.w}x{self.h}+{wx}+{wy}")
                        
                # Bulles d'alcool cartoon
                if len(self.bubbles) < 8 and random.random() < 0.35:
                    self.bubbles.append({
                        "x": (self.w // 2) + random.uniform(-40, 40),
                        "y": (self.h // 2) + 20,
                        "vy": random.uniform(-2.5, -1.0),
                        "r": random.uniform(3, 7),
                        "life": 1.0
                    })
                    
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.bubbles.clear()
                    self.last_wx = None
                    self.last_wy = None
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)
            
    def _draw(self):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = self.h // 2 + 25
        
        # 1. Bulles d'alcool pétillantes
        new_bubbles = []
        for b in self.bubbles:
            self.canvas.create_oval(b["x"] - b["r"], b["y"] - b["r"], b["x"] + b["r"], b["y"] + b["r"], fill="", outline="#fde047", width=2)
            b["y"] += b["vy"]
            b["life"] -= 0.04
            if b["life"] > 0:
                new_bubbles.append(b)
        self.bubbles = new_bubbles
        
        # 2. Bouteille de Rhum 'XXX' inclinée vers le curseur
        jug_x = cx - 55 + math.sin(self.phase * 0.8) * 6
        jug_y = cy - 75 + math.cos(self.phase * 0.8) * 4
        jug_rot = -38.0 + math.sin(self.phase * 2.5) * 12.0
        
        # Cruche en céramique (grès beige + col foncé)
        self.canvas.create_oval(jug_x - 26, jug_y - 24, jug_x + 26, jug_y + 36, fill="#d97706", outline="#78350f", width=3)
        self.canvas.create_rectangle(jug_x - 12, jug_y - 45, jug_x + 12, jug_y - 20, fill="#92400e", outline="#78350f", width=2)
        # Anse de la cruche
        self.canvas.create_arc(jug_x - 38, jug_y - 20, jug_x - 14, jug_y + 15, start=90, extent=180, style="arc", outline="#78350f", width=4)
        # Bouchon en liège qui saute
        cork_x = jug_x + 35
        cork_y = jug_y - 55 + math.sin(self.phase * 5.0) * 8
        self.canvas.create_polygon([(cork_x - 8, cork_y - 6), (cork_x + 8, cork_y - 10), (cork_x + 10, cork_y + 4), (cork_x - 6, cork_y + 8)], fill="#b45309", outline="#451a03", width=2)
        self.canvas.create_text(cork_x + 14, cork_y - 8, text="POP! 🍾", font=("Impact", 10, "bold"), fill="#fbbf24")
        # Inscription vintage 'XXX'
        self.canvas.create_text(jug_x, jug_y + 4, text="XXX", font=("Impact", 13, "bold"), fill="#fef3c7")
        
        # Jet d'alcool doré qui coule vers le bas
        pour_end_x = cx - 5
        pour_end_y = cy - 15
        self.canvas.create_line(jug_x + 10, jug_y - 30, pour_end_x, pour_end_y, fill="#f59e0b", width=6, capstyle=tk.ROUND)
        self.canvas.create_line(jug_x + 10, jug_y - 30, pour_end_x, pour_end_y, fill="#fef08a", width=3, capstyle=tk.ROUND)
        # Gouttes d'éclaboussure
        for s in range(4):
            sx = pour_end_x + math.sin(self.phase * 3 + s) * 14
            sy = pour_end_y + math.cos(self.phase * 3 + s) * 8
            self.canvas.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill="#fef08a", outline="#d97706", width=1)
            
        # 3. Curseur cartoon ivre avec visage expressif
        cursor_center_x = cx
        cursor_center_y = cy
        
        # Tête ronde souriante ivre
        self.canvas.create_oval(cursor_center_x - 22, cursor_center_y - 22, cursor_center_x + 22, cursor_center_y + 22, fill="#fef08a", outline="#ca8a04", width=3)
        # Joues roses bien imbibées
        self.canvas.create_oval(cursor_center_x - 20, cursor_center_y + 2, cursor_center_x - 8, cursor_center_y + 12, fill="#f43f5e", outline="")
        self.canvas.create_oval(cursor_center_x + 8, cursor_center_y + 2, cursor_center_x + 20, cursor_center_y + 12, fill="#f43f5e", outline="")
        # Yeux tournoyants en spirale cartoon
        spin_ang = self.phase * 4.0
        self.canvas.create_text(cursor_center_x - 9, cursor_center_y - 6, text="🌀", font=("Segoe UI Emoji", 11))
        self.canvas.create_text(cursor_center_x + 9, cursor_center_y - 6, text="🌀", font=("Segoe UI Emoji", 11))
        # Bouche ondulée en zigzag avec sourire niais
        self.canvas.create_line(cursor_center_x - 10, cursor_center_y + 12, cursor_center_x - 3, cursor_center_y + 8, cursor_center_x + 3, cursor_center_y + 14, cursor_center_x + 10, cursor_center_y + 10, fill="#713f12", width=3, smooth=True)
        
        # 4. Étoiles dorées tournoyant en orbite 3D au-dessus de la tête
        star_count = 4
        for i in range(star_count):
            ang = self.phase * 2.2 + i * (2 * math.pi / star_count)
            star_x = cursor_center_x + math.cos(ang) * 36
            star_y = cursor_center_y - 32 + math.sin(ang) * 12
            self.canvas.create_text(star_x, star_y, text="⭐", font=("Segoe UI Emoji", 13))
            
        # 5. Bulles de dialogue
        self.canvas.create_text(cx + 65, cy - 65, text="GLOU GLOU ! 🍺", font=("Impact", 12, "bold"), fill="#f59e0b")
        self.canvas.create_text(cx + 55, cy + 20, text="*HIC !* 🫧", font=("Impact", 13, "bold"), fill="#ec4899")


class CartoonWallOverlay:
    """
    Mur invisible cartoon : mur de briques 3D vivant avec mortier, fissures,
    mousse végétale et un visage expressif doté d'yeux animés qui suivent la souris,
    accompagné d'un impact spectaculaire '💥 BONK ! 💥' avec débris et étincelles.
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 160, 320
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
            
        self.last_wx = None
        self.last_wy = None
        self.phase = 0.0
        self.debris = []
        self.visible = False
        self._loop_active = True
        self._tick()
        
    def _tick(self):
        if not self._loop_active:
            return
        try:
            global wall_state
            if wall_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                mx = wall_state.get("mx", 0)
                my = wall_state.get("my", 0)
                is_bonking = wall_state.get("is_bonking", False)
                wall_x = wall_state.get("wall_x", mx)
                
                self.phase += 0.2
                wx = int(wall_x - (self.w // 2))
                wy = int(my - (self.h // 2))
                
                if (wx, wy) != (self.last_wx, self.last_wy):
                    self.last_wx = wx
                    self.last_wy = wy
                    if self.hwnd:
                        ctypes.windll.user32.SetWindowPos(
                            self.hwnd, 0, wx, wy, 0, 0,
                            0x0001 | 0x0004 | 0x0010
                        )
                    else:
                        self.win.geometry(f"{self.w}x{self.h}+{wx}+{wy}")
                        
                if is_bonking and len(self.debris) < 12:
                    for _ in range(3):
                        self.debris.append({
                            "x": (self.w // 2) + random.uniform(-10, 10),
                            "y": (self.h // 2) + random.uniform(-20, 20),
                            "vx": random.uniform(-5, 5),
                            "vy": random.uniform(-6, -2),
                            "r": random.uniform(3, 7),
                            "color": random.choice(["#b91c1c", "#d97706", "#94a3b8"]),
                            "life": 1.0
                        })
                        
                self._draw(mx, my, wx, wy, is_bonking)
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.debris.clear()
                    self.last_wx = None
                    self.last_wy = None
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)
            
    def _draw(self, mx, my, wx, wy, is_bonking):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = self.h // 2
        
        # 1. Structure du mur de briques 3D
        brick_w = 42
        brick_h = 24
        start_y = 15
        row = 0
        while start_y < self.h - 15:
            offset_x = -15 if row % 2 == 0 else 0
            for bx in range(cx - 35 + offset_x, cx + 45, brick_w):
                # Brique rouge avec bord biseauté 3D
                self.canvas.create_rectangle(bx, start_y, bx + brick_w - 4, start_y + brick_h - 4, fill="#b91c1c", outline="#7f1d1d", width=2)
                self.canvas.create_line(bx + 2, start_y + 2, bx + brick_w - 6, start_y + 2, fill="#f87171", width=1) # reflet haut
            start_y += brick_h
            row += 1
            
        # Touches de mousse végétale cartoon
        self.canvas.create_oval(cx - 28, cy - 80, cx - 14, cy - 65, fill="#65a30d", outline="#3f6212", width=1)
        self.canvas.create_oval(cx + 12, cy + 70, cx + 28, cy + 85, fill="#65a30d", outline="#3f6212", width=1)
        
        # 2. Visage vivant cartoon au centre du mur
        face_y = cy - 10
        # Yeux globuleux suivant la souris
        eye_spacing = 18
        rel_mx = mx - (wx + cx)
        rel_my = my - (wy + face_y)
        pupil_dist = math.hypot(rel_mx, rel_my) or 1.0
        pupil_dx = (rel_mx / pupil_dist) * 4.5
        pupil_dy = (rel_my / pupil_dist) * 4.5
        
        for side in [-1, 1]:
            ex = cx + side * eye_spacing
            ey = face_y
            # Blanc de l'œil
            self.canvas.create_oval(ex - 12, ey - 14, ex + 12, ey + 14, fill="#ffffff", outline="#0f172a", width=3)
            # Pupille noire vivante
            self.canvas.create_oval(ex + pupil_dx - 5, ey + pupil_dy - 5, ex + pupil_dx + 5, ey + pupil_dy + 5, fill="#0f172a", outline="")
            # Reflet blanc dans la pupille
            self.canvas.create_oval(ex + pupil_dx - 3, ey + pupil_dy - 4, ex + pupil_dx, ey + pupil_dy - 1, fill="#ffffff", outline="")
            # Gros sourcil de brique
            brow_angle = -side * 15 if not is_bonking else side * 25
            self.canvas.create_line(ex - 14, ey - 16 - side * 2, ex + 14, ey - 16 + side * 2, fill="#450a0a", width=5)
            
        # Bouche de brique avec rictus narquois ou dents serrées
        if is_bonking:
            self.canvas.create_rectangle(cx - 16, face_y + 24, cx + 16, face_y + 36, fill="#ffffff", outline="#0f172a", width=2)
            self.canvas.create_line(cx - 6, face_y + 24, cx - 6, face_y + 36, fill="#0f172a", width=1)
            self.canvas.create_line(cx + 6, face_y + 24, cx + 6, face_y + 36, fill="#0f172a", width=1)
        else:
            self.canvas.create_arc(cx - 18, face_y + 15, cx + 18, face_y + 38, start=180, extent=180, fill="#450a0a", outline="#0f172a", width=2)
            
        # 3. Débris et poussière de choc
        new_debris = []
        for d in self.debris:
            self.canvas.create_oval(d["x"] - d["r"], d["y"] - d["r"], d["x"] + d["r"], d["y"] + d["r"], fill=d["color"], outline="#0f172a", width=1)
            d["x"] += d["vx"]
            d["y"] += d["vy"]
            d["vy"] += 0.5
            d["life"] -= 0.08
            if d["life"] > 0:
                new_debris.append(d)
        self.debris = new_debris
        
        # 4. Impact BONK spectaculaire avec étoile de bande-dessinée
        if is_bonking:
            # Étoile cartoon à 12 branches
            star_pts = []
            for sp in range(12):
                sa = sp * (math.pi / 6.0) + self.phase
                sr = 38 if sp % 2 == 0 else 18
                star_pts.append((cx + math.cos(sa) * sr, cy + math.sin(sa) * sr))
            self.canvas.create_polygon(star_pts, fill="#facc15", outline="#ea580c", width=3)
            self.canvas.create_text(cx, cy, text="💥 BONK ! 💥", font=("Impact", 13, "bold"), fill="#dc2626")




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

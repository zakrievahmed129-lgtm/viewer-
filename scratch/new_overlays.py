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


print("Classes 1-3 compiled successfully!")

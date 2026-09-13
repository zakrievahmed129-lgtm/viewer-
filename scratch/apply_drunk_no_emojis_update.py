import sys

# Script d'application de la refonte de la souris ivre
with open("ghost_script.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Mise à jour de drunk_state
old_drunk_state = 'drunk_state = {"active": False, "mx": 0, "my": 0, "intro_reset": False}'
new_drunk_state = 'drunk_state = {"active": False, "mx": 0, "my": 0, "drinking": False, "intro_reset": False}'

if old_drunk_state in content:
    content = content.replace(old_drunk_state, new_drunk_state, 1)
    print("1. drunk_state mis à jour avec drinking: False")
else:
    print("WARNING: old_drunk_state non trouvé")

# 2. Nouvelle classe CartoonDrunkOverlay
new_overlay_code = '''class CartoonDrunkOverlay:
    """
    Souris ivre cartoon :
    1. Phase Boisson (~2s) : la souris boit dans une bouteille d'alcool réaliste.
    2. Phase Ivre : la souris arrête complètement de boire (zéro bouteille),
       sa tête tourne d'ivresse (yeux en spirales vectorielles animées, vacillement)
       avec des étoiles cartoon dorées qui orbitent en 3D autour de sa tête.
       (Aucun emoji, aucun texte, pur rendu vectoriel cartoon).
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
                is_drinking = drunk_state.get("drinking", False)
                
                self.phase += 0.22
                wx = int(mx - (self.w // 2))
                wy = int(my - 125)
                
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
                        
                # Bulles d'alcool pétillantes (uniquement quand elle boit)
                if is_drinking and random.random() < 0.35:
                    self.bubbles.append({
                        "x": (self.w // 2) - 15 + random.uniform(-6, 6),
                        "y": 125 - 10 + random.uniform(-4, 4),
                        "vx": random.uniform(-1.5, 1.5),
                        "vy": random.uniform(-2.2, -0.6),
                        "r": random.uniform(2.5, 5.5),
                        "life": 1.0
                    })
                    
                self._draw(is_drinking)
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

    def _draw_star(self, cx, cy, radius, spin):
        """Dessine une véritable étoile cartoon 5 branches dorée sans aucun emoji."""
        pts = []
        r_in = radius * 0.42
        for i in range(10):
            r = radius if i % 2 == 0 else r_in
            ang = spin + i * (math.pi / 5.0) - (math.pi / 2.0)
            pts.append(cx + math.cos(ang) * r)
            pts.append(cy + math.sin(ang) * r)
        self.canvas.create_polygon(pts, fill="#fbbf24", outline="#b45309", width=1.5)
        # Éclat spéculaire blanc au centre
        cr = max(1.5, radius * 0.22)
        self.canvas.create_oval(cx - cr, cy - cr, cx + cr, cy + cr, fill="#ffffff", outline="")

    def _draw(self, is_drinking=False):
        self.canvas.delete("all")
        mx = self.w // 2
        my = 125
        
        # Angle d'inclinaison et vacillement comique
        if is_drinking:
            sway_angle = math.sin(self.phase * 2.5) * 8.0 - 10.0
        else:
            # Vacillement prononcé quand elle est ivre (sa tête qui tourne)
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
            # Yeux fermés satisfaits en dégustant (arcs simples)
            for ox in [3, 9]:
                ex = mx + (ox * cos_r - 10 * sin_r)
                ey = my + (ox * sin_r + 10 * cos_r)
                self.canvas.create_arc(ex - 3, ey - 3, ex + 3, ey + 3, start=0, extent=180, style="arc", outline="#000000", width=2)
        else:
            # YEUX EN SPIRALE HYPNOTIQUE VECTORIELLE ANIMÉE (SA TÊTE QUI TOURNE !)
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
        # Quand elle est ivre, la souris a arrêté de boire (zéro bouteille).
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
            
            # Reflets blancs lustrés
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
                    self._draw_star(sx, sy, 8.0 * scale, spin)'''

# Recherche de l'ancienne classe CartoonDrunkOverlay
start_marker = "class CartoonDrunkOverlay:"
end_marker = "class CartoonWallOverlay:"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker)

if idx_start != -1 and idx_end != -1:
    content = content[:idx_start] + new_overlay_code + "\n\n" + content[idx_end:]
    print("2. CartoonDrunkOverlay remplacé avec succès (sans emojis, sans texte, étoiles vectorielles, fin de boisson)")
else:
    print(f"ERREUR: markers non trouvés idx_start={idx_start}, idx_end={idx_end}")

# 3. Mise à jour de _drunk_mouse_loop et toggle_drunk_mouse
old_loop_code = '''def _drunk_mouse_loop():
    """
    Souris ivre avec animation cartoon :
    1. Boit de l'alcool dans une bouteille super réaliste (goulot, liquide ambré, étiquette, reflets).
    2. Commence à vaciller avec joues rouges d'ébriété, perte d'équilibre et étoiles/spirales 3D en orbite autour de sa tête (*HIC !*).
    """
    global drunk_mouse_active, drunk_state
    t = 0.0
    start_time = time.time()
    ensure_prank_overlays_started()
    drunk_state["intro_reset"] = True
    
    while drunk_mouse_active:
        try:
            x, y = _get_current_mouse_position()
            elapsed = time.time() - start_time
            if elapsed < 2.0:
                # Phase 1 : dégustation goulue à la bouteille, tremblements de gorgées
                sip_x = int(math.sin(t * 8.0) * 2.0)
                sip_y = int(math.cos(t * 8.0) * 2.0)
                target_x = x + sip_x
                target_y = y + sip_y
            else:
                # Phase 2 : vacillement comique prononcé et titubements
                stagger_x = int(math.sin(t * 1.5) * 16.0 + math.cos(t * 0.7) * 8.0)
                stagger_y = int(math.cos(t * 1.3) * 12.0 + math.sin(t * 0.8) * 6.0)
                if random.random() < 0.05:
                    stagger_x += random.choice([-18, 18])
                    stagger_y += random.choice([-10, 10])
                target_x = x + stagger_x
                target_y = y + stagger_y
                
            sw = ctypes.windll.user32.GetSystemMetrics(0)
            sh = ctypes.windll.user32.GetSystemMetrics(1)
            target_x = max(10, min(sw - 10, target_x))
            target_y = max(10, min(sh - 10, target_y))
            
            ctypes.windll.user32.SetCursorPos(target_x, target_y)
            drunk_state["active"] = True
            drunk_state["mx"] = target_x
            drunk_state["my"] = target_y
                
            t += 0.22
        except Exception:
            pass
        time.sleep(0.035)
        
    drunk_state["active"] = False'''

new_loop_code = '''def _drunk_mouse_loop():
    """
    Souris ivre avec animation cartoon :
    1. Boit de l'alcool dans une bouteille réaliste au démarrage (~2.2s).
    2. Dès qu'elle est ivre, elle ARRÊTE de boire : plus de bouteille, sa tête tourne avec des étoiles en orbite.
    """
    global drunk_mouse_active, drunk_state
    t = 0.0
    start_time = time.time()
    ensure_prank_overlays_started()
    drunk_state["intro_reset"] = True
    
    while drunk_mouse_active:
        try:
            x, y = _get_current_mouse_position()
            elapsed = time.time() - start_time
            is_drinking = (elapsed < 2.2)
            drunk_state["drinking"] = is_drinking
            
            if is_drinking:
                # Phase 1 : dégustation à la bouteille, tremblements de gorgées
                sip_x = int(math.sin(t * 8.0) * 2.0)
                sip_y = int(math.cos(t * 8.0) * 2.0)
                target_x = x + sip_x
                target_y = y + sip_y
            else:
                # Phase 2 : elle est ivre, a arrêté de boire ! Vacillements et tête qui tourne
                stagger_x = int(math.sin(t * 1.5) * 16.0 + math.cos(t * 0.7) * 8.0)
                stagger_y = int(math.cos(t * 1.3) * 12.0 + math.sin(t * 0.8) * 6.0)
                if random.random() < 0.05:
                    stagger_x += random.choice([-18, 18])
                    stagger_y += random.choice([-10, 10])
                target_x = x + stagger_x
                target_y = y + stagger_y
                
            sw = ctypes.windll.user32.GetSystemMetrics(0)
            sh = ctypes.windll.user32.GetSystemMetrics(1)
            target_x = max(10, min(sw - 10, target_x))
            target_y = max(10, min(sh - 10, target_y))
            
            ctypes.windll.user32.SetCursorPos(target_x, target_y)
            drunk_state["active"] = True
            drunk_state["mx"] = target_x
            drunk_state["my"] = target_y
                
            t += 0.22
        except Exception:
            pass
        time.sleep(0.035)
        
    drunk_state["active"] = False
    drunk_state["drinking"] = False'''

if old_loop_code in content:
    content = content.replace(old_loop_code, new_loop_code, 1)
    print("3. _drunk_mouse_loop mis à jour avec transition boire -> ivre")
else:
    print("WARNING: old_loop_code non trouvé!")

# Mise à jour toggle_drunk_mouse pour reset drinking
old_toggle = '''    elif not active:
        drunk_mouse_active = False
        drunk_state["active"] = False'''

new_toggle = '''    elif not active:
        drunk_mouse_active = False
        drunk_state["active"] = False
        drunk_state["drinking"] = False'''

if old_toggle in content:
    content = content.replace(old_toggle, new_toggle, 1)
    print("4. toggle_drunk_mouse mis à jour avec reset drinking: False")

# Sauvegarde
with open("ghost_script.py", "w", encoding="utf-8") as f:
    f.write(content)
print("ghost_script.py sauvegardé avec succès!")

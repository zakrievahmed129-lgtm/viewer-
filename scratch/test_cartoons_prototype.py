# -*- coding: utf-8 -*-
"""
Prototype et testeur visuel pour les 4 composants refaits :
1. CartoonPainterOverlay (Lancer de pinceaux réaliste, impact vitre, vibration amortie, coulures de peinture)
2. CartoonKeysOverlay (Touches mécaniques 3D hyper-réalistes, substitution par maillet de gremlin)
3. CartoonGhostOverlay (Fantôme super chiant bloquant le curseur, bave, jumpscare, secousses)
4. CartoonMessageDelivery (Fenêtre de message cartoon chaleureuse avec grand personnage coursier en élastique)
"""

import sys
import os
import math
import time
import random
import ctypes
from ctypes import wintypes
import tkinter as tk

# ==============================================================================
# 1. CARTOON PAINTER OVERLAY (LANCER DE PINCEAUX RÉALISTE)
# ==============================================================================

class CartoonPainterOverlay:
    """
    Peintre cartoon français :
    Lance des pinceaux un par un avec une trajectoire 3D balistique réaliste vers l'écran.
    À l'impact sur la vitre :
    - Énorme tache de peinture 3D lustrée et éclaboussures radiales.
    - Le pinceau reste fiché dans la vitre et vibre avec une oscillation harmonique amortie.
    - Coulures épaisses qui descendent le long de l'écran avec la gravité.
    Plusieurs pinceaux peuvent rester plantés simultanément !
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
        self.px = float(self.sw - 165)
        self.py = float(self.sh - 135)
        
        # État du lancer du peintre
        self.throw_state = "IDLE"  # IDLE, AIM, WINDUP, THROW, CELEBRATE
        self.throw_timer = 0
        self.current_brush_color = "#ef4444"
        
        # Pinceaux en vol, pinceaux plantés, coulures et particules
        self.flying_brushes = []
        self.stuck_brushes = []
        self.air_droplets = []
        self.comic_splats = []
        
        self.colors = [
            "#ef4444", "#3b82f6", "#f59e0b", "#10b981",
            "#8b5cf6", "#ec4899", "#06b6d4", "#f97316"
        ]
        self._tick()

    def throw_new_brush(self):
        """Déclenche le lancer d'un nouveau pinceau vers une cible aléatoire sur l'écran."""
        self.current_brush_color = random.choice(self.colors)
        tx = random.randint(140, self.sw - 200)
        ty = random.randint(100, self.sh - 180)
        
        self.flying_brushes.append({
            "sx": self.px - 30,
            "sy": self.py - 45,
            "tx": tx,
            "ty": ty,
            "color": self.current_brush_color,
            "t": 0.0,
            "speed": random.uniform(0.045, 0.065),  # Rapide et dynamique (~16-22 frames)
            "spin": random.uniform(-15.0, 15.0),
            "rot": random.uniform(0, 360),
            "arc_height": random.uniform(-140, -80)
        })

    def _tick(self):
        if not self._loop_active:
            return
        try:
            # Vérification globale de l'état actif
            is_active = True
            if "painter_state" in globals():
                is_active = globals()["painter_state"].get("active", False)
                
            if is_active:
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                self.phase += 0.15
                self.throw_timer += 1
                
                # Respiration et petits pas du peintre
                self.px = (self.sw - 165) + math.sin(self.phase * 0.5) * 15
                self.py = (self.sh - 135) + math.cos(self.phase * 0.8) * 8
                
                # Machine à état du lancer du peintre
                if self.throw_state == "IDLE":
                    if self.throw_timer > 35:
                        self.throw_state = "AIM"
                        self.throw_timer = 0
                elif self.throw_state == "AIM":
                    if self.throw_timer > 15:
                        self.throw_state = "WINDUP"
                        self.throw_timer = 0
                elif self.throw_state == "WINDUP":
                    if self.throw_timer > 12:
                        self.throw_state = "THROW"
                        self.throw_timer = 0
                        self.throw_new_brush()
                elif self.throw_state == "THROW":
                    if self.throw_timer > 8:
                        self.throw_state = "CELEBRATE"
                        self.throw_timer = 0
                elif self.throw_state == "CELEBRATE":
                    if self.throw_timer > 30:
                        self.throw_state = "IDLE"
                        self.throw_timer = 0
                        
                # 1. Mise à jour des pinceaux en vol
                new_flying = []
                for b in self.flying_brushes:
                    b["t"] += b["speed"]
                    b["rot"] += b["spin"]
                    
                    # Spawn de gouttelettes traînantes
                    if random.random() < 0.65:
                        # Position actuelle du pinceau
                        t = b["t"]
                        cur_x = b["sx"] + (b["tx"] - b["sx"]) * t
                        cur_y = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc_height"] * t * (1 - t))
                        self.air_droplets.append({
                            "x": cur_x + random.uniform(-6, 6),
                            "y": cur_y + random.uniform(-6, 6),
                            "color": b["color"],
                            "r": random.uniform(2.5, 4.5),
                            "life": 1.0,
                            "vy": random.uniform(0.5, 2.0)
                        })
                        
                    if b["t"] >= 1.0:
                        # IMPACT SUR L'ÉCRAN !
                        tx = b["tx"]
                        ty = b["ty"]
                        color = b["color"]
                        
                        # Création du pinceau planté avec vibration amortie
                        self.stuck_brushes.append({
                            "x": tx,
                            "y": ty,
                            "color": color,
                            "base_angle": random.uniform(-35, 35),
                            "vib_t": 0.0,
                            "vib_amp": random.uniform(22.0, 32.0),
                            "life": random.uniform(14.0, 22.0),
                            "splat_r": random.uniform(28, 46),
                            "drips": [
                                {
                                    "ox": random.uniform(-10, 10),
                                    "oy": random.uniform(10, 20),
                                    "len": 0.0,
                                    "max_len": random.uniform(60, 220),
                                    "speed": random.uniform(1.2, 3.2),
                                    "width": random.uniform(3.5, 6.0)
                                } for _ in range(random.randint(1, 3))
                            ]
                        })
                        
                        # Étoile et texte comique d'impact
                        self.comic_splats.append({
                            "x": tx,
                            "y": ty - 25,
                            "text": random.choice(["💥 SPLAT !", "🎨 TCHAAK !", "✨ BIM !", "🖌️ PLOUF !"]),
                            "color": color,
                            "life": 1.0
                        })
                        
                        # Limiter à 8 pinceaux plantés max
                        if len(self.stuck_brushes) > 8:
                            self.stuck_brushes.pop(0)
                    else:
                        new_flying.append(b)
                self.flying_brushes = new_flying
                
                # 2. Mise à jour des gouttelettes en l'air
                new_drops = []
                for d in self.air_droplets:
                    d["y"] += d["vy"]
                    d["life"] -= 0.05
                    if d["life"] > 0:
                        new_drops.append(d)
                self.air_droplets = new_drops
                
                # 3. Mise à jour des pinceaux plantés et coulures
                new_stuck = []
                for sb in self.stuck_brushes:
                    sb["life"] -= 0.04
                    sb["vib_t"] += 0.16
                    for dr in sb["drips"]:
                        if dr["len"] < dr["max_len"]:
                            dr["len"] += dr["speed"]
                    if sb["life"] > 0:
                        new_stuck.append(sb)
                self.stuck_brushes = new_stuck
                
                # 4. Mise à jour des textes comiques
                new_splats = []
                for cs in self.comic_splats:
                    cs["life"] -= 0.045
                    cs["y"] -= 0.6
                    if cs["life"] > 0:
                        new_splats.append(cs)
                self.comic_splats = new_splats
                
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.flying_brushes.clear()
                    self.stuck_brushes.clear()
                    self.air_droplets.clear()
                    self.comic_splats.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(22, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        
        # 1. Gouttelettes d'air traînantes
        for d in self.air_droplets:
            r = d["r"] * d["life"]
            self.canvas.create_oval(d["x"] - r, d["y"] - r, d["x"] + r, d["y"] + r, fill=d["color"], outline="")
            
        # 2. Coulures et taches des pinceaux plantés (au fond de la vitre)
        for sb in self.stuck_brushes:
            sx, sy, scolor = sb["x"], sb["y"], sb["color"]
            sr = sb["splat_r"]
            
            # A. Coulures sous gravité
            for dr in sb["drips"]:
                dx = sx + dr["ox"]
                dy = sy + dr["oy"]
                dlen = dr["len"]
                dw = dr["width"]
                if dlen > 2:
                    self.canvas.create_line(dx, dy, dx, dy + dlen, fill=scolor, width=int(dw), capstyle=tk.ROUND)
                    # Gouttelette terminale renflée en forme de poire
                    gy = dy + dlen
                    self.canvas.create_oval(dx - dw*0.9, gy - dw*0.9, dx + dw*0.9, gy + dw*1.2, fill=scolor, outline="")
                    # Éclat lustré blanc sur la goutte
                    self.canvas.create_oval(dx - dw*0.3, gy - dw*0.3, dx + dw*0.2, gy + dw*0.4, fill="#ffffff", outline="")
            
            # B. Grosse tache de peinture bombée 3D
            # Ombre sombre externe
            self.canvas.create_oval(sx - sr - 3, sy - sr - 3, sx + sr + 3, sy + sr + 3, fill="#0f172a", outline="")
            
            # Lobes organiques de la tache
            pts = []
            for deg in range(0, 360, 24):
                rad = math.radians(deg)
                lobe = 1.0 + 0.38 * math.sin(deg * 3.5) + 0.15 * math.cos(deg * 2.0)
                rr = sr * lobe
                pts.append((sx + math.cos(rad) * rr, sy + math.sin(rad) * rr))
            self.canvas.create_polygon(pts, fill=scolor, outline="", smooth=True)
            
            # Reflet laqué blanc brillant 3D (dôme de lumière)
            self.canvas.create_arc(
                sx - sr * 0.65, sy - sr * 0.65, sx + sr * 0.25, sy + sr * 0.25,
                start=40, extent=95, style="arc", outline="#ffffff", width=4
            )
            
            # Éclaboussures satellites radiales
            for ed in [25, 75, 140, 210, 275, 330]:
                erad = math.radians(ed)
                dist = sr * 1.55
                ex = sx + math.cos(erad) * dist
                ey = sy + math.sin(erad) * dist
                self.canvas.create_oval(ex - 4, ey - 4, ex + 4, ey + 4, fill=scolor, outline="")
                
        # 3. Manche et virole des pinceaux plantés (avec vibration amortie !)
        for sb in self.stuck_brushes:
            sx, sy, scolor = sb["x"], sb["y"], sb["color"]
            
            # Calcul de l'oscillation amortie du manche planté
            vt = sb["vib_t"]
            damping = math.exp(-vt * 3.8)
            vib_angle = sb["vib_amp"] * damping * math.sin(vt * 28.0)
            total_angle = sb["base_angle"] + vib_angle
            rad = math.radians(total_angle - 90)  # Pointeur vers le haut / oblique
            
            # Longueur du manche en perspective
            handle_len = 85.0
            hx2 = sx + math.cos(rad) * handle_len
            hy2 = sy + math.sin(rad) * handle_len
            
            # Virole métallique (fixation des poils)
            vx1 = sx + math.cos(rad) * 12
            vy1 = sy + math.sin(rad) * 12
            self.canvas.create_line(sx, sy, vx1, vy1, fill=scolor, width=9, capstyle=tk.ROUND)
            
            vx2 = sx + math.cos(rad) * 26
            vy2 = sy + math.sin(rad) * 26
            # Métal chromé avec reflet
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#94a3b8", width=8)
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#f8fafc", width=3)
            
            # Manche en bois verni sculpté (dégradé bois caramel / acajou)
            self.canvas.create_line(vx2, vy2, hx2, hy2, fill="#b45309", width=6, capstyle=tk.ROUND)
            self.canvas.create_line(vx2 + math.cos(rad)*5, vy2 + math.sin(rad)*5, hx2 - math.cos(rad)*10, hy2 - math.sin(rad)*10, fill="#d97706", width=3)
            # Bout arrondi du manche
            self.canvas.create_oval(hx2 - 4, hy2 - 4, hx2 + 4, hy2 + 4, fill="#78350f", outline="")
            
        # 4. Pinceaux en plein vol (Perspective 3D & rotation balistique)
        for b in self.flying_brushes:
            t = b["t"]
            # Position parabolique
            bx = b["sx"] + (b["tx"] - b["sx"]) * t
            by = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc_height"] * t * (1 - t))
            
            # Échelle 3D : grandit au fur et à mesure qu'il s'approche de la caméra
            scale = 0.45 + 0.90 * t
            rot_rad = math.radians(b["rot"])
            b_len = 70.0 * scale
            
            # Points du manche
            x_tip = bx - math.cos(rot_rad) * (b_len * 0.4)
            y_tip = by - math.sin(rot_rad) * (b_len * 0.4)
            x_end = bx + math.cos(rot_rad) * (b_len * 0.6)
            y_end = by + math.sin(rot_rad) * (b_len * 0.6)
            
            # Manche en bois
            self.canvas.create_line(bx, by, x_end, y_end, fill="#92400e", width=max(3, int(6 * scale)), capstyle=tk.ROUND)
            # Virole argentée
            v_mid_x = bx - math.cos(rot_rad) * (b_len * 0.15)
            v_mid_y = by - math.sin(rot_rad) * (b_len * 0.15)
            self.canvas.create_line(bx, by, v_mid_x, v_mid_y, fill="#e2e8f0", width=max(4, int(7 * scale)))
            # Poils trempés de peinture vive
            self.canvas.create_line(v_mid_x, v_mid_y, x_tip, y_tip, fill=b["color"], width=max(5, int(9 * scale)), capstyle=tk.ROUND)
            
            # Ligne de vitesse / vent cartoon derrière le pinceau
            tail_x = bx + math.cos(rot_rad) * (b_len * 0.9)
            tail_y = by + math.sin(rot_rad) * (b_len * 0.9)
            self.canvas.create_line(x_end, y_end, tail_x, tail_y, fill="#f8fafc", width=2, dash=(4, 4))
            
        # 5. Textes et étoiles d'impact comiques
        for cs in self.comic_splats:
            cx, cy = cs["x"], cs["y"]
            # Étoile cartoon jaune
            star_pts = []
            for sa_deg in range(0, 360, 36):
                sa = math.radians(sa_deg)
                sr = 22 if (sa_deg // 36) % 2 == 0 else 10
                star_pts.append((cx + math.cos(sa) * sr, cy + math.sin(sa) * sr))
            self.canvas.create_polygon(star_pts, fill="#facc15", outline="#ea580c", width=2)
            self.canvas.create_text(cx, cy, text=cs["text"], font=("Impact", 13, "bold"), fill="#dc2626")
            
        # 6. Personnage du Peintre Cartoon en bas à droite
        self._draw_painter()

    def _draw_painter(self):
        px = self.px
        py = self.py
        
        # A. Ombre au sol
        self.canvas.create_oval(px - 38, py + 34, px + 38, py + 46, fill="#0f172a", outline="")
        
        # B. Pieds cartoon (chaussures cirées noires)
        self.canvas.create_oval(px - 28, py + 30, px - 6, py + 42, fill="#0f172a", outline="")
        self.canvas.create_oval(px + 6, py + 30, px + 28, py + 42, fill="#0f172a", outline="")
        
        # C. Pantalon noir
        self.canvas.create_rectangle(px - 22, py + 18, px + 22, py + 33, fill="#1e293b", outline="#0f172a", width=2)
        
        # D. Corps : Marinière à rayures bleues et blanches
        # Buste penché selon l'état de lancer
        lean = 0.0
        if self.throw_state == "WINDUP":
            lean = 12.0  # Arqué en arrière
        elif self.throw_state in ("THROW", "AIM"):
            lean = -10.0  # Projeté en avant
            
        body_x = px + lean * 0.5
        self.canvas.create_oval(body_x - 30, py - 26, body_x + 30, py + 24, fill="#ffffff", outline="#0f172a", width=3)
        for ry in range(-16, 20, 9):
            self.canvas.create_line(body_x - 26, py + ry, body_x + 26, py + ry, fill="#1d4ed8", width=4)
            
        # E. Foulard rouge d'artiste autour du cou
        self.canvas.create_polygon([
            (body_x - 14, py - 24), (body_x, py - 18), (body_x + 14, py - 24),
            (body_x + 6, py - 12), (body_x - 6, py - 12)
        ], fill="#dc2626", outline="#7f1d1d", width=1)
        
        # F. Palette de bois dans la main gauche
        pal_x = body_x - 42
        pal_y = py + 4
        self.canvas.create_oval(pal_x - 26, pal_y - 18, pal_x + 26, pal_y + 18, fill="#d97706", outline="#78350f", width=3)
        # Trou du pouce
        self.canvas.create_oval(pal_x - 16, pal_y - 6, pal_x - 8, pal_y + 6, fill="#fed7aa", outline="#78350f", width=2)
        # Taches de peinture sur la palette
        pal_dots = ["#ef4444", "#3b82f6", "#facc15", "#10b981", "#a855f7"]
        for pi, pc in enumerate(pal_dots):
            pdeg = math.radians(pi * 48 - 25)
            self.canvas.create_oval(pal_x + math.cos(pdeg)*15 - 4, pal_y + math.sin(pdeg)*10 - 4,
                                    pal_x + math.cos(pdeg)*15 + 4, pal_y + math.sin(pdeg)*10 + 4,
                                    fill=pc, outline="")
                                    
        # G. Bras droit & Pinceau tenu (selon l'animation de lancer)
        arm_start_x = body_x + 22
        arm_start_y = py - 12
        if self.throw_state == "IDLE":
            hand_x = body_x + 36
            hand_y = py - 4
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            # Pinceau tenu verticalement
            self.canvas.create_line(hand_x, hand_y - 28, hand_x, hand_y + 18, fill="#92400e", width=4)
            self.canvas.create_line(hand_x, hand_y - 28, hand_x, hand_y - 38, fill=self.current_brush_color, width=6, capstyle=tk.ROUND)
        elif self.throw_state == "AIM":
            # Bras tendu pointant l'écran
            hand_x = body_x - 15
            hand_y = py - 35
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y, hand_x - 30, hand_y - 12, fill="#92400e", width=4)
            self.canvas.create_line(hand_x - 30, hand_y - 12, hand_x - 42, hand_y - 18, fill=self.current_brush_color, width=6, capstyle=tk.ROUND)
        elif self.throw_state == "WINDUP":
            # Bras armé très loin en arrière
            hand_x = body_x + 48
            hand_y = py - 40
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y, hand_x + 28, hand_y - 20, fill="#92400e", width=4)
            self.canvas.create_line(hand_x + 28, hand_y - 20, hand_x + 40, hand_y - 28, fill=self.current_brush_color, width=6, capstyle=tk.ROUND)
        elif self.throw_state == "THROW":
            # Coup de fouet vers l'avant avec lignes de vitesse
            hand_x = body_x - 32
            hand_y = py - 42
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x - 10, hand_y, hand_x - 35, hand_y - 10, fill="#f8fafc", width=3, dash=(3, 3))
        elif self.throw_state == "CELEBRATE":
            # Bras en l'air victorieux
            hand_x = body_x + 25
            hand_y = py - 48
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_text(body_x - 10, py - 85, text="MAGNIFIQUE ! 🎨✨", font=("Impact", 13, "bold"), fill="#f59e0b")
            
        # H. Tête ronde et expressive
        head_x = body_x
        head_y = py - 44
        self.canvas.create_oval(head_x - 24, head_y - 24, head_x + 24, head_y + 24, fill="#fed7aa", outline="#c2410c", width=2)
        
        # Béret rouge incliné avec téton
        self.canvas.create_oval(head_x - 32, head_y - 34, head_x + 24, head_y - 14, fill="#dc2626", outline="#7f1d1d", width=3)
        self.canvas.create_line(head_x - 5, head_y - 34, head_x - 5, head_y - 40, fill="#7f1d1d", width=3)
        
        # Yeux expressifs (clin d'œil d'artiste)
        if self.throw_state in ("AIM", "WINDUP"):
            # Oeil droit fermé (visée), oeil gauche grand ouvert concentré
            self.canvas.create_line(head_x + 4, head_y - 6, head_x + 14, head_y - 6, fill="#0f172a", width=3)
            self.canvas.create_oval(head_x - 16, head_y - 12, head_x - 4, head_y + 2, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 13, head_y - 10, head_x - 8, head_y - 5, fill="#ffffff", outline="")
        else:
            # Yeux joyeux grands ouverts
            self.canvas.create_oval(head_x - 15, head_y - 10, head_x - 4, head_y + 2, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x + 4, head_y - 10, head_x + 15, head_y + 2, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 12, head_y - 8, head_x - 8, head_y - 4, fill="#ffffff", outline="")
            self.canvas.create_oval(head_x + 7, head_y - 8, head_x + 11, head_y - 4, fill="#ffffff", outline="")
            
        # Grande moustache française noire en guidon ciré
        m_pts = [
            (head_x - 26, head_y + 6), (head_x - 10, head_y + 12),
            (head_x, head_y + 10), (head_x + 10, head_y + 12), (head_x + 26, head_y + 6)
        ]
        self.canvas.create_line(m_pts, fill="#0f172a", width=4, smooth=True)
        
        # Gros nez rose rond
        self.canvas.create_oval(head_x - 6, head_y - 2, head_x + 6, head_y + 8, fill="#fca5a5", outline="#c2410c", width=1)


# ==============================================================================
# 2. CARTOON KEYS OVERLAY (CLAVIER FOU AVEC TOUCHES 3D & MAILLET DE GREMLIN)
# ==============================================================================

class CartoonKeysOverlay:
    """
    Clavier fou cartoon hyper-réaliste :
    Affiche côte à côte deux touches de clavier mécanique 3D (profil PBT concave, switches MX,
    ressorts métalliques hélicoïdaux et illumination).
    Quand l'utilisateur tape une touche (ex: 'K') :
    - La touche 'K' commence à s'enfoncer.
    - Un gremlin farceur surgit et ÉCRASE violemment une autre touche (ex: 'E') avec un maillet géant !
    - La touche 'E' s'écrase jusqu'au fond avec ondes de choc, étincelles ⚡ et "CLACK !".
    - La touche 'K' de l'utilisateur est violemment repoussée en l'air sur son ressort avec un "❓ NON !".
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 480, 320
        self.sw = self.win.winfo_screenwidth()
        self.sh = self.win.winfo_screenheight()
        self.win.geometry(f"{self.w}x{self.h}+{self.sw - self.w - 40}+{self.sh - self.h - 100}")
        
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
        
        # Données d'état de l'échange de touches
        self.user_char = "K"
        self.prank_char = "E"
        self.anim_t = 0.0
        self.is_animating = False
        
        # Positions physiques des touches
        self.user_key_depth = 0.0      # Enfoncement (0 = repos, 18 = écrasé)
        self.prank_key_depth = 0.0
        self.user_key_recoil = 0.0     # Rebond éjecté en l'air
        
        # Effets : étincelles, ondes de choc
        self.sparks = []
        self.shockwaves = []
        self.bubble_text = ""
        self.bubble_timer = 0
        
        self._tick()

    def trigger_key_swap(self, chosen_char, replaced_char):
        """Déclenché depuis le hook clavier quand l'utilisateur tape chosen_char et que replaced_char est produit."""
        self.user_char = str(chosen_char).upper()
        self.prank_char = str(replaced_char).upper()
        self.anim_t = 0.0
        self.is_animating = True
        self.bubble_text = f"NON ! C'EST '{self.prank_char}' ! 😂"
        self.bubble_timer = 45

    def _tick(self):
        if not self._loop_active:
            return
        try:
            is_active = True
            if "keys_state" in globals():
                is_active = globals()["keys_state"].get("active", False)
                
            if is_active:
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                self.phase += 0.18
                
                # Simulation automatique si idle pour tester
                if not self.is_animating and random.random() < 0.025:
                    u = random.choice(["A", "Z", "Q", "S", "D", "T", "P"])
                    r = random.choice(["O", "E", "I", "U"])
                    self.trigger_key_swap(u, r)
                    
                # Gestion de l'animation séquentielle du swap
                if self.is_animating:
                    self.anim_t += 0.045
                    t = self.anim_t
                    
                    if t < 0.20:
                        # Phase 1 : La touche utilisateur commence à s'enfoncer (l'utilisateur appuie)
                        prog = t / 0.20
                        self.user_key_depth = 8.0 * prog
                        self.prank_key_depth = 0.0
                        self.user_key_recoil = 0.0
                    elif t < 0.35:
                        # Phase 2 : Le gremlin arme et ÉCRASE la touche farceur avec le maillet !
                        prog = (t - 0.20) / 0.15
                        self.prank_key_depth = 22.0 * prog
                        # Onde de choc et étincelles au moment du choc (t ~ 0.30)
                        if len(self.shockwaves) == 0:
                            self.shockwaves.append({"r": 10, "max_r": 65, "alpha": 1.0})
                            for _ in range(8):
                                self.sparks.append({
                                    "x": 330 + random.uniform(-20, 20),
                                    "y": 200 + random.uniform(-10, 10),
                                    "vx": random.uniform(-6, 6),
                                    "vy": random.uniform(-8, -2),
                                    "life": 1.0
                                })
                    elif t < 0.65:
                        # Phase 3 : Contrecoup ! La touche de l'utilisateur est éjectée en l'air par le ressort
                        prog = (t - 0.35) / 0.30
                        self.prank_key_depth = 22.0 * (1.0 - prog * 0.4) # Reste bien enfoncée
                        self.user_key_depth = 0.0
                        # Rebond en l'air
                        self.user_key_recoil = math.sin(prog * math.pi) * 26.0
                    else:
                        # Phase 4 : Retour progressif au repos avec oscillations amorties
                        prog = (t - 0.65) / 0.35
                        damping = math.exp(-prog * 4.0)
                        self.prank_key_depth = 12.0 * damping * math.cos(prog * 12.0)
                        self.user_key_recoil = 8.0 * damping * math.sin(prog * 14.0)
                        if t >= 1.1:
                            self.is_animating = False
                            self.user_key_depth = 0.0
                            self.prank_key_depth = 0.0
                            self.user_key_recoil = 0.0
                else:
                    self.user_key_depth = 0.0
                    self.prank_key_depth = 0.0
                    self.user_key_recoil = 0.0
                    
                # Mise à jour des ondes de choc
                new_waves = []
                for sw in self.shockwaves:
                    sw["r"] += 4.5
                    sw["alpha"] -= 0.07
                    if sw["alpha"] > 0 and sw["r"] < sw["max_r"]:
                        new_waves.append(sw)
                self.shockwaves = new_waves
                
                # Mise à jour des étincelles
                new_sparks = []
                for sp in self.sparks:
                    sp["x"] += sp["vx"]
                    sp["y"] += sp["vy"]
                    sp["vy"] += 0.6 # Gravité
                    sp["life"] -= 0.08
                    if sp["life"] > 0:
                        new_sparks.append(sp)
                self.sparks = new_sparks
                
                if self.bubble_timer > 0:
                    self.bubble_timer -= 1
                    
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.sparks.clear()
                    self.shockwaves.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw_mechanical_key(self, kx, ky, char, label_text, is_user_key, depth, recoil):
        """Dessine une touche mécanique 3D ultra détaillée avec switch, ressort et keycap PBT."""
        # Calcul de la position verticale réelle de la touche
        actual_y = ky + depth - recoil
        
        # 1. Base du boîtier du switch mécanique (plaque aluminium de montage)
        base_w, base_h = 100, 36
        self.canvas.create_rectangle(kx - base_w//2, ky + 14, kx + base_w//2, ky + 14 + base_h, fill="#1e293b", outline="#0f172a", width=2)
        self.canvas.create_rectangle(kx - base_w//2 + 4, ky + 18, kx + base_w//2 - 4, ky + 14 + base_h - 4, fill="#0f172a", outline="")
        
        # 2. Ressort hélicoïdal métallique sous la touche
        spring_bottom = ky + 16
        spring_top = actual_y + 12
        spring_h = max(6, spring_bottom - spring_top)
        coils = 5
        pts = [(kx, spring_bottom)]
        for c in range(coils):
            cw = 8 if c % 2 == 0 else -8
            cy_step = spring_bottom - (c + 1) * (spring_h / float(coils))
            pts.append((kx + cw, cy_step))
        for i in range(len(pts) - 1):
            self.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], fill="#94a3b8", width=3)
            
        # 3. Tige en croix Cherry MX (Stem rouge ou bleu)
        stem_color = "#3b82f6" if is_user_key else "#ef4444"
        self.canvas.create_rectangle(kx - 4, actual_y + 6, kx + 4, actual_y + 16, fill=stem_color, outline="#1e293b", width=1)
        self.canvas.create_rectangle(kx - 10, actual_y + 9, kx + 10, actual_y + 13, fill=stem_color, outline="")
        
        # 4. Keycap 3D réaliste (Profil concave avec chanfreins et reflets)
        kw, kh = 84, 54
        tilt_angle = -12.0 if (is_user_key and recoil > 5) else 0.0
        
        # Palette de couleurs du keycap
        if is_user_key:
            # Keycap utilisateur : Gris ardoise / marine sobre
            col_top = "#334155"
            col_front = "#1e293b"
            col_edge = "#475569"
            col_text = "#f8fafc"
        else:
            # Keycap farceur : Ambre / Or électrique éclatant
            col_top = "#f59e0b"
            col_front = "#b45309"
            col_edge = "#fbbf24"
            col_text = "#ffffff"
            
        # A. Face avant / biseau inférieur du keycap (ombre 3D)
        front_pts = [
            (kx - kw//2, actual_y - kh//2 + 10),
            (kx + kw//2, actual_y - kh//2 + 10),
            (kx + kw//2 - 6, actual_y + kh//2),
            (kx - kw//2 + 6, actual_y + kh//2)
        ]
        self.canvas.create_polygon(front_pts, fill=col_front, outline="#0f172a", width=2)
        
        # B. Face supérieure concave du keycap (toucher PBT)
        top_pts = [
            (kx - kw//2 + 6, actual_y - kh//2),
            (kx + kw//2 - 6, actual_y - kh//2),
            (kx + kw//2 - 2, actual_y - kh//2 + 18),
            (kx - kw//2 + 2, actual_y - kh//2 + 18)
        ]
        self.canvas.create_polygon(top_pts, fill=col_top, outline=col_edge, width=2)
        
        # C. Reflet cylindrique concave (lustre sur le dessus de la touche)
        self.canvas.create_line(kx - kw//2 + 12, actual_y - kh//2 + 4, kx + kw//2 - 12, actual_y - kh//2 + 4, fill="#ffffff", width=2)
        
        # D. Lettre gravée sur la touche (Typographie mécanique nette)
        self.canvas.create_text(kx, actual_y - 2, text=char, font=("Impact", 24, "bold"), fill=col_text)
        
        # E. Banderole / Étiquette au-dessus de la touche
        lbl_y = ky - 48
        lbl_col = "#38bdf8" if is_user_key else "#f59e0b"
        self.canvas.create_rectangle(kx - 68, lbl_y - 12, kx + 68, lbl_y + 12, fill="#0f172a", outline=lbl_col, width=2)
        self.canvas.create_text(kx, lbl_y, text=label_text, font=("Impact", 10, "bold"), fill=lbl_col)
        
        # F. Indicateur spécial si la touche rebondit avec confusion
        if is_user_key and recoil > 6:
            self.canvas.create_text(kx + 38, actual_y - 30, text="❓", font=("Segoe UI Emoji", 18))

    def _draw(self):
        self.canvas.delete("all")
        
        # Coordonnées des deux touches
        key1_x = 135  # Touche Utilisateur
        key2_x = 345  # Touche Farceur
        keys_y = 190
        
        # 1. Dessin des deux touches mécaniques
        self._draw_mechanical_key(
            key1_x, keys_y, self.user_char,
            f"VOUS : '{self.user_char}'", True,
            self.user_key_depth, self.user_key_recoil
        )
        self._draw_mechanical_key(
            key2_x, keys_y, self.prank_char,
            f"FARCEUR : '{self.prank_char}'", False,
            self.prank_key_depth, 0.0
        )
        
        # 2. Ondes de choc circulaires sur la touche écrasée
        for sw in self.shockwaves:
            r = sw["r"]
            self.canvas.create_oval(key2_x - r, keys_y + 8 - r*0.4, key2_x + r, keys_y + 8 + r*0.4, outline="#facc15", width=3)
            
        # 3. Étincelles d'impact
        for sp in self.sparks:
            self.canvas.create_text(sp["x"], sp["y"], text="⚡", font=("Segoe UI Emoji", 11))
            
        # 4. Gremlin Farceur avec Maillet Géant
        # Position du gremlin au-dessus de la touche farceur
        gx = 340 + math.sin(self.phase * 2.0) * 3.0
        gy = 75
        
        # Oreilles pointues de lutin/gremlin
        self.canvas.create_polygon([(gx - 30, gy - 16), (gx - 65, gy - 38), (gx - 18, gy - 2)], fill="#a855f7", outline="#581c87", width=2)
        self.canvas.create_polygon([(gx - 28, gy - 14), (gx - 55, gy - 32), (gx - 20, gy - 4)], fill="#f472b6", outline="") # intérieur rose
        self.canvas.create_polygon([(gx + 30, gy - 16), (gx + 65, gy - 38), (gx + 18, gy - 2)], fill="#a855f7", outline="#581c87", width=2)
        self.canvas.create_polygon([(gx + 28, gy - 14), (gx + 55, gy - 32), (gx + 20, gy - 4)], fill="#f472b6", outline="")
        
        # Tête ronde et pelage violet
        self.canvas.create_oval(gx - 32, gy - 28, gx + 32, gy + 28, fill="#9333ea", outline="#581c87", width=3)
        self.canvas.create_polygon([(gx - 8, gy - 28), (gx, gy - 42), (gx + 8, gy - 28)], fill="#a855f7", outline="#581c87", width=2)
        
        # Yeux de chat jaunes félins dorés
        self.canvas.create_oval(gx - 22, gy - 14, gx - 6, gy + 4, fill="#facc15", outline="#713f12", width=2)
        self.canvas.create_oval(gx + 6, gy - 14, gx + 22, gy + 4, fill="#facc15", outline="#713f12", width=2)
        self.canvas.create_line(gx - 14, gy - 12, gx - 14, gy + 2, fill="#0f172a", width=3)
        self.canvas.create_line(gx + 14, gy - 12, gx + 14, gy + 2, fill="#0f172a", width=3)
        
        # Rictus diabolique avec dents acérées
        self.canvas.create_arc(gx - 20, gy - 2, gx + 20, gy + 22, start=180, extent=180, fill="#450a0a", outline="#0f172a", width=2)
        self.canvas.create_polygon([(gx - 12, gy + 10), (gx - 8, gy + 18), (gx - 4, gy + 10)], fill="#ffffff", outline="")
        self.canvas.create_polygon([(gx + 4, gy + 10), (gx + 8, gy + 18), (gx + 12, gy + 10)], fill="#ffffff", outline="")
        
        # 5. Maillet géant en bois tenu par le gremlin
        # Angle du maillet selon l'étape de frappe
        if self.is_animating:
            t = self.anim_t
            if t < 0.20:
                mallet_angle = -45.0  # Levée d'armement
            elif t < 0.38:
                mallet_angle = 65.0   # Écrasement violent sur la touche
            else:
                mallet_angle = 15.0   # Rebond post-choc
        else:
            mallet_angle = -15.0 + math.sin(self.phase * 3.0) * 8.0
            
        mrad = math.radians(mallet_angle)
        hand_x = gx - 20
        hand_y = gy + 18
        
        # Manche du maillet
        m_len = 75.0
        head_x = hand_x + math.cos(mrad) * m_len
        head_y = hand_y + math.sin(mrad) * m_len
        self.canvas.create_line(hand_x, hand_y, head_x, head_y, fill="#b45309", width=6, capstyle=tk.ROUND)
        
        # Tête en bois du maillet (cylindre avec cerclages de fer)
        head_rad = mrad + math.pi/2
        hw, hh = 22, 16
        c1x = head_x - math.cos(head_rad) * hw
        c1y = head_y - math.sin(head_rad) * hw
        c2x = head_x + math.cos(head_rad) * hw
        c2y = head_y + math.sin(head_rad) * hw
        self.canvas.create_line(c1x, c1y, c2x, c2y, fill="#78350f", width=24, capstyle=tk.ROUND)
        # Cerclages d'acier
        self.canvas.create_line(c1x, c1y, c1x + math.cos(mrad)*4, c1y + math.sin(mrad)*4, fill="#94a3b8", width=22)
        self.canvas.create_line(c2x, c2y, c2x - math.cos(mrad)*4, c2y - math.sin(mrad)*4, fill="#94a3b8", width=22)
        
        # Mains griffues tenant le manche
        self.canvas.create_oval(hand_x - 7, hand_y - 7, hand_x + 7, hand_y + 7, fill="#7e22ce", outline="#0f172a", width=2)
        
        # 6. Bulle de texte et effets d'exclamation
        if self.bubble_timer > 0:
            bx = 240
            by = 40
            self.canvas.create_rectangle(bx - 120, by - 16, bx + 120, by + 16, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_text(bx, by, text=self.bubble_text, font=("Impact", 12, "bold"), fill="#dc2626")


# ==============================================================================
# 3. CARTOON GHOST OVERLAY (FANTÔME BIEN PLUS CHIANT ET INTERACTIF)
# ==============================================================================

class CartoonGhostOverlay:
    """
    Poltergeist cartoon hyper interactif et BEAUCOUP PLUS CHIANT :
    1. Traque activement le curseur et se place DIRECTEMENT devant la souris pour bloquer les clics !
    2. Projette des flaques de bave d'ectoplasme gluantes directement sous le curseur.
    3. Fait des jumpscares agressifs rapprochés (zoom 2.5x) avec secousses d'écran et cri de frayeur.
    4. Kidnappe parfois la souris pour la faire tourner en rond.
    5. Feux follets taquins et bulles de dialogues provocatrices !
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
        self.phase = 0.0
        self.visible = False
        self._loop_active = True
        
        # Machine à états chiante : BLOCK_MOUSE, JUMPSCARE, KIDNAP, SLIME_ATTACK
        self.state = "BLOCK_MOUSE"
        self.state_timer = 0
        self.jumpscare_scale = 1.0
        
        # Suivi de la souris
        self.last_mx = self.sw // 2
        self.last_my = self.sh // 2
        self.mouse_idle_frames = 0
        
        # Flaques d'ectoplasme gluant, ondes sonores et feux follets
        self.ectoplasm = []
        self.sound_waves = []
        self.wisps = [
            {"angle": 0.0, "dist": 50, "speed": 0.08},
            {"angle": 2.1, "dist": 70, "speed": -0.06},
            {"angle": 4.2, "dist": 60, "speed": 0.07}
        ]
        self.taunt_text = "T'ESSAIES DE CLIQUER OÙ ? 😜"
        self.taunt_timer = 60
        
        self._tick()

    def trigger_booh(self):
        """Déclenche un jumpscare instantané avec répulsion de souris."""
        self.state = "JUMPSCARE"
        self.state_timer = 0
        self.jumpscare_scale = 2.4
        self.taunt_text = random.choice([
            "BOOOOUH ! 👻⚡", "ATTRAPÉ ! 😂",
            "T'AS CRU POUVOIR CLIQUER ? 😜", "DÉGAGE DE LÀ ! 💥"
        ])
        self.taunt_timer = 40
        self.sound_waves.append({"r": 20, "max_r": 160, "life": 1.0})

    def _tick(self):
        if not self._loop_active:
            return
        try:
            is_active = True
            if "ghost_state" in globals():
                is_active = globals()["ghost_state"].get("active", False)
                
            if is_active:
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                # Position actuelle de la souris
                pt = wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                mx, my = pt.x, pt.y
                
                # Détection d'immobilité de la souris
                if abs(mx - self.last_mx) < 3 and abs(my - self.last_my) < 3:
                    self.mouse_idle_frames += 1
                else:
                    self.mouse_idle_frames = 0
                self.last_mx, self.last_my = mx, my
                
                self.phase += 0.12
                self.state_timer += 1
                
                # Mise à jour des feux follets orbitaux
                for w in self.wisps:
                    w["angle"] += w["speed"]
                    
                # 1. État BLOCK_MOUSE : Le fantôme se place systèmatiquement DIRECTEMENT DEVANT le curseur
                if self.state == "BLOCK_MOUSE":
                    # Cible : 15px au-dessus et à droite du curseur (pile sur la zone de clic !)
                    target_gx = mx + 20
                    target_gy = my - 15
                    
                    # Suivi réactif à haute vélocité (impossible à esquiver facilement)
                    dx = target_gx - self.gx
                    dy = target_gy - self.gy
                    self.gx += dx * 0.28
                    self.gy += dy * 0.28
                    
                    # Flottement organique
                    self.gx += math.sin(self.phase * 2.0) * 4.0
                    self.gy += math.cos(self.phase * 2.5) * 4.0
                    
                    # Si la souris s'arrête plus de 35 frames (~0.7s) -> POUF JUMPSCARE !
                    if self.mouse_idle_frames > 35 and self.state_timer > 60:
                        self.trigger_booh()
                    # Régulièrement, déposer une flaque de bave sous le curseur
                    elif self.state_timer % 90 == 0:
                        self.state = "SLIME_ATTACK"
                        self.state_timer = 0
                    elif self.state_timer > 240 and random.random() < 0.3:
                        self.state = "KIDNAP"
                        self.state_timer = 0
                        
                # 2. État SLIME_ATTACK : Crache de la bave d'ectoplasme gluante sur le curseur
                elif self.state == "SLIME_ATTACK":
                    # Déposer une grosse flaque verte gluante
                    if len(self.ectoplasm) < 14:
                        self.ectoplasm.append({
                            "x": mx,
                            "y": my,
                            "r": random.uniform(22, 38),
                            "drip": 0.0,
                            "max_drip": random.uniform(40, 160),
                            "life": random.uniform(10.0, 18.0)
                        })
                    self.taunt_text = "SPLURP ! UN PEU DE BAVE ? 🧪"
                    self.taunt_timer = 35
                    self.state = "BLOCK_MOUSE"
                    self.state_timer = 0
                    
                # 3. État KIDNAP : Attrape le curseur et le fait tourner en spirale
                elif self.state == "KIDNAP":
                    # Attraction physique du curseur en spirale
                    spiral_r = 50.0 + math.sin(self.state_timer * 0.3) * 30.0
                    k_angle = self.state_timer * 0.25
                    new_cur_x = int(self.gx + math.cos(k_angle) * spiral_r)
                    new_cur_y = int(self.gy + math.sin(k_angle) * spiral_r)
                    try:
                        ctypes.windll.user32.SetCursorPos(new_cur_x, new_cur_y)
                    except Exception:
                        pass
                    self.taunt_text = "C'EST MON CURSEUR ! 🖱️👻"
                    self.taunt_timer = 30
                    if self.state_timer > 50:
                        self.state = "BLOCK_MOUSE"
                        self.state_timer = 0
                        
                # 4. État JUMPSCARE : Grossit subitement, hurle, repousse la souris et secoue la fenêtre
                elif self.state == "JUMPSCARE":
                    self.jumpscare_scale = max(1.0, self.jumpscare_scale - 0.06)
                    # Au tout début du jumpscare : repousser la souris violemment au loin !
                    if self.state_timer == 1:
                        repel_dist = random.uniform(180, 260)
                        repel_ang = random.uniform(0, 2 * math.pi)
                        nx = int(max(40, min(self.sw - 40, mx + math.cos(repel_ang) * repel_dist)))
                        ny = int(max(40, min(self.sh - 40, my + math.sin(repel_ang) * repel_dist)))
                        try:
                            ctypes.windll.user32.SetCursorPos(nx, ny)
                        except Exception:
                            pass
                    if self.state_timer > 30:
                        self.state = "BLOCK_MOUSE"
                        self.state_timer = 0
                        self.jumpscare_scale = 1.0
                        
                # Mise à jour des ondes sonores
                new_waves = []
                for w in self.sound_waves:
                    w["r"] += 5.5
                    w["life"] -= 0.04
                    if w["life"] > 0 and w["r"] < w["max_r"]:
                        new_waves.append(w)
                self.sound_waves = new_waves
                
                # Mise à jour de l'ectoplasme (coulures et vieillissement)
                new_ecto = []
                for e in self.ectoplasm:
                    if e["drip"] < e["max_drip"]:
                        e["drip"] += 1.2
                    e["life"] -= 0.02
                    if e["life"] > 0:
                        new_ecto.append(e)
                self.ectoplasm = new_ecto
                
                if self.taunt_timer > 0:
                    self.taunt_timer -= 1
                    
                self._draw(mx, my)
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.ectoplasm.clear()
                    self.sound_waves.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw(self, mx, my):
        self.canvas.delete("all")
        
        # 1. Flaques d'ectoplasme gluantes dégoulinantes
        for e in self.ectoplasm:
            ex, ey, er, edrip = e["x"], e["y"], e["r"], e["drip"]
            # Flaque avec lobes visqueux
            self.canvas.create_oval(ex - er, ey - er*0.6, ex + er, ey + er*0.6, fill="#22c55e", outline="#15803d", width=2)
            self.canvas.create_oval(ex - er*0.5, ey - er*0.35, ex + er*0.3, ey, fill="#86efac", outline="")
            # Coulure qui dégouline
            if edrip > 2:
                self.canvas.create_line(ex, ey, ex, ey + edrip, fill="#22c55e", width=5, capstyle=tk.ROUND)
                self.canvas.create_oval(ex - 4, ey + edrip - 4, ex + 4, ey + edrip + 6, fill="#16a34a", outline="")
                
        # 2. Feux follets / mini-esprits qui gravitent autour
        for w in self.wisps:
            wx = self.gx + math.cos(w["angle"]) * w["dist"]
            wy = self.gy + math.sin(w["angle"]) * (w["dist"] * 0.6)
            self.canvas.create_oval(wx - 8, wy - 8, wx + 8, wy + 8, fill="#38bdf8", outline="#e0f2fe", width=1)
            self.canvas.create_oval(wx - 4, wy - 4, wx + 4, wy + 4, fill="#ffffff", outline="")
            
        # 3. Ondes sonores de cri spectral
        for w in self.sound_waves:
            r = w["r"]
            self.canvas.create_oval(self.gx - r, self.gy - r, self.gx + r, self.gy + r, outline="#38bdf8", width=3, dash=(6, 3))
            
        # 4. Dessin du fantôme
        scale = self.jumpscare_scale
        cx, cy = self.gx, self.gy
        
        # Aura luminescente spectrale cyan
        for aura_r in [65 * scale, 50 * scale, 38 * scale]:
            self.canvas.create_oval(cx - aura_r, cy - aura_r, cx + aura_r, cy + aura_r, fill="", outline="#38bdf8", width=2)
            
        # Corps drapé ondulant
        bw = 44 * scale
        pts = []
        # Tête arrondie
        for deg in range(0, 185, 15):
            rad = math.radians(deg)
            pts.append((cx + math.cos(rad) * bw, cy - 20 * scale - math.sin(rad) * 42 * scale))
        # Jupe fantomatique flottante
        skirt_y = cy + 38 * scale
        vol_count = 6
        for v in range(vol_count + 1):
            vx = cx - bw + (v * (bw * 2 / float(vol_count)))
            wave = math.sin(self.phase * 4.0 + v * 1.5) * (14 * scale)
            pts.append((vx, skirt_y + wave))
            
        # Corps blanc avec reflet bleuté
        self.canvas.create_polygon(pts, fill="#f8fafc", outline="#0f172a", width=3, smooth=True)
        self.canvas.create_arc(cx - bw + 8, cy - 50 * scale, cx + bw - 8, cy + 10, start=60, extent=60, style="arc", outline="#bae6fd", width=3)
        
        # Yeux & Bouche selon l'état
        eye_y = cy - 22 * scale
        if self.state == "JUMPSCARE":
            # Yeux diaboliques rouges avec fangs hurlants
            self.canvas.create_oval(cx - 24*scale, eye_y - 14*scale, cx - 6*scale, eye_y + 12*scale, fill="#dc2626", outline="#7f1d1d", width=2)
            self.canvas.create_oval(cx + 6*scale, eye_y - 14*scale, cx + 24*scale, eye_y + 12*scale, fill="#dc2626", outline="#7f1d1d", width=2)
            self.canvas.create_oval(cx - 18*scale, eye_y - 8*scale, cx - 12*scale, eye_y + 2*scale, fill="#fef08a", outline="")
            self.canvas.create_oval(cx + 12*scale, eye_y - 8*scale, cx + 18*scale, eye_y + 2*scale, fill="#fef08a", outline="")
            # Bouche grande ouverte hurlante
            self.canvas.create_oval(cx - 22*scale, cy + 6*scale, cx + 22*scale, cy + 34*scale, fill="#0f172a", outline="#94a3b8", width=2)
            self.canvas.create_polygon([(cx - 14*scale, cy + 6*scale), (cx - 9*scale, cy + 16*scale), (cx - 4*scale, cy + 6*scale)], fill="#ffffff", outline="")
            self.canvas.create_polygon([(cx + 4*scale, cy + 6*scale), (cx + 9*scale, cy + 16*scale), (cx + 14*scale, cy + 6*scale)], fill="#ffffff", outline="")
        else:
            # Visage farceur taquin avec langue tirée 😛
            self.canvas.create_oval(cx - 20*scale, eye_y - 10*scale, cx - 4*scale, eye_y + 8*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx + 4*scale, eye_y - 10*scale, cx + 20*scale, eye_y + 8*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx - 15*scale, eye_y - 8*scale, cx - 9*scale, eye_y - 2*scale, fill="#ffffff", outline="")
            self.canvas.create_oval(cx + 9*scale, eye_y - 8*scale, cx + 15*scale, eye_y - 2*scale, fill="#ffffff", outline="")
            # Sourire avec langue rose qui dépasse vers la souris
            self.canvas.create_arc(cx - 18*scale, cy + 2*scale, cx + 18*scale, cy + 22*scale, start=180, extent=180, fill="#0f172a", outline="", width=2)
            # Langue rose qui gigote
            tongue_w = math.sin(self.phase * 5.0) * (6 * scale)
            self.canvas.create_oval(cx - 8*scale + tongue_w, cy + 12*scale, cx + 8*scale + tongue_w, cy + 28*scale, fill="#f43f5e", outline="#9f1239", width=1)
            
        # Mains fantomatiques qui essayent d'attraper la souris
        hx1 = cx - 35 * scale + math.sin(self.phase * 3.0) * 8
        hy1 = cy + 10 * scale
        hx2 = cx + 35 * scale - math.sin(self.phase * 3.0) * 8
        hy2 = cy + 10 * scale
        self.canvas.create_oval(hx1 - 10*scale, hy1 - 8*scale, hx1 + 10*scale, hy1 + 8*scale, fill="#f8fafc", outline="#0f172a", width=2)
        self.canvas.create_oval(hx2 - 10*scale, hy2 - 8*scale, hx2 + 10*scale, hy2 + 8*scale, fill="#f8fafc", outline="#0f172a", width=2)
        
        # 5. Bulle de dialogue chiante
        if self.taunt_timer > 0:
            tx = cx
            ty = cy - 75 * scale
            self.canvas.create_rectangle(tx - 110, ty - 16, tx + 110, ty + 16, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_text(tx, ty, text=self.taunt_text, font=("Impact", int(12 * scale), "bold"), fill="#dc2626")


# ==============================================================================
# 4. CARTOON MESSAGE DELIVERY WINDOW (NOUVELLE FENÊTRE CARTOON CHALEUREUSE)
# ==============================================================================

def show_cartoon_troll_window_on_client(text, on_close=None):
    """
    Remplacement TOTAL de l'ancienne fenêtre néon/hacker :
    Un grand personnage cartoon coursier express surgit du haut de l'écran en élastique (bungee)
    avec squash & stretch et claque sur l'écran un grand panneau de bois et parchemin chaleureux
    sans aucun néon, avec sceau de cire, texte ultra lisible et bouton 3D cartoon !
    """
    win = tk.Toplevel()
    win.title("LIVRAISON SPÉCIALE 📬")
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.attributes("-transparentcolor", "#010101")
    win.configure(bg="#010101")
    
    w, h = 640, 520
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2 - 30
    win.geometry(f"{w}x{h}+{x}+{y}")
    
    canvas = tk.Canvas(win, width=w, height=h, bg="#010101", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # État d'animation d'arrivée en élastique (Bungee drop)
    anim_data = {
        "t": 0.0,
        "offset_y": -500.0,
        "vel_y": 0.0,
        "settled": False,
        "dust_clouds": [],
        "closing": False,
        "close_t": 0.0
    }
    
    def _close_window():
        if anim_data["closing"]:
            return
        anim_data["closing"] = True
        anim_data["close_t"] = 0.0

    def _cleanup():
        try:
            win.destroy()
        except Exception:
            pass
        if on_close:
            try:
                on_close()
            except Exception:
                pass

    # Raccourcis clavier pour fermer
    win.bind("<Escape>", lambda e: _close_window())
    win.bind("<Return>", lambda e: _close_window())
    win.bind("<space>", lambda e: _close_window())
    
    def _tick_anim():
        try:
            if not win.winfo_exists():
                return
                
            if not anim_data["closing"]:
                # Physique d'arrivée en élastique (Ressort amorti)
                target_y = 0.0
                k = 0.18      # Raideur du ressort
                damp = 0.72   # Amortissement
                
                force = (target_y - anim_data["offset_y"]) * k
                anim_data["vel_y"] = (anim_data["vel_y"] + force) * damp
                anim_data["offset_y"] += anim_data["vel_y"]
                
                if abs(anim_data["offset_y"]) < 1.0 and abs(anim_data["vel_y"]) < 0.5:
                    anim_data["offset_y"] = 0.0
                    if not anim_data["settled"]:
                        anim_data["settled"] = True
                        # Nuages de poussière d'impact cartoon
                        for _ in range(6):
                            anim_data["dust_clouds"].append({
                                "x": 320 + random.uniform(-180, 180),
                                "y": 440 + random.uniform(-10, 10),
                                "r": random.uniform(12, 24),
                                "life": 1.0
                            })
            else:
                # Animation de fermeture rapide : le personnage remonte en élastique à toute vitesse !
                anim_data["close_t"] += 1.0
                anim_data["offset_y"] -= anim_data["close_t"] * 35.0
                if anim_data["offset_y"] < -550.0:
                    _cleanup()
                    return
                    
            # Mise à jour des nuages de poussière
            new_dust = []
            for dc in anim_data["dust_clouds"]:
                dc["r"] += 1.2
                dc["life"] -= 0.06
                if dc["life"] > 0:
                    new_dust.append(dc)
            anim_data["dust_clouds"] = new_dust
            
            _render()
            win.after(20, _tick_anim)
        except Exception:
            _cleanup()

    def _render():
        canvas.delete("all")
        cur_oy = anim_data["offset_y"]
        
        # 1. Corde élastique / Bungee depuis le haut de l'écran jusqu'à la casquette
        cx = 320
        rope_end_y = max(0, 70 + cur_oy)
        canvas.create_line(cx, 0, cx, rope_end_y, fill="#78350f", width=5)
        canvas.create_line(cx - 1, 0, cx - 1, rope_end_y, fill="#d97706", width=2)
        
        # 2. Nuages de poussière cartoon à l'atterrissage
        for dc in anim_data["dust_clouds"]:
            dr = dc["r"]
            canvas.create_oval(dc["x"] - dr, dc["y"] - dr*0.6, dc["x"] + dr, dc["y"] + dr*0.6, fill="#e2e8f0", outline="#cbd5e1", width=1)
            
        # 3. Grand Panneau de Bois et Parchemin Chaleureux
        board_y = 150 + cur_oy
        bw, bh = 560, 310
        bx1 = cx - bw // 2
        by1 = board_y
        bx2 = cx + bw // 2
        by2 = board_y + bh
        
        # Ombre portée du panneau
        canvas.create_rectangle(bx1 + 8, by1 + 8, bx2 + 8, by2 + 8, fill="#0f172a", outline="")
        
        # Cadre en bois rustique caramel / chêne chaud (Zéro néon !)
        canvas.create_rectangle(bx1, by1, bx2, by2, fill="#78350f", outline="#451a03", width=5)
        canvas.create_rectangle(bx1 + 10, by1 + 10, bx2 - 10, by2 - 10, fill="#92400e", outline="#78350f", width=2)
        
        # Clous en laiton doré aux 4 coins
        for (nx, ny) in [(bx1 + 16, by1 + 16), (bx2 - 16, by1 + 16), (bx1 + 16, by2 - 16), (bx2 - 16, by2 - 16)]:
            canvas.create_oval(nx - 6, ny - 6, nx + 6, ny + 6, fill="#f59e0b", outline="#78350f", width=2)
            canvas.create_line(nx - 3, ny - 3, nx + 3, ny + 3, fill="#451a03", width=2)
            
        # Parchemin intérieur crème / ivoire chaleureux
        canvas.create_rectangle(bx1 + 22, by1 + 22, bx2 - 22, by2 - 22, fill="#fef3c7", outline="#fde68a", width=2)
        
        # Ruban rouge élégant en en-tête
        rub_y = by1 + 42
        canvas.create_polygon([
            (bx1 + 45, rub_y - 18), (bx2 - 45, rub_y - 18),
            (bx2 - 35, rub_y), (bx2 - 45, rub_y + 18),
            (bx1 + 45, rub_y + 18), (bx1 + 35, rub_y)
        ], fill="#dc2626", outline="#991b1b", width=2)
        canvas.create_text(cx, rub_y, text="📬 MESSAGE DE AHMED 📬", font=("Impact", 13, "bold"), fill="#ffffff")
        
        # Corps du message d'Ahmed (Encre noire / anthracite ultra lisible)
        raw_text = text if text else "Aucun message reçu."
        clean_msg = raw_text.strip()
        if clean_msg.upper().startswith("AHMED:"):
            clean_msg = clean_msg[6:].strip()
        elif clean_msg.upper().startswith("MESSAGE DE AHMED:"):
            clean_msg = clean_msg[17:].strip()
        elif clean_msg.upper().startswith("MESSAGE DU VIEWER:"):
            clean_msg = clean_msg[18:].strip()
        elif clean_msg.upper().startswith("MESSAGE:"):
            clean_msg = clean_msg[8:].strip()
            
        display_msg = f"MESSAGE DE AHMED :\n« {clean_msg} »"
            
        canvas.create_text(
            cx, by1 + 140, text=display_msg,
            font=("Arial Black", 12), fill="#0f172a",
            width=480, justify="center"
        )
        
        # Sceau de cire rouge officiel en bas à gauche
        seal_x = bx1 + 65
        seal_y = by2 - 50
        canvas.create_oval(seal_x - 22, seal_y - 22, seal_x + 22, seal_y + 22, fill="#b91c1c", outline="#7f1d1d", width=3)
        canvas.create_text(seal_x, seal_y, text="POSTE\nOFFICIELLE", font=("Impact", 6, "bold"), fill="#fef08a", justify="center")
        
        # Bouton Cartoon 3D interactif "J'AI COMPRIS ! 👍"
        btn_w, btn_h = 220, 44
        btn_x1 = cx - btn_w // 2 + 30
        btn_y1 = by2 - 62
        btn_x2 = btn_x1 + btn_w
        btn_y2 = btn_y1 + btn_h
        
        # Ombre bouton
        canvas.create_rectangle(btn_x1 + 3, btn_y1 + 3, btn_x2 + 3, btn_y2 + 3, fill="#0f172a", outline="")
        # Fond vert émeraude 3D
        btn_tag = canvas.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#16a34a", outline="#14532d", width=3)
        # Reflet blanc sur le haut du bouton
        canvas.create_line(btn_x1 + 6, btn_y1 + 4, btn_x2 - 6, btn_y1 + 4, fill="#86efac", width=3)
        btn_text = canvas.create_text(btn_x1 + btn_w//2, btn_y1 + btn_h//2, text="J'AI COMPRIS ! 👍", font=("Impact", 13, "bold"), fill="#ffffff")
        
        # Événement de clic sur le bouton
        canvas.tag_bind(btn_tag, "<Button-1>", lambda e: _close_window())
        canvas.tag_bind(btn_text, "<Button-1>", lambda e: _close_window())
        canvas.tag_bind(btn_tag, "<Enter>", lambda e: canvas.itemconfig(btn_tag, fill="#22c55e"))
        canvas.tag_bind(btn_tag, "<Leave>", lambda e: canvas.itemconfig(btn_tag, fill="#16a34a"))
        
        # 4. Grand Personnage Cartoon Perché au-dessus du Panneau
        char_x = cx
        char_y = board_y - 20
        
        # Bras et gants blancs cartoon tenant les bords du panneau
        canvas.create_line(char_x - 35, char_y + 10, bx1 + 35, by1 + 10, fill="#1e3a8a", width=12, capstyle=tk.ROUND)
        canvas.create_oval(bx1 + 25, by1, bx1 + 45, by1 + 20, fill="#ffffff", outline="#0f172a", width=2) # Gant blanc gauche
        
        canvas.create_line(char_x + 35, char_y + 10, bx2 - 35, by1 + 10, fill="#1e3a8a", width=12, capstyle=tk.ROUND)
        canvas.create_oval(bx2 - 45, by1, bx2 - 25, by1 + 20, fill="#ffffff", outline="#0f172a", width=2) # Gant blanc droit
        
        # Corps : Veste bleue de livreur avec boutons dorés
        canvas.create_oval(char_x - 34, char_y - 15, char_x + 34, char_y + 35, fill="#1d4ed8", outline="#0f172a", width=3)
        canvas.create_oval(char_x - 4, char_y, char_x + 4, char_y + 8, fill="#facc15", outline="")
        canvas.create_oval(char_x - 4, char_y + 14, char_x + 4, char_y + 22, fill="#facc15", outline="")
        
        # Tête ronde et joues roses
        head_y = char_y - 40
        canvas.create_oval(char_x - 30, head_y - 30, char_x + 30, head_y + 30, fill="#fed7aa", outline="#c2410c", width=3)
        canvas.create_oval(char_x - 32, head_y + 4, char_x - 18, head_y + 18, fill="#fca5a5", outline="")
        canvas.create_oval(char_x + 18, head_y + 4, char_x + 32, head_y + 18, fill="#fca5a5", outline="")
        
        # Grands yeux globuleux cartoon expressifs
        canvas.create_oval(char_x - 22, head_y - 18, char_x - 3, head_y + 8, fill="#ffffff", outline="#0f172a", width=2)
        canvas.create_oval(char_x + 3, head_y - 18, char_x + 22, head_y + 8, fill="#ffffff", outline="#0f172a", width=2)
        canvas.create_oval(char_x - 14, head_y - 12, char_x - 6, head_y - 2, fill="#0f172a", outline="")
        canvas.create_oval(char_x + 6, head_y - 12, char_x + 14, head_y - 2, fill="#0f172a", outline="")
        canvas.create_oval(char_x - 12, head_y - 10, char_x - 9, head_y - 6, fill="#ffffff", outline="")
        canvas.create_oval(char_x + 8, head_y - 10, char_x + 11, head_y - 6, fill="#ffffff", outline="")
        
        # Grand sourire chaleureux
        canvas.create_arc(char_x - 18, head_y + 2, char_x + 18, head_y + 24, start=180, extent=180, fill="#450a0a", outline="#0f172a", width=2)
        canvas.create_polygon([(char_x - 8, head_y + 12), (char_x, head_y + 18), (char_x + 8, head_y + 12)], fill="#ffffff", outline="")
        
        # Casquette officielle de livreur avec écusson doré
        cap_y = head_y - 26
        canvas.create_oval(char_x - 36, cap_y - 16, char_x + 36, cap_y + 10, fill="#1e3a8a", outline="#0f172a", width=3)
        # Visière courbée
        canvas.create_arc(char_x - 40, cap_y - 4, char_x + 40, cap_y + 20, start=0, extent=180, fill="#0f172a", outline="")
        # Écusson doré "EXPRESS"
        canvas.create_oval(char_x - 9, cap_y - 10, char_x + 9, cap_y + 6, fill="#facc15", outline="#713f12", width=1)
        canvas.create_text(char_x, cap_y - 2, text="★", font=("Arial", 10, "bold"), fill="#78350f")
        
    _tick_anim()
    return win


# ==============================================================================
# MENU PRINCIPAL DE TEST
# ==============================================================================

def main():
    root = tk.Tk()
    root.title("Testeur des 4 Nouveaux Cartoons")
    root.geometry("450x380+100+100")
    root.configure(bg="#1e293b")
    
    lbl = tk.Label(
        root, text="PROTOTYPAGE DES 4 CARTOONS REFAITS\nCliquez sur les boutons pour tester :",
        font=("Arial", 12, "bold"), bg="#1e293b", fg="#f8fafc"
    )
    lbl.pack(pady=15)
    
    # 1. Peintre
    globals()["painter_state"] = {"active": True}
    painter_overlay = CartoonPainterOverlay(root)
    
    # 2. Clavier fou
    globals()["keys_state"] = {"active": True}
    keys_overlay = CartoonKeysOverlay(root)
    
    # 3. Fantôme chiant
    globals()["ghost_state"] = {"active": True}
    ghost_overlay = CartoonGhostOverlay(root)
    
    def test_painter_throw():
        painter_overlay.throw_state = "WINDUP"
        painter_overlay.throw_timer = 0
        
    def test_keys_swap():
        keys_overlay.trigger_key_swap("Z", "O")
        
    def test_ghost_jumpscare():
        ghost_overlay.trigger_booh()
        
    def test_delivery_window():
        show_cartoon_troll_window_on_client("Salut l'ami ! Voici ton message spécial livré en direct par le facteur cartoon express !")
        
    btn_style = {"font": ("Arial", 11, "bold"), "width": 32, "pady": 6}
    
    tk.Button(root, text="1. Lancer un Pinceau (Peintre 🎨)", bg="#ef4444", fg="#ffffff", command=test_painter_throw, **btn_style).pack(pady=6)
    tk.Button(root, text="2. Taper Touche 'Z' -> Écraser 'O' (Clavier ⌨️)", bg="#f59e0b", fg="#0f172a", command=test_keys_swap, **btn_style).pack(pady=6)
    tk.Button(root, text="3. Jumpscare Fantôme Chiant (BOOOH 👻)", bg="#06b6d4", fg="#0f172a", command=test_ghost_jumpscare, **btn_style).pack(pady=6)
    tk.Button(root, text="4. Ouvrir Fenêtre Message Cartoon (📬)", bg="#22c55e", fg="#0f172a", command=test_delivery_window, **btn_style).pack(pady=6)
    
    root.mainloop()

if __name__ == "__main__":
    main()

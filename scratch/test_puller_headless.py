import tkinter as tk
import math
import random
import ctypes

class CartoonPullerOverlay:
    """
    Bonhomme cartoon musclé qui attrape la souris avec une corde et la tracte
    vers l'avant en courant (sens physique et graphique 100% cohérent : court en avant,
    incliné dans le sens de la traction, corde tendue vers l'arrière reliée à la souris,
    nuages de poussière, sueur et rubans propulsés vers l'arrière).
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        # Dimensions généreuses pour contenir à la fois le coureur, la corde entière et la souris
        self.w, self.h = 440, 280
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
        self.facing = 1.0 # 1.0 = court vers la droite, -1.0 = court vers la gauche
        self.sweat_drops = []
        self.dust_puffs = []
        self.visible = False
        self.speech_timer = 0
        self.speech_text = "HO-ISSE ! 🏃‍♂️💨"
        self._loop_active = True
        
    def _tick_headless_test(self, mx, my, dx, dy):
        """Simulation tick for testing."""
        self.phase += 0.35
        if dx > 1.2:
            self.facing = 1.0
        elif dx < -1.2:
            self.facing = -1.0
            
        dist_ahead = 135
        char_screen_x = mx + int(self.facing * dist_ahead)
        char_screen_y = my - 12
        
        center_x = (mx + char_screen_x) // 2
        center_y = (my + char_screen_y) // 2
        
        wx = int(center_x - (self.w // 2))
        wy = int(center_y - (self.h // 2))
        
        canvas_mx = mx - wx
        canvas_my = my - wy
        canvas_cx = char_screen_x - wx
        canvas_cy = char_screen_y - wy
        
        self._draw(canvas_cx, canvas_cy, canvas_mx, canvas_my)
        
    def _draw(self, cx, cy, mx, my):
        self.canvas.delete("all")
        facing = self.facing
        
        # 1. Poussière de course / dérapage projetée en ARRIÈRE du mouvement (-facing)
        if random.random() < 0.45:
            self.dust_puffs.append({
                "x": cx - (facing * 28) + random.uniform(-10, 10),
                "y": cy + 58 + random.uniform(-4, 4),
                "vx": -facing * random.uniform(2.5, 5.5),
                "vy": random.uniform(-2.2, 0.4),
                "r": random.uniform(5.5, 9.5),
                "life": 1.0
            })
            
        new_dust = []
        for d in self.dust_puffs:
            d["x"] += d["vx"]
            d["y"] += d["vy"]
            d["r"] += 0.8
            d["life"] -= 0.08
            if d["life"] > 0:
                self.canvas.create_oval(d["x"] - d["r"], d["y"] - d["r"]*0.7, d["x"] + d["r"], d["y"] + d["r"]*0.7, fill="#64748b", outline="")
                new_dust.append(d)
        self.dust_puffs = new_dust
        
        # 2. Lignes de vitesse cartoon projetées en arrière (-facing)
        for l in range(3):
            ly = cy - 20 + l * 24
            lx_start = cx - facing * 35
            lx_end = cx - facing * (75 + math.sin(self.phase + l) * 14)
            self.canvas.create_line(lx_start, ly, lx_end, ly, fill="#cbd5e1", width=2, dash=(4, 2))
            
        # 3. Ombre au sol sous le coureur
        shadow_rx = 34
        shadow_ry = 9
        self.canvas.create_oval(cx - shadow_rx, cy + 62 - shadow_ry, cx + shadow_rx, cy + 62 + shadow_ry, fill="#020617", outline="")
        
        # 4. Cycle de course effréné des jambes cartoon
        stride = math.sin(self.phase * 1.8) * 26.0
        leg_lift_f = max(0.0, math.cos(self.phase * 1.8)) * 18.0
        leg_lift_b = max(0.0, -math.cos(self.phase * 1.8)) * 18.0
        
        hip_x = cx - facing * 6
        hip_y = cy + 16
        
        # Jambe avant (attaque vers l'avant dans le sens facing)
        foot_front_x = hip_x + (facing * 22) + (facing * stride)
        foot_front_y = cy + 58 - leg_lift_f
        knee_front_x = (hip_x + foot_front_x) / 2.0 + (facing * 10)
        knee_front_y = (hip_y + foot_front_y) / 2.0 - 6
        
        # Jambe arrière (pousse vers l'arrière)
        foot_back_x = hip_x - (facing * 20) - (facing * stride)
        foot_back_y = cy + 58 - leg_lift_b
        knee_back_x = (hip_x + foot_back_x) / 2.0 - (facing * 8)
        knee_back_y = (hip_y + foot_back_y) / 2.0 - 6
        
        # Rendu pantalon d'effort bleu sportif
        self.canvas.create_line(hip_x, hip_y, knee_back_x, knee_back_y, fill="#0f172a", width=14, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, knee_back_x, knee_back_y, fill="#1d4ed8", width=9, capstyle=tk.ROUND)
        self.canvas.create_line(knee_back_x, knee_back_y, foot_back_x, foot_back_y, fill="#0f172a", width=13, capstyle=tk.ROUND)
        self.canvas.create_line(knee_back_x, knee_back_y, foot_back_x, foot_back_y, fill="#1d4ed8", width=8, capstyle=tk.ROUND)
        
        self.canvas.create_line(hip_x, hip_y, knee_front_x, knee_front_y, fill="#0f172a", width=14, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, knee_front_x, knee_front_y, fill="#2563eb", width=9, capstyle=tk.ROUND)
        self.canvas.create_line(knee_front_x, knee_front_y, foot_front_x, foot_front_y, fill="#0f172a", width=13, capstyle=tk.ROUND)
        self.canvas.create_line(knee_front_x, knee_front_y, foot_front_x, foot_front_y, fill="#2563eb", width=8, capstyle=tk.ROUND)
        
        # Baskets de sport cartoon rouges à semelles blanches
        for fx, fy in [(foot_back_x, foot_back_y), (foot_front_x, foot_front_y)]:
            self.canvas.create_oval(fx - 14, fy + 2, fx + 14, fy + 9, fill="#f8fafc", outline="#0f172a", width=2)
            self.canvas.create_polygon([
                fx - facing * 12, fy + 3,
                fx + facing * 16, fy + 3,
                fx + facing * 13, fy - 6,
                fx - facing * 8, fy - 9,
                fx - facing * 12, fy - 4
            ], fill="#ef4444", outline="#0f172a", width=2)
            
        # 5. Torse musclé penché EN AVANT dans la direction du mouvement
        lean_angle = facing * 30.0
        lean_rad = math.radians(lean_angle)
        bob = math.sin(self.phase * 3.6) * 3.5
        
        shoulder_x = hip_x + math.sin(lean_rad) * 44.0
        shoulder_y = hip_y - math.cos(lean_rad) * 44.0 + bob
        
        # Débardeur de sport orange vif
        self.canvas.create_line(hip_x, hip_y, shoulder_x, shoulder_y, fill="#0f172a", width=26, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, shoulder_x, shoulder_y, fill="#ea580c", width=20, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x + facing*2, hip_y - 2, shoulder_x + facing*2, shoulder_y - 2, fill="#f97316", width=8, capstyle=tk.ROUND)
        
        # 6. Bras musclés en pleine traction de la corde vers l'arrière (-facing)
        torso_cy = (hip_y + shoulder_y) / 2.0
        hands_x = hip_x - (facing * 12)
        hands_y = torso_cy + 4
        
        # Bras arrière
        self.canvas.create_line(shoulder_x - facing*5, shoulder_y + 4, hands_x - facing*6, hands_y - 4, fill="#0f172a", width=12, capstyle=tk.ROUND)
        self.canvas.create_line(shoulder_x - facing*5, shoulder_y + 4, hands_x - facing*6, hands_y - 4, fill="#fed7aa", width=8, capstyle=tk.ROUND)
        self.canvas.create_oval(shoulder_x - 8, shoulder_y - 2, shoulder_x + 8, shoulder_y + 14, fill="#fed7aa", outline="#c2410c", width=2)
        
        # Bras avant
        self.canvas.create_line(shoulder_x + facing*6, shoulder_y + 6, hands_x + facing*6, hands_y, fill="#0f172a", width=13, capstyle=tk.ROUND)
        self.canvas.create_line(shoulder_x + facing*6, shoulder_y + 6, hands_x + facing*6, hands_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
        
        # Gants de force marrons agrippant la corde
        self.canvas.create_oval(hands_x - 10, hands_y - 8, hands_x + 10, hands_y + 8, fill="#92400e", outline="#0f172a", width=2)
        self.canvas.create_oval(hands_x - 4 + facing*6, hands_y - 6, hands_x + 12 + facing*6, hands_y + 6, fill="#b45309", outline="#0f172a", width=2)
        
        # 7. Tête expressive déterminée, regardant devant vers facing
        head_x = shoulder_x + (facing * 12)
        head_y = shoulder_y - 20
        
        # Visage en sueur
        self.canvas.create_oval(head_x - 19, head_y - 19, head_x + 19, head_y + 19, fill="#fed7aa", outline="#c2410c", width=3)
        self.canvas.create_oval(head_x + facing*6 - 6, head_y + 3, head_x + facing*6 + 8, head_y + 11, fill="#fca5a5", outline="")
        
        # Yeux concentrés
        eye_x = head_x + (facing * 7)
        eye_y = head_y - 3
        self.canvas.create_oval(eye_x - 5, eye_y - 5, eye_x + 5, eye_y + 5, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_oval(eye_x + facing*2 - 2, eye_y - 2, eye_x + facing*2 + 2, eye_y + 2, fill="#0f172a", outline="")
        self.canvas.create_line(eye_x - facing*8, eye_y - 8, eye_x + facing*6, eye_y - 5, fill="#7c2d12", width=4)
        
        # Dents serrées de grimace d'effort
        mouth_x = head_x + (facing * 9)
        mouth_y = head_y + 9
        self.canvas.create_rectangle(mouth_x - 8, mouth_y - 4, mouth_x + 8, mouth_y + 4, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_line(mouth_x - 4, mouth_y - 4, mouth_x - 4, mouth_y + 4, fill="#0f172a", width=1)
        self.canvas.create_line(mouth_x + 2, mouth_y - 4, mouth_x + 2, mouth_y + 4, fill="#0f172a", width=1)
        self.canvas.create_line(mouth_x - 8, mouth_y, mouth_x + 8, mouth_y, fill="#0f172a", width=1)
        
        # Bandeau ninja rouge vif sur le front
        band_y = head_y - 10
        self.canvas.create_line(head_x - 20, band_y, head_x + 20, band_y, fill="#ef4444", width=7)
        # Rubans flottant au vent vers l'arrière (-facing)
        ribbon_wave = math.sin(self.phase * 4.5) * 8.0
        self.canvas.create_line(head_x - facing*18, band_y, head_x - facing*45, band_y - 8 + ribbon_wave, fill="#dc2626", width=4)
        self.canvas.create_line(head_x - facing*18, band_y, head_x - facing*40, band_y + 8 - ribbon_wave, fill="#b91c1c", width=4)
        
        # 8. Gouttes de sueur qui giclent vers l'arrière (-facing)
        if random.random() < 0.35:
            self.sweat_drops.append({
                "x": head_x + random.uniform(-6, 6),
                "y": head_y - 12,
                "vx": -facing * random.uniform(2.5, 6.0),
                "vy": random.uniform(-3.5, -0.5),
                "life": 1.0
            })
            
        new_sweat = []
        for s in self.sweat_drops:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.4
            s["life"] -= 0.1
            if s["life"] > 0:
                self.canvas.create_oval(s["x"] - 3, s["y"] - 4, s["x"] + 3, s["y"] + 4, fill="#38bdf8", outline="#0284c7", width=1)
                new_sweat.append(s)
        self.sweat_drops = new_sweat
        
        # 9. Corde nautique torsadée ultra-tendue reliant les mains à la souris (vers l'arrière -facing)
        rope_vib = math.sin(self.phase * 8.0) * 3.0
        mid_rx = (hands_x + mx) / 2.0
        mid_ry = (hands_y + my) / 2.0 + rope_vib
        
        self.canvas.create_line(hands_x, hands_y, mid_rx, mid_ry, fill="#78350f", width=6)
        self.canvas.create_line(mid_rx, mid_ry, mx, my, fill="#78350f", width=6)
        self.canvas.create_line(hands_x, hands_y, mid_rx, mid_ry, fill="#d97706", width=3, dash=(6, 3))
        self.canvas.create_line(mid_rx, mid_ry, mx, my, fill="#d97706", width=3, dash=(6, 3))
        
        # Nœud coulant cartoon / grappin enserrant la souris
        self.canvas.create_oval(mx - 15, my - 15, mx + 15, my + 15, outline="#b45309", width=3)
        self.canvas.create_line(mx - 18, my - 4, mx + 18, my - 4, fill="#78350f", width=4)
        self.canvas.create_line(mx - 18, my + 4, mx + 18, my + 4, fill="#78350f", width=4)
        self.canvas.create_text(mx, my - 20, text="🪢", font=("Segoe UI Emoji", 14))
        
        # Curseur de souris cartoon simulé
        self.canvas.create_polygon([
            mx, my,
            mx, my + 24,
            mx + 6, my + 18,
            mx + 13, my + 28,
            mx + 17, my + 26,
            mx + 10, my + 16,
            mx + 18, my + 16
        ], fill="#ffffff", outline="#000000", width=2)
        
        # Lignes de friction / dérapage sous le curseur traîné
        self.canvas.create_line(mx - facing*10, my + 22, mx - facing*30, my + 22, fill="#f59e0b", width=3, dash=(3, 3))
        self.canvas.create_line(mx - facing*10, my + 28, mx - facing*25, my + 28, fill="#f59e0b", width=2, dash=(3, 3))
        
        # 10. Bulle de dialogue comique
        self.speech_timer = (self.speech_timer + 1) % 45
        if self.speech_timer == 1:
            self.speech_text = random.choice([
                "AVANCE ! HO-ISSE ! 🏃‍♂️💨",
                "C'EST DU LOURD ! 💥",
                "TIIIIRE LA SOURIS ! 🐭",
                "PAR ICI LE CURSEUR ! ⚡",
                "HNNNGH ! ÇA VIENT ! 💪"
            ])
            
        bubble_x = cx + facing * 20
        bubble_y = cy - 65
        self.canvas.create_text(bubble_x, bubble_y, text=self.speech_text, font=("Impact", 13, "bold"), fill="#f97316")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    overlay = CartoonPullerOverlay(root)
    # Test 100 frames moving right
    for i in range(50):
        overlay._tick_headless_test(300 + i * 2, 400, 4.0, 0.0)
    # Test 100 frames moving left
    for i in range(50):
        overlay._tick_headless_test(400 - i * 2, 400, -4.0, 0.0)
    print("50 right frames and 50 left frames tested successfully!")
    root.destroy()

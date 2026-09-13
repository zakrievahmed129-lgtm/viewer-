import tkinter as tk
import math
import random

class CartoonPullerTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Direction Bonhomme qui Tire la Souris")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e293b")
        
        self.canvas = tk.Canvas(self.root, width=980, height=620, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        self.phase = 0.0
        self.dust_puffs = []
        self.sweat_drops = []
        
        # Souris simulée
        self.mx = 450
        self.my = 350
        self.vx = 8.0 # Déplacement vers la DROITE
        
        self.btn_frame = tk.Frame(self.root, bg="#1e293b")
        self.btn_frame.pack()
        
        tk.Button(self.btn_frame, text="Tirer vers la DROITE (->)", command=self.set_right, bg="#22c55e", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=10)
        tk.Button(self.btn_frame, text="Tirer vers la GAUCHE (<-)", command=self.set_left, bg="#ef4444", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=10)
        
        self.info_lbl = tk.Label(self.root, text="", bg="#1e293b", fg="white", font=("Arial", 12))
        self.info_lbl.pack(pady=5)
        
        self._tick()
        
    def set_right(self):
        self.vx = 8.0
        
    def set_left(self):
        self.vx = -8.0
        
    def _tick(self):
        self.phase += 0.35
        
        # La souris avance dans la direction vx
        self.mx += self.vx
        if self.mx > 750:
            self.vx = -8.0
        elif self.mx < 250:
            self.vx = 8.0
            
        facing = 1.0 if self.vx >= 0 else -1.0
        self.info_lbl.config(text=f"Direction du mouvement: {'DROITE (->)' if facing > 0 else 'GAUCHE (<-)'} | Bonhomme EN AVANT, tire la souris DERRIERE LUI !")
        
        self._draw(self.mx, self.my, facing)
        self.root.after(30, self._tick)
        
    def _draw(self, mx, my, facing):
        self.canvas.delete("all")
        
        # Le bonhomme est EN AVANT de la souris dans le sens du mouvement
        dist_ahead = 135
        cx = mx + (facing * dist_ahead)
        cy = my - 15
        
        # Sol / ombre sous le personnage
        shadow_rx = 36
        shadow_ry = 10
        self.canvas.create_oval(cx - shadow_rx, cy + 62 - shadow_ry, cx + shadow_rx, cy + 62 + shadow_ry, fill="#020617", outline="")
        
        # 1. Poussière de course / dérapage projetée en ARRIÈRE du mouvement (-facing)
        if random.random() < 0.45:
            self.dust_puffs.append({
                "x": cx - (facing * 30) + random.uniform(-10, 10),
                "y": cy + 58 + random.uniform(-5, 5),
                "vx": -facing * random.uniform(2, 5),
                "vy": random.uniform(-2, 0.5),
                "r": random.uniform(5, 9),
                "life": 1.0
            })
            
        new_dust = []
        for d in self.dust_puffs:
            d["x"] += d["vx"]
            d["y"] += d["vy"]
            d["r"] += 0.9
            d["life"] -= 0.08
            if d["life"] > 0:
                self.canvas.create_oval(d["x"] - d["r"], d["y"] - d["r"]*0.7, d["x"] + d["r"], d["y"] + d["r"]*0.7, fill="#64748b", outline="")
                new_dust.append(d)
        self.dust_puffs = new_dust
        
        # 2. Lignes de vitesse cartoon projetées en arrière (-facing)
        for l in range(3):
            ly = cy - 20 + l * 25
            lx_start = cx - facing * 40
            lx_end = cx - facing * (75 + math.sin(self.phase + l) * 15)
            self.canvas.create_line(lx_start, ly, lx_end, ly, fill="#94a3b8", width=2, dash=(4, 2))
            
        # 3. Cycle de course cartoon effréné des jambes (run cycle vigoureux)
        # Foulée rythmée par self.phase
        stride = math.sin(self.phase * 1.6) * 28.0
        leg_lift_f = max(0.0, math.cos(self.phase * 1.6)) * 18.0
        leg_lift_b = max(0.0, -math.cos(self.phase * 1.6)) * 18.0
        
        hip_x = cx - facing * 5
        hip_y = cy + 15
        
        # Jambe avant (celle qui attaque vers l'avant dans le sens facing)
        foot_front_x = hip_x + (facing * 20) + (facing * stride)
        foot_front_y = cy + 58 - leg_lift_f
        knee_front_x = (hip_x + foot_front_x) / 2.0 + (facing * 10)
        knee_front_y = (hip_y + foot_front_y) / 2.0 - 6
        
        # Jambe arrière (celle qui pousse en arrière)
        foot_back_x = hip_x - (facing * 20) - (facing * stride)
        foot_back_y = cy + 58 - leg_lift_b
        knee_back_x = (hip_x + foot_back_x) / 2.0 - (facing * 8)
        knee_back_y = (hip_y + foot_back_y) / 2.0 - 6
        
        # Rendu des jambes en pantalon d'effort bleu vif
        # Cuisse / mollet arrière
        self.canvas.create_line(hip_x, hip_y, knee_back_x, knee_back_y, fill="#0f172a", width=13, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, knee_back_x, knee_back_y, fill="#1d4ed8", width=9, capstyle=tk.ROUND)
        self.canvas.create_line(knee_back_x, knee_back_y, foot_back_x, foot_back_y, fill="#0f172a", width=12, capstyle=tk.ROUND)
        self.canvas.create_line(knee_back_x, knee_back_y, foot_back_x, foot_back_y, fill="#1d4ed8", width=8, capstyle=tk.ROUND)
        
        # Cuisse / mollet avant
        self.canvas.create_line(hip_x, hip_y, knee_front_x, knee_front_y, fill="#0f172a", width=13, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, knee_front_x, knee_front_y, fill="#2563eb", width=9, capstyle=tk.ROUND)
        self.canvas.create_line(knee_front_x, knee_front_y, foot_front_x, foot_front_y, fill="#0f172a", width=12, capstyle=tk.ROUND)
        self.canvas.create_line(knee_front_x, knee_front_y, foot_front_x, foot_front_y, fill="#2563eb", width=8, capstyle=tk.ROUND)
        
        # Baskets de sport cartoon rouges à semelles blanches
        for fx, fy, f_lift in [(foot_back_x, foot_back_y, leg_lift_b), (foot_front_x, foot_front_y, leg_lift_f)]:
            # Semelle blanche
            self.canvas.create_oval(fx - 14, fy + 2, fx + 14, fy + 9, fill="#f8fafc", outline="#0f172a", width=2)
            # Chaussure rouge profilée dans la direction facing
            self.canvas.create_polygon([
                fx - facing * 12, fy + 3,
                fx + facing * 16, fy + 3,
                fx + facing * 13, fy - 6,
                fx - facing * 8, fy - 9,
                fx - facing * 12, fy - 4
            ], fill="#ef4444", outline="#0f172a", width=2)
            
        # 4. Torse musclé d'athlète penché EN AVANT (effort de traction vers facing)
        lean_angle = facing * 32.0 # Incliné à 32° dans le sens du mouvement
        lean_rad = math.radians(lean_angle)
        
        # Torse / buste
        shoulder_x = hip_x + math.sin(lean_rad) * 42.0
        shoulder_y = hip_y - math.cos(lean_rad) * 42.0
        
        # Bobbing vertical naturel de la course
        bob = math.sin(self.phase * 3.2) * 3.5
        shoulder_y += bob
        
        # Débardeur orange musclé
        torso_cx = (hip_x + shoulder_x) / 2.0
        torso_cy = (hip_y + shoulder_y) / 2.0
        self.canvas.create_line(hip_x, hip_y, shoulder_x, shoulder_y, fill="#0f172a", width=26, capstyle=tk.ROUND)
        self.canvas.create_line(hip_x, hip_y, shoulder_x, shoulder_y, fill="#ea580c", width=20, capstyle=tk.ROUND)
        # Biais d'ombrage du torse
        self.canvas.create_line(hip_x + facing*2, hip_y - 2, shoulder_x + facing*2, shoulder_y - 2, fill="#f97316", width=8, capstyle=tk.ROUND)
        
        # 5. Bras musclés en pleine traction de la corde
        # La corde part des mains (situées près de la hanche / torse) et repart en arrière (-facing) vers la souris
        hands_x = hip_x - (facing * 12)
        hands_y = torso_cy + 4
        
        # Bras arrière
        self.canvas.create_line(shoulder_x - facing*5, shoulder_y + 4, hands_x - facing*6, hands_y - 4, fill="#0f172a", width=12, capstyle=tk.ROUND)
        self.canvas.create_line(shoulder_x - facing*5, shoulder_y + 4, hands_x - facing*6, hands_y - 4, fill="#fed7aa", width=8, capstyle=tk.ROUND)
        # Biceps saillant
        self.canvas.create_oval(shoulder_x - 8, shoulder_y - 2, shoulder_x + 8, shoulder_y + 14, fill="#fed7aa", outline="#c2410c", width=2)
        
        # Bras avant
        self.canvas.create_line(shoulder_x + facing*6, shoulder_y + 6, hands_x + facing*6, hands_y, fill="#0f172a", width=13, capstyle=tk.ROUND)
        self.canvas.create_line(shoulder_x + facing*6, shoulder_y + 6, hands_x + facing*6, hands_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
        
        # Gants de force marrons / blancs agrippant fermement la corde
        self.canvas.create_oval(hands_x - 10, hands_y - 8, hands_x + 10, hands_y + 8, fill="#92400e", outline="#0f172a", width=2)
        self.canvas.create_oval(hands_x - 4 + facing*6, hands_y - 6, hands_x + 12 + facing*6, hands_y + 6, fill="#b45309", outline="#0f172a", width=2)
        
        # 6. Tête expressive déterminée, tournée vers l'AVANT (vers facing)
        head_x = shoulder_x + (facing * 12)
        head_y = shoulder_y - 20
        
        # Visage en sueur, rouge d'effort
        self.canvas.create_oval(head_x - 19, head_y - 19, head_x + 19, head_y + 19, fill="#fed7aa", outline="#c2410c", width=3)
        # Joues cramoisies
        self.canvas.create_oval(head_x + facing*6 - 6, head_y + 3, head_x + facing*6 + 8, head_y + 11, fill="#fca5a5", outline="")
        
        # Yeux concentrés / plissés regardant droit devant dans le sens facing
        eye_x = head_x + (facing * 7)
        eye_y = head_y - 3
        self.canvas.create_oval(eye_x - 5, eye_y - 5, eye_x + 5, eye_y + 5, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_oval(eye_x + facing*2 - 2, eye_y - 2, eye_x + facing*2 + 2, eye_y + 2, fill="#0f172a", outline="")
        # Sourcil froncé conquérant
        self.canvas.create_line(eye_x - facing*8, eye_y - 8, eye_x + facing*6, eye_y - 5, fill="#7c2d12", width=4)
        
        # Bouche grimaçante avec dents serrées d'effort
        mouth_x = head_x + (facing * 9)
        mouth_y = head_y + 9
        self.canvas.create_rectangle(mouth_x - 8, mouth_y - 4, mouth_x + 8, mouth_y + 4, fill="#ffffff", outline="#0f172a", width=2)
        self.canvas.create_line(mouth_x - 4, mouth_y - 4, mouth_x - 4, mouth_y + 4, fill="#0f172a", width=1)
        self.canvas.create_line(mouth_x + 2, mouth_y - 4, mouth_x + 2, mouth_y + 4, fill="#0f172a", width=1)
        self.canvas.create_line(mouth_x - 8, mouth_y, mouth_x + 8, mouth_y, fill="#0f172a", width=1)
        
        # Bandeau de ninja rouge vif sur le front
        band_y = head_y - 10
        self.canvas.create_line(head_x - 20, band_y, head_x + 20, band_y, fill="#ef4444", width=7)
        # Rubans du bandeau flottant au vent EN ARRIÈRE (-facing)
        ribbon_wave = math.sin(self.phase * 4.5) * 8.0
        self.canvas.create_line(head_x - facing*18, band_y, head_x - facing*45, band_y - 8 + ribbon_wave, fill="#dc2626", width=4)
        self.canvas.create_line(head_x - facing*18, band_y, head_x - facing*40, band_y + 8 - ribbon_wave, fill="#b91c1c", width=4)
        
        # 7. Gouttes de sueur qui giclent en arrière (-facing)
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
        
        # 8. Corde nautique ultra-tendue reliant les mains à la souris (vers l'arrière -facing)
        rope_vib = math.sin(self.phase * 8.0) * 3.0
        # Corde tendue avec vibration de résonance
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
        
        # Curseur de souris simulé
        self.canvas.create_polygon([
            mx, my,
            mx, my + 24,
            mx + 6, my + 18,
            mx + 13, my + 28,
            mx + 17, my + 26,
            mx + 10, my + 16,
            mx + 18, my + 16
        ], fill="#ffffff", outline="#000000", width=2)
        
        # Effet de traction sur la souris (lignes de dérapage de la souris)
        self.canvas.create_line(mx - facing*10, my + 22, mx - facing*30, my + 22, fill="#f59e0b", width=3, dash=(3, 3))
        self.canvas.create_line(mx - facing*10, my + 28, mx - facing*25, my + 28, fill="#f59e0b", width=2, dash=(3, 3))
        
        # 9. Bulle de dialogue comique
        bubble_x = cx + facing * 20
        bubble_y = cy - 65
        self.canvas.create_text(bubble_x, bubble_y, text="AVANCE ! HO-ISSE ! 🏃‍♂️💨", font=("Impact", 13, "bold"), fill="#f97316")

if __name__ == "__main__":
    app = CartoonPullerTest()
    app.root.mainloop()

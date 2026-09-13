import tkinter as tk
import math
import random

class GiantMessageTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Titan Geant - Lancer de Message Legendaire")
        self.root.geometry("1400x850")
        self.root.configure(bg="#020617")
        
        self.sw = 1380
        self.sh = 820
        self.canvas = tk.Canvas(self.root, width=self.sw, height=self.sh, bg="#020617", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Dimensions du message géant (70% de l'écran)
        self.bw = int(self.sw * 0.70)
        self.bh = int(self.sh * 0.68)
        self.target_cx = self.sw // 2 - 40 # Légèrement décalé à gauche pour laisser voir le titan à droite
        self.target_cy = self.sh // 2 + 10
        
        self.anim_data = {
            "t": 0.0,
            "state": "EMERGE", # EMERGE -> WINDUP -> THROW -> REBOUND -> SETTLED -> EXIT
            "titan_emerge": 0.0, # 0.0 = complètement hors écran, 1.0 = à moitié sorti du bord
            "titan_windup": 0.0, # recul du titan pour armer
            "board_scale": 0.12,
            "board_x": float(self.sw + 100),
            "board_y": float(self.sh * 0.5),
            "board_rot": 35.0,
            "rebound_t": 0.0,
            "dust": [],
            "shockwaves": [],
            "sparks": [],
            "closing": False,
            "close_t": 0.0,
            "shake_x": 0.0,
            "shake_y": 0.0,
            "speech": "ATTENTION LES YEUX ! ⚡"
        }
        
        self.root.bind("<space>", lambda e: self.restart())
        self.root.bind("<Escape>", lambda e: self.close())
        
        self._tick()
        
    def restart(self):
        self.anim_data["t"] = 0.0
        self.anim_data["state"] = "EMERGE"
        self.anim_data["titan_emerge"] = 0.0
        self.anim_data["titan_windup"] = 0.0
        self.anim_data["board_scale"] = 0.12
        self.anim_data["board_x"] = float(self.sw + 100)
        self.anim_data["board_y"] = float(self.sh * 0.5)
        self.anim_data["board_rot"] = 35.0
        self.anim_data["rebound_t"] = 0.0
        self.anim_data["dust"].clear()
        self.anim_data["shockwaves"].clear()
        self.anim_data["sparks"].clear()
        self.anim_data["closing"] = False
        self.anim_data["close_t"] = 0.0
        
    def close(self):
        self.anim_data["closing"] = True
        self.anim_data["state"] = "EXIT"
        
    def _tick(self):
        self.anim_data["t"] += 0.035
        t = self.anim_data["t"]
        ad = self.anim_data
        
        # Effet de tremblement de caméra
        ad["shake_x"] *= 0.85
        ad["shake_y"] *= 0.85
        
        if ad["state"] == "EMERGE":
            # Le titan surgit depuis le bord droit (moitié de son corps sort du bezel)
            ad["titan_emerge"] += (1.0 - ad["titan_emerge"]) * 0.14
            ad["speech"] = "QUELQU'UN A UN MESSAGE ? 🌋"
            if ad["titan_emerge"] > 0.94:
                ad["titan_emerge"] = 1.0
                ad["state"] = "WINDUP"
                ad["t"] = 0.0
                
        elif ad["state"] == "WINDUP":
            # Le titan arme son bras colossal en arrière (hyper-anticipation)
            ad["titan_windup"] = min(1.0, ad["t"] / 0.50)
            ad["speech"] = "CHARGEMENT TITANESQUE... 💥"
            
            # Tremblement croissant
            ad["shake_x"] = random.uniform(-3, 3) * ad["titan_windup"]
            ad["shake_y"] = random.uniform(-3, 3) * ad["titan_windup"]
            
            # Étincelles d'énergie autour du poing
            hand_x = self.sw - 60 - int(ad["titan_windup"] * 90)
            hand_y = self.sh * 0.45 - int(ad["titan_windup"] * 40)
            ad["board_x"] = hand_x
            ad["board_y"] = hand_y
            ad["board_scale"] = 0.18 + ad["titan_windup"] * 0.06
            ad["board_rot"] = 35.0 + ad["titan_windup"] * 20.0
            
            if random.random() < 0.6:
                ad["sparks"].append({
                    "x": hand_x + random.uniform(-30, 30),
                    "y": hand_y + random.uniform(-30, 30),
                    "vx": random.uniform(-5, -1),
                    "vy": random.uniform(-3, 3),
                    "color": random.choice(["#facc15", "#ef4444", "#ffffff"]),
                    "r": random.uniform(3, 7),
                    "life": 1.0
                })
                
            if ad["t"] > 0.55:
                ad["state"] = "THROW"
                ad["t"] = 0.0
                ad["shake_x"] = random.uniform(-16, 16)
                ad["shake_y"] = random.uniform(-16, 16)
                # Onde de choc supersonique au départ
                ad["shockwaves"].append({"x": hand_x, "y": hand_y, "r": 20, "max_r": 180, "alpha": 1.0})
                
        elif ad["state"] == "THROW":
            # LANCER LÉGENDAIRE : LE MESSAGE S'ÉCRASE DANS LA FACE EN 3D !
            prog = min(1.0, ad["t"] / 0.28) # Lancer foudroyant en ~0.28s
            ease = 1.0 - math.pow(1.0 - prog, 3) # Decel explosive
            
            start_bx = self.sw - 150
            start_by = self.sh * 0.40
            ad["board_x"] = start_bx + (self.target_cx - start_bx) * ease
            ad["board_y"] = start_by + (self.target_cy - start_by) * ease
            ad["board_scale"] = 0.22 + (1.12 - 0.22) * ease
            ad["board_rot"] = 55.0 * (1.0 - ease)
            
            # Le titan projette son torse et son bras en avant lors de la détente
            ad["titan_windup"] = 1.0 - ease * 1.5
            ad["speech"] = "REÇOIS ÇA EN PLEINE FACE ! 🚀"
            
            if prog >= 1.0:
                ad["state"] = "REBOUND"
                ad["rebound_t"] = 0.0
                ad["shake_x"] = random.uniform(-20, 20)
                ad["shake_y"] = random.uniform(-20, 20)
                # Double onde de choc d'impact contre la vitre
                ad["shockwaves"].append({"x": self.target_cx, "y": self.target_cy, "r": 25, "max_r": 260, "alpha": 1.0})
                ad["shockwaves"].append({"x": self.target_cx, "y": self.target_cy, "r": 10, "max_r": 160, "alpha": 1.0})
                # Énormes nuages de poussière cartoon
                for _ in range(20):
                    ad["dust"].append({
                        "x": self.target_cx + random.uniform(-self.bw*0.48, self.bw*0.48),
                        "y": self.target_cy + self.bh*0.48 + random.uniform(-18, 18),
                        "r": random.uniform(22, 55),
                        "vx": random.uniform(-4, 4),
                        "vy": random.uniform(-3, -0.5),
                        "life": 1.0
                    })
                    
        elif ad["state"] == "REBOUND":
            # Rebond élastique 3D violent
            ad["rebound_t"] += 0.055
            rt = ad["rebound_t"]
            damping = math.exp(-rt * 3.5)
            rebound = 0.18 * damping * math.sin(rt * 18.0)
            ad["board_scale"] = 1.0 + rebound
            ad["board_rot"] = 5.0 * damping * math.cos(rt * 15.0)
            
            # Le titan reprend sa posture imposante de sentinelle
            ad["titan_windup"] += (0.0 - ad["titan_windup"]) * 0.12
            ad["speech"] = "DANS LE MILLE ! 🎯💥"
            
            if rt > 1.2:
                ad["state"] = "SETTLED"
                ad["board_scale"] = 1.0
                ad["board_rot"] = 0.0
                
        elif ad["state"] == "SETTLED":
            # Respiration vivante du titan et légers clignements d'yeux
            ad["speech"] = random.choice([
                "C'EST SIGNÉ AHMED ! 📬🔥",
                "LIS BIEN, C'EST IMPORTANT ! 🧐",
                "LE MAÎTRE A PARLÉ ! 👑",
                "ALORS, IMPRESSIONNÉ ? 😎"
            ]) if int(t * 10) % 80 == 0 else ad["speech"]
            
        elif ad["state"] == "EXIT":
            ad["close_t"] += 0.08
            ad["board_y"] -= math.pow(ad["close_t"] * 26.0, 2)
            # Le titan recule derrière le bord de l'écran
            ad["titan_emerge"] -= 0.06
            if ad["titan_emerge"] < 0.0:
                self.restart()
                
        # Particules
        new_dust = []
        for d in ad["dust"]:
            d["x"] += d.get("vx", 0)
            d["y"] += d.get("vy", 0)
            d["r"] += 1.4
            d["life"] -= 0.04
            if d["life"] > 0:
                new_dust.append(d)
        ad["dust"] = new_dust
        
        new_shk = []
        for s in ad["shockwaves"]:
            s["r"] += 12.0
            s["alpha"] -= 0.06
            if s["alpha"] > 0 and s["r"] < s["max_r"]:
                new_shk.append(s)
        ad["shockwaves"] = new_shk
        
        new_spk = []
        for sp in ad["sparks"]:
            sp["x"] += sp["vx"]
            sp["y"] += sp["vy"]
            sp["life"] -= 0.07
            if sp["life"] > 0:
                new_spk.append(sp)
        ad["sparks"] = new_spk
        
        self._render()
        self.root.after(16, self._tick)
        
    def _render(self):
        self.canvas.delete("all")
        ad = self.anim_data
        shx = ad["shake_x"]
        shy = ad["shake_y"]
        
        # 1. Poussière et ondes de choc en arrière-plan
        for d in ad["dust"]:
            dr = d["r"]
            self.canvas.create_oval(d["x"] - dr + shx, d["y"] - dr*0.5 + shy, d["x"] + dr + shx, d["y"] + dr*0.5 + shy, fill="#475569", outline="")
            
        for s in ad["shockwaves"]:
            sr = s["r"]
            self.canvas.create_oval(s["x"] - sr + shx, s["y"] - sr*0.6 + shy, s["x"] + sr + shx, s["y"] + sr*0.6 + shy, outline="#ffffff", width=max(2, int(4 * s["alpha"])))
            
        for sp in ad["sparks"]:
            r = sp["r"] * sp["life"]
            self.canvas.create_oval(sp["x"] - r + shx, sp["y"] - r + shy, sp["x"] + r + shx, sp["y"] + r + shy, fill=sp["color"], outline="")
            
        # 2. LE TITAN GÉANT QUI SORT À MOITIÉ DU BORD DE L'ÉCRAN
        self._draw_giant_titan(shx, shy)
        
        # 3. LE PANNEAU DE MESSAGE GÉANT (70% de l'écran avec rebond 3D)
        self._draw_giant_message_board(shx, shy)
        
    def _draw_giant_titan(self, shx, shy):
        ad = self.anim_data
        emerge = ad["titan_emerge"]
        if emerge <= 0.0:
            return
            
        windup = ad["titan_windup"]
        t = ad["t"]
        
        # Le titan est ancré sur le bord droit de l'écran (x = self.sw)
        # emerge fait entrer sa moitié gauche dans l'écran :
        # Quand emerge = 1.0, son centre est à ~ self.sw - 120 (la moitié de son énorme corps dépasse à l'intérieur)
        max_reach = 260
        base_x = self.sw - (emerge * max_reach) + (windup * 90) + shx
        base_y = self.sh * 0.50 + shy + math.sin(t * 2.5) * 6.0
        
        # === AURA ÉNERGÉTIQUE / OMBRE GÉANTE DU BORD ===
        self.canvas.create_oval(base_x - 140, base_y - 340, base_x + 360, base_y + 360, fill="#0f172a", outline="")
        
        # === TORSE COLOSSAL DU TITAN ===
        # Forme trapézoïdale puissante d'un colosse mythique (armure or / cuir titanesque)
        chest_w = 210
        chest_h = 240
        self.canvas.create_polygon([
            base_x - 40, base_y - chest_h//2,
            self.sw + 50, base_y - chest_h//2 - 40,
            self.sw + 50, base_y + chest_h//2 + 80,
            base_x - 10, base_y + chest_h//2 + 40,
            base_x - 60, base_y
        ], fill="#7c2d12", outline="#451a03", width=5)
        
        # Pectoraux saillants blindés
        pec_y = base_y - 20
        self.canvas.create_oval(base_x - 50, pec_y - 55, base_x + 60, pec_y + 40, fill="#c2410c", outline="#7c2d12", width=4)
        self.canvas.create_oval(base_x + 30, pec_y - 65, self.sw + 20, pec_y + 30, fill="#9a3412", outline="#7c2d12", width=4)
        
        # Harnais / plastron d'or avec emblème gravé
        self.canvas.create_line(base_x - 45, pec_y - 50, base_x + 20, pec_y + 35, fill="#f59e0b", width=12)
        self.canvas.create_oval(base_x - 10, pec_y - 20, base_x + 25, pec_y + 15, fill="#fbbf24", outline="#b45309", width=3)
        self.canvas.create_text(base_x + 8, pec_y - 2, text="⚡", font=("Impact", 18), fill="#78350f")
        
        # === ÉPAULE ET BRAS COLOSSAL QUI SORT DU BORD ===
        # L'épaule gigantesque
        shoulder_x = base_x - 30
        shoulder_y = base_y - 90
        self.canvas.create_oval(shoulder_x - 65, shoulder_y - 65, shoulder_x + 65, shoulder_y + 65, fill="#ea580c", outline="#7c2d12", width=5)
        # Épaulière d'acier doré à pointes cartoon
        self.canvas.create_polygon([
            shoulder_x - 60, shoulder_y - 10,
            shoulder_x - 80, shoulder_y - 60,
            shoulder_x, shoulder_y - 85,
            shoulder_x + 50, shoulder_y - 45,
            shoulder_x + 30, shoulder_y + 10
        ], fill="#f59e0b", outline="#78350f", width=4)
        
        # Bras / Biceps phénoménal
        if ad["state"] in ("EMERGE", "WINDUP"):
            # Bras replié vers l'arrière, armant le lancer
            arm_reach_x = shoulder_x - 60 - int(windup * 60)
            arm_reach_y = shoulder_y + 90 - int(windup * 30)
            self.canvas.create_line(shoulder_x - 15, shoulder_y, arm_reach_x, arm_reach_y, fill="#ea580c", width=44, capstyle=tk.ROUND)
            self.canvas.create_line(shoulder_x - 15, shoulder_y, arm_reach_x, arm_reach_y, fill="#fed7aa", width=32, capstyle=tk.ROUND)
            # Veines d'effort qui gonflent
            if windup > 0.3:
                self.canvas.create_line(shoulder_x - 20, shoulder_y + 20, arm_reach_x + 10, arm_reach_y - 10, fill="#38bdf8", width=3)
            # Énorme poing / brassard de force
            self.canvas.create_oval(arm_reach_x - 40, arm_reach_y - 35, arm_reach_x + 35, arm_reach_y + 40, fill="#b45309", outline="#451a03", width=4)
            self.canvas.create_oval(arm_reach_x - 30, arm_reach_y - 25, arm_reach_x + 25, arm_reach_y + 30, fill="#fed7aa", outline="#c2410c", width=3)
        elif ad["state"] == "THROW":
            # Bras tendu explosivement vers l'avant (vers le centre de l'écran)
            thrust_x = shoulder_x - 180
            thrust_y = shoulder_y + 70
            self.canvas.create_line(shoulder_x, shoulder_y, thrust_x, thrust_y, fill="#ea580c", width=48, capstyle=tk.ROUND)
            self.canvas.create_line(shoulder_x, shoulder_y, thrust_x, thrust_y, fill="#fed7aa", width=34, capstyle=tk.ROUND)
            # Paume géante ouverte qui vient de propulser le panneau
            self.canvas.create_oval(thrust_x - 45, thrust_y - 40, thrust_x + 40, thrust_y + 45, fill="#fed7aa", outline="#c2410c", width=4)
            # Lignes de vitesse du fouetté de bras
            for l in range(4):
                self.canvas.create_line(thrust_x + 20, thrust_y - 30 + l*20, thrust_x - 90, thrust_y - 30 + l*20, fill="#facc15", width=3, dash=(6, 3))
        else: # REBOUND, SETTLED
            # Posture imposante : main colossale posée sur le bord du cadre de l'écran ou pointant fièrement
            hand_x = base_x - 110
            hand_y = base_y + 40
            self.canvas.create_line(shoulder_x, shoulder_y, hand_x, hand_y, fill="#ea580c", width=42, capstyle=tk.ROUND)
            self.canvas.create_line(shoulder_x, shoulder_y, hand_x, hand_y, fill="#fed7aa", width=30, capstyle=tk.ROUND)
            # Brassard d'or clouté
            self.canvas.create_rectangle(hand_x - 20, hand_y - 25, hand_x + 15, hand_y + 25, fill="#f59e0b", outline="#78350f", width=3)
            # Main géante qui pointe fièrement vers le message
            self.canvas.create_oval(hand_x - 45, hand_y - 30, hand_x + 10, hand_y + 25, fill="#fed7aa", outline="#c2410c", width=3)
            # Index colossal pointé vers le centre
            self.canvas.create_line(hand_x - 25, hand_y - 10, hand_x - 70, hand_y - 10, fill="#fed7aa", width=16, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x - 25, hand_y - 10, hand_x - 70, hand_y - 10, fill="#c2410c", width=3, capstyle=tk.ROUND)
            
        # === TÊTE COLOSSALE DU TITAN ===
        head_x = base_x - 15
        head_y = shoulder_y - 80
        head_r = 75
        
        # Mâchoire carrée surpuissante
        self.canvas.create_polygon([
            head_x - head_r*0.75, head_y - head_r*0.4,
            head_x + head_r*0.8, head_y - head_r*0.5,
            head_x + head_r*0.9, head_y + head_r*0.5,
            head_x + head_r*0.2, head_y + head_r*1.1,
            head_x - head_r*0.6, head_y + head_r*1.0,
            head_x - head_r*0.9, head_y + head_r*0.3
        ], fill="#fed7aa", outline="#c2410c", width=4)
        
        # Chevelure / crête de feu ou de gladiateur
        crest_pts = [
            (head_x - 70, head_y - 40),
            (head_x - 85, head_y - 95),
            (head_x - 45, head_y - 125),
            (head_x, head_y - 145),
            (head_x + 50, head_y - 130),
            (head_x + 90, head_y - 85),
            (head_x + 70, head_y - 30)
        ]
        self.canvas.create_polygon(crest_pts, fill="#dc2626", outline="#7f1d1d", width=4)
        self.canvas.create_line(head_x - 30, head_y - 120, head_x, head_y - 70, fill="#facc15", width=4)
        
        # Yeux ardents géants (regard braqué sur l'utilisateur !)
        eye_y = head_y - 8
        # Oeil gauche
        self.canvas.create_oval(head_x - 46, eye_y - 16, head_x - 14, eye_y + 16, fill="#fef08a", outline="#0f172a", width=3)
        self.canvas.create_oval(head_x - 36, eye_y - 10, head_x - 20, eye_y + 10, fill="#0f172a", outline="")
        self.canvas.create_oval(head_x - 33, eye_y - 7, head_x - 27, eye_y - 1, fill="#ffffff", outline="") # éclat
        # Oeil droit
        self.canvas.create_oval(head_x + 6, eye_y - 16, head_x + 38, eye_y + 16, fill="#fef08a", outline="#0f172a", width=3)
        self.canvas.create_oval(head_x + 16, eye_y - 10, head_x + 32, eye_y + 10, fill="#0f172a", outline="")
        self.canvas.create_oval(head_x + 19, eye_y - 7, head_x + 25, eye_y - 1, fill="#ffffff", outline="")
        
        # Gros sourcils épais déterminés
        self.canvas.create_line(head_x - 52, eye_y - 24, head_x - 10, eye_y - 16, fill="#7f1d1d", width=7)
        self.canvas.create_line(head_x + 2, eye_y - 16, head_x + 44, eye_y - 24, fill="#7f1d1d", width=7)
        
        # Nez fort de colosse
        self.canvas.create_polygon([
            head_x - 4, eye_y - 6,
            head_x - 14, eye_y + 24,
            head_x + 6, eye_y + 24
        ], fill="#fba478", outline="#c2410c", width=2)
        
        # Bouche géante grimaçante / sourire confiant triomphal
        mouth_y = head_y + 44
        self.canvas.create_arc(head_x - 42, mouth_y - 18, head_x + 32, mouth_y + 32, start=190, extent=160, fill="#450a0a", outline="#0f172a", width=3)
        # Dents blanches impeccables
        self.canvas.create_rectangle(head_x - 34, mouth_y - 2, head_x + 24, mouth_y + 12, fill="#ffffff", outline="#0f172a", width=2)
        for dx in range(-24, 20, 10):
            self.canvas.create_line(head_x + dx, mouth_y - 2, head_x + dx, mouth_y + 12, fill="#0f172a", width=1)
            
        # === BULLE DE DIALOGUE GÉANTE DU TITAN ===
        bubble_x = head_x - 140
        bubble_y = head_y - 100
        bw = 280
        bh = 65
        self.canvas.create_rectangle(bubble_x - bw//2 + 5, bubble_y - bh//2 + 5, bubble_x + bw//2 + 5, bubble_y + bh//2 + 5, fill="#0f172a", outline="")
        self.canvas.create_rectangle(bubble_x - bw//2, bubble_y - bh//2, bubble_x + bw//2, bubble_y + bh//2, fill="#fef08a", outline="#ca8a04", width=3)
        # Pointe de la bulle vers le titan
        self.canvas.create_polygon([
            bubble_x + bw//2 - 20, bubble_y + 10,
            bubble_x + bw//2 + 25, bubble_y + 35,
            bubble_x + bw//2 - 10, bubble_y + bh//2
        ], fill="#fef08a", outline="#ca8a04", width=2)
        self.canvas.create_text(bubble_x, bubble_y, text=ad["speech"], font=("Impact", 13, "bold"), fill="#78350f")

    def _draw_giant_message_board(self, shx, shy):
        ad = self.anim_data
        scale = ad["board_scale"]
        if scale <= 0.05:
            return
            
        cur_bw = int(self.bw * scale)
        cur_bh = int(self.bh * scale)
        cx = int(ad["board_x"]) + shx
        cy = int(ad["board_y"]) + shy
        
        bx1 = cx - cur_bw // 2
        by1 = cy - cur_bh // 2
        bx2 = cx + cur_bw // 2
        by2 = cy + cur_bh // 2
        
        # Ombre portée 3D du panneau géant
        self.canvas.create_rectangle(bx1 + 18, by1 + 18, bx2 + 18, by2 + 18, fill="#020617", outline="")
        
        # Cadre en bois rustique caramel / chêne chaud (Zéro néon !)
        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill="#78350f", outline="#451a03", width=max(4, int(8 * scale)))
        self.canvas.create_rectangle(bx1 + 14, by1 + 14, bx2 - 14, by2 - 14, fill="#92400e", outline="#78350f", width=max(2, int(4 * scale)))
        
        # Clous en laiton aux 4 coins
        nail_r = max(4, int(11 * scale))
        for (nx, ny) in [(bx1 + 24, by1 + 24), (bx2 - 24, by1 + 24), (bx1 + 24, by2 - 24), (bx2 - 24, by2 - 24)]:
            self.canvas.create_oval(nx - nail_r, ny - nail_r, nx + nail_r, ny + nail_r, fill="#f59e0b", outline="#78350f", width=2)
            
        # Parchemin intérieur crème / ivoire chaleureux
        self.canvas.create_rectangle(bx1 + 30, by1 + 30, bx2 - 30, by2 - 30, fill="#fef3c7", outline="#fde68a", width=3)
        
        # Ruban rouge supérieur ÉNORME
        rub_y = by1 + int(60 * scale)
        rub_h = int(32 * scale)
        rub_indent = int(65 * scale)
        self.canvas.create_polygon([
            (bx1 + rub_indent, rub_y - rub_h), (bx2 - rub_indent, rub_y - rub_h),
            (bx2 - rub_indent + 15, rub_y), (bx2 - rub_indent, rub_y + rub_h),
            (bx1 + rub_indent, rub_y + rub_h), (bx1 + rub_indent - 15, rub_y)
        ], fill="#dc2626", outline="#991b1b", width=3)
        
        header_font_size = max(12, int(26 * scale))
        self.canvas.create_text(cx, rub_y, text="📬 MESSAGE DE AHMED 📬", font=("Impact", header_font_size, "bold"), fill="#ffffff")
        
        # Message de test
        display_msg = "« Regarde cette animation légendaire ! Le Titan colossal balance le message en plein sur l'écran ! »"
        actual_font_sz = max(11, int(30 * scale))
        
        # Ombre douce du texte
        self.canvas.create_text(
            cx + 2, cy + int(10 * scale) + 2, text=display_msg,
            font=("Impact", actual_font_sz), fill="#94a3b8",
            width=int(cur_bw * 0.84), justify="center"
        )
        # Texte net
        self.canvas.create_text(
            cx, cy + int(10 * scale), text=display_msg,
            font=("Impact", actual_font_sz), fill="#0f172a",
            width=int(cur_bw * 0.84), justify="center"
        )
        
        # Sceau de cire rouge géant
        seal_x = bx1 + int(90 * scale)
        seal_y = by2 - int(75 * scale)
        seal_r = int(34 * scale)
        if seal_r > 8:
            self.canvas.create_oval(seal_x - seal_r, seal_y - seal_r, seal_x + seal_r, seal_y + seal_r, fill="#b91c1c", outline="#7f1d1d", width=3)
            self.canvas.create_text(seal_x, seal_y, text="POSTE\nOFFICIELLE", font=("Impact", max(6, int(9 * scale)), "bold"), fill="#fef08a", justify="center")
            
        # Grand Bouton 3D vert émeraude
        btn_w = int(320 * scale)
        btn_h = int(60 * scale)
        btn_x1 = cx - btn_w // 2 + int(40 * scale)
        btn_y1 = by2 - int(95 * scale)
        btn_x2 = btn_x1 + btn_w
        btn_y2 = btn_y1 + btn_h
        
        if btn_w > 40:
            self.canvas.create_rectangle(btn_x1 + 4, btn_y1 + 4, btn_x2 + 4, btn_y2 + 4, fill="#0f172a", outline="")
            self.canvas.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#16a34a", outline="#14532d", width=3)
            self.canvas.create_line(btn_x1 + 8, btn_y1 + 5, btn_x2 - 8, btn_y1 + 5, fill="#86efac", width=3)
            btn_txt_sz = max(10, int(18 * scale))
            self.canvas.create_text(btn_x1 + btn_w//2, btn_y1 + btn_h//2, text="J'AI COMPRIS ! 👍", font=("Impact", btn_txt_sz, "bold"), fill="#ffffff")

if __name__ == "__main__":
    app = GiantMessageTest()
    app.root.mainloop()

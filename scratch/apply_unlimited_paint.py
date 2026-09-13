import sys

with open("ghost_script.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Suppression du cap de 16 pinceaux
t1 = """                        if len(self.stuck_brushes) > 16:
                            self.stuck_brushes.pop(0)"""

r1 = """                        # Peinture illimitée pour le peintre fou : aucune limite de pinceaux sur l'écran !
                        if len(self.stuck_brushes) > 400:
                            self.stuck_brushes.pop(0)"""

if t1 in content:
    content = content.replace(t1, r1, 1)
    print("1. Cap de 16 pinceaux remplacé par mode illimité (>400) avec succès!")
else:
    print("WARNING: t1 non trouvé!")

# 2. Suppression de l'expiration des taches (peinture permanente sur l'écran)
t2 = """                new_stuck = []
                for sb in self.stuck_brushes:
                    sb["life"] -= 0.015
                    sb["vib_t"] += 0.14
                    for dr in sb["drips"]:
                        if dr["len"] < dr["max_len"]:
                            dr["len"] += dr["speed"]
                    if sb["life"] > 0:
                        new_stuck.append(sb)
                self.stuck_brushes = new_stuck"""

r2 = """                # Peinture permanente : les taches et coulures restent collées à l'écran sans limite !
                for sb in self.stuck_brushes:
                    sb["vib_t"] += 0.14
                    for dr in sb["drips"]:
                        if dr["len"] < dr["max_len"]:
                            dr["len"] += dr["speed"]"""

if t2 in content:
    content = content.replace(t2, r2, 1)
    print("2. Expiration des taches supprimée : peinture permanente avec succès!")
else:
    print("WARNING: t2 non trouvé!")

# 3. Punchlines du peintre fou illimité et cadence de tir
t3 = """                        if self.state_timer == 1:
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
                            
                        # Émulsion de peinture rapide sur la palette
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
                            
                        # Trempage éclair de ~0.35s
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
                            
                        # Moulinet rapide de ~0.6s
                        if self.state_timer > 32:
                            self.anim_state = "THROW"
                            self.state_timer = 0
                            self._trigger_throw()"""

r3 = """                        if self.state_timer == 1:
                            self.color_index += 1
                            self.current_color = self.palette_colors[self.color_index % len(self.palette_colors)]
                            self.speech_text = random.choice([
                                "ET UN AUTRE ! 🎨",
                                "PEINTURE ILLIMITÉE ! 🔥",
                                "PRENDS ÇA ! 💥",
                                "DE LA COULEUR PARTOUT ! 🌈",
                                "DANS LE MILLE ! 🎯",
                                "CHEF-D'ŒUVRE SUIVANT ! ✨",
                                "C'EST L'APOCALYPSE DE L'ART ! ⚡",
                                "JUSQU'À COUVRIR TOUT L'ÉCRAN ! 🖌️"
                            ])
                            self.speech_timer = 28
                            
                        # Émulsion de peinture rapide sur la palette
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
                            
                        # Trempage éclair rapide
                        reload_max = 14 if self.throw_count > 6 else 18
                        if self.state_timer > reload_max:
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
                            
                        # Moulinet énergique
                        windup_max = 24 if self.throw_count > 6 else 32
                        if self.state_timer > windup_max:
                            self.anim_state = "THROW"
                            self.state_timer = 0
                            self._trigger_throw()"""

if t3 in content:
    content = content.replace(t3, r3, 1)
    print("3. Dialogues et tempo du peintre fou mis à jour avec succès!")
else:
    print("WARNING: t3 non trouvé!")

with open("ghost_script.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fichier ghost_script.py mis à jour avec succès!")

import re

# Lecture du fichier original
with open("ghost_script.py", "r", encoding="utf-8") as f:
    content = f.read()

# Backup avant modification
with open("ghost_script.py.bak_shadows", "w", encoding="utf-8") as f:
    f.write(content)

changes_count = 0

# 1. Suppression de l'aura / ombre sombre du Titan
t1 = """                # Aura / ombre sombre sur le bord
                canvas.create_oval(base_x - 140, base_y - 340, base_x + 360, base_y + 360, fill="#0f172a", outline="")"""
if t1 in content:
    content = content.replace(t1, "                # (Ombre supprimée selon instructions)")
    changes_count += 1
    print("1. Aura titan supprimée avec succès")
else:
    print("WARNING: Aura titan non trouvée!")

# 2. Suppression de l'ombre de la bulle de dialogue du Titan
t2 = """                canvas.create_rectangle(bubble_x - bbw//2 + 5, bubble_y - bbh//2 + 5, bubble_x + bbw//2 + 5, bubble_y + bbh//2 + 5, fill="#0f172a", outline="")
                canvas.create_rectangle(bubble_x - bbw//2, bubble_y - bbh//2, bubble_x + bbw//2, bubble_y + bbh//2, fill="#fef08a", outline="#ca8a04", width=3)"""
r2 = """                canvas.create_rectangle(bubble_x - bbw//2, bubble_y - bbh//2, bubble_x + bbw//2, bubble_y + bbh//2, fill="#fef08a", outline="#ca8a04", width=3)"""
if t2 in content:
    content = content.replace(t2, r2)
    changes_count += 1
    print("2. Ombre bulle dialogue titan supprimée avec succès")
else:
    print("WARNING: Ombre bulle dialogue titan non trouvée!")

# 3. Suppression de l'ombre portée du panneau géant
t3 = """                # Ombre portée 3D du panneau géant
                canvas.create_rectangle(bx1 + 18, by1 + 18, bx2 + 18, by2 + 18, fill="#020617", outline="")"""
if t3 in content:
    content = content.replace(t3, "                # (Ombre panneau supprimée)")
    changes_count += 1
    print("3. Ombre panneau géant supprimée avec succès")
else:
    print("WARNING: Ombre panneau géant non trouvée!")

# 4. Suppression de l'ombre portée du texte du message
t4 = """                # Ombre douce du texte pour le relief 3D
                canvas.create_text(
                    cx + 2, cy + int(10 * scale) + 2, text=display_msg,
                    font=("Impact", actual_font_sz), fill="#94a3b8",
                    width=int(cur_bw * 0.84), justify="center"
                )
                canvas.create_text(
                    cx, cy + int(10 * scale), text=display_msg,
                    font=("Impact", actual_font_sz), fill="#0f172a",
                    width=int(cur_bw * 0.84), justify="center"
                )"""
r4 = """                canvas.create_text(
                    cx, cy + int(10 * scale), text=display_msg,
                    font=("Impact", actual_font_sz), fill="#0f172a",
                    width=int(cur_bw * 0.84), justify="center"
                )"""
if t4 in content:
    content = content.replace(t4, r4)
    changes_count += 1
    print("4. Ombre texte message supprimée avec succès")
else:
    print("WARNING: Ombre texte message non trouvée!")

# 5. Suppression de l'ombre du bouton du panneau géant
t5 = """                if btn_w > 40:
                    canvas.create_rectangle(btn_x1 + 4, btn_y1 + 4, btn_x2 + 4, btn_y2 + 4, fill="#0f172a", outline="")
                    btn_tag = canvas.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#16a34a", outline="#14532d", width=3)"""
r5 = """                if btn_w > 40:
                    btn_tag = canvas.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#16a34a", outline="#14532d", width=3)"""
if t5 in content:
    content = content.replace(t5, r5)
    changes_count += 1
    print("5. Ombre bouton panneau supprimée avec succès")
else:
    print("WARNING: Ombre bouton panneau non trouvée!")

# 6. Suppression de l'ombre sous le coureur dans CartoonPullerOverlay
t6 = """        # 3. Ombre au sol sous le coureur
        shadow_rx = 34
        shadow_ry = 9
        self.canvas.create_oval(cx - shadow_rx, cy + 62 - shadow_ry, cx + shadow_rx, cy + 62 + shadow_ry, fill="#020617", outline="")
        
        # 4. Cycle de course effréné des jambes cartoon"""
r6 = """        # (Ombre au sol sous le coureur supprimée)
        
        # 3. Cycle de course effréné des jambes cartoon"""
if t6 in content:
    content = content.replace(t6, r6)
    changes_count += 1
    print("6. Ombre coureur puller supprimée avec succès")
else:
    print("WARNING: Ombre coureur puller non trouvée!")

# 7. Suppression de l'ombre de la peinture dans CartoonPainterOverlay
t7 = """            self.canvas.create_oval(sx - sr - 5, sy - sr - 5, sx + sr + 5, sy + sr + 5, fill="#0f172a", outline="")
            
            pts = []"""
r7 = """            # (Ombre de la tache de peinture supprimée selon instructions)
            pts = []"""
if t7 in content:
    content = content.replace(t7, r7)
    changes_count += 1
    print("7. Ombre tache de peinture supprimée avec succès")
else:
    print("WARNING: Ombre tache de peinture non trouvée!")

# 8. Perfectionnement de _drunk_mouse_loop avec clamping et vacillements réalistes
t8 = """def _drunk_mouse_loop():
    \"\"\"
    Souris ivre avec animation cartoon :
    1. Boit de l'alcool (bouteille qui s'incline, GLOU GLOU, gorgées).
    2. Commence à vaciller avec joues roses, étoiles de vertige en orbite et bulles de hoquet (HIC ! 💫).
    \"\"\"
    global drunk_mouse_active, drunk_state
    t = 0.0
    start_time = time.time()
    ensure_prank_overlays_started()
    drunk_state["intro_reset"] = True
    
    while drunk_mouse_active:
        try:
            x, y = _get_current_mouse_position()
            elapsed = time.time() - start_time
            if elapsed < 2.6:
                # Phase 1 : dégustation de la bouteille d'alcool, tremblements sur place
                sip_x = int(math.sin(t * 8.0) * 2.0)
                sip_y = int(math.cos(t * 8.0) * 2.0)
                target_x = x + sip_x
                target_y = y + sip_y
            else:
                # Phase 2 : ivresse totale et vacillements instables
                stagger_x = math.sin(t * 1.6) * 14.0 + math.cos(t * 0.7) * 7.0
                stagger_y = math.cos(t * 1.4) * 12.0 + math.sin(t * 0.9) * 6.0
                if random.random() < 0.06:
                    stagger_x += random.choice([-22.0, 22.0])
                target_x = int(x + stagger_x)
                target_y = int(y + stagger_y)
                
            ctypes.windll.user32.SetCursorPos(target_x, target_y)
            drunk_state["active"] = True
            drunk_state["mx"] = target_x
            drunk_state["my"] = target_y
                
            t += 0.22
        except Exception:
            pass
        time.sleep(0.03)
        
    drunk_state["active"] = False"""

r8 = """def _drunk_mouse_loop():
    \"\"\"
    Souris ivre avec animation cartoon :
    1. Boit de l'alcool dans une bouteille super réaliste (goulot, liquide ambré, étiquette, reflets).
    2. Commence à vaciller avec joues rouges d'ébriété, perte d'équilibre et étoiles/spirales 3D en orbite autour de sa tête (*HIC !*).
    \"\"\"
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
        
    drunk_state["active"] = False"""

if t8 in content:
    content = content.replace(t8, r8)
    changes_count += 1
    print("8. Boucle _drunk_mouse_loop optimisée avec succès")
else:
    print("WARNING: _drunk_mouse_loop non trouvée!")

print(f"\nTotal modifications réussies : {changes_count}/8")

if changes_count == 8:
    with open("ghost_script.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fichier ghost_script.py mis à jour avec succès!")
else:
    print("ERREUR: Certaines modifications n'ont pas été appliquées, le fichier n'a pas été sauvegardé.")

# -*- coding: utf-8 -*-
"""
Mise à jour de show_troll_window_on_client dans ghost_script.py :
- Plein écran transparent (sw x sh).
- Le livreur surgit du bord de l'écran (off-screen à droite).
- Il arme son lancer et balance violemment le message à la face de l'utilisateur !
- Le message grandit en 3D et s'écrase sur la vitre avec un rebond élastique (rebound).
- Le panneau prend 70% de l'écran.
- Le message est écrit en ÉNORME.
"""

import sys
import os
import shutil
import py_compile

SCRIPT_PATH = "ghost_script.py"

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    content = f.read()

target_start = "def show_troll_window_on_client(text):"
idx_start = content.find(target_start)
if idx_start == -1:
    print("ERREUR: Impossible de trouver target_start")
    sys.exit(1)

target_end = "# ==============================================================================\n# AUDIO LOOPBACK AND CAPTURE SUPPORT"
idx_end = content.find(target_end, idx_start)
if idx_end == -1:
    print("ERREUR: Impossible de trouver target_end")
    sys.exit(1)

new_func = '''def show_troll_window_on_client(text):
    """
    Grand Personnage Cartoon Livreur Express :
    - Surgit à toute vitesse depuis le bord de l'écran (off-screen).
    - Mouline le bras et balance littéralement le message à la figure de l'utilisateur !
    - Le message grossit en perspective 3D et claque contre la vitre avec un puissant rebond élastique.
    - Le panneau prend 70% de l'écran et le message est écrit en ÉNORME !
    """
    def _create_gui():
        global active_troll_wins, active_troll_hwnds, root
        try:
            win = tk.Toplevel(root) if root else tk.Tk()
            active_troll_wins.add(win)
            win.title("MESSAGE DE AHMED 📬")
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.attributes("-transparentcolor", "#010101")
            win.configure(bg="#010101")
            
            try:
                sw = win.winfo_screenwidth()
                sh = win.winfo_screenheight()
            except Exception:
                sw, sh = 1920, 1080
                
            win.geometry(f"{sw}x{sh}+0+0")
            win.resizable(False, False)
            win.lift()
            
            win.update()
            thwnd = int(win.wm_frame(), 16)
            active_troll_hwnds.add(thwnd)
            
            canvas = tk.Canvas(win, width=sw, height=sh, bg="#010101", highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            
            # Dimensions cibles du panneau : 70% de l'écran !
            bw = int(sw * 0.72)
            bh = int(sh * 0.70)
            target_cx = sw // 2
            target_cy = sh // 2 + 25
            
            anim_data = {
                "t": 0.0,
                "state": "ENTER",  # ENTER, WINDUP, THROW, REBOUND, SETTLED, EXIT
                "char_x": float(sw + 260),  # Démarre complètement hors écran à droite
                "char_y": float(sh * 0.45),
                "board_scale": 0.12,
                "board_x": float(sw + 100),
                "board_y": float(sh * 0.45),
                "board_rot": 45.0,
                "rebound_t": 0.0,
                "dust": [],
                "closing": False,
                "close_t": 0.0
            }
            
            def _cleanup_and_destroy():
                try:
                    active_troll_hwnds.discard(thwnd)
                except Exception:
                    pass
                try:
                    active_troll_wins.discard(win)
                except Exception:
                    pass
                try:
                    win.destroy()
                except Exception:
                    pass

            def _start_close():
                if anim_data["closing"]:
                    return
                anim_data["closing"] = True
                anim_data["state"] = "EXIT"

            win.protocol("WM_DELETE_WINDOW", _cleanup_and_destroy)
            win.bind("<Escape>", lambda e: _start_close())
            win.bind("<Return>", lambda e: _start_close())
            win.bind("<space>", lambda e: _start_close())
            
            def _tick_anim():
                try:
                    if not win.winfo_exists():
                        return
                        
                    anim_data["t"] += 0.035
                    t = anim_data["t"]
                    
                    if anim_data["state"] == "ENTER":
                        # Le personnage déboule depuis le bord droit (glissade cartoon)
                        anim_data["char_x"] += ((sw - 200) - anim_data["char_x"]) * 0.22
                        anim_data["board_x"] = anim_data["char_x"] - 60
                        anim_data["board_y"] = anim_data["char_y"] - 10
                        if abs(anim_data["char_x"] - (sw - 200)) < 15:
                            anim_data["state"] = "WINDUP"
                            
                    elif anim_data["state"] == "WINDUP":
                        # Mouline le bras en arrière avec grande anticipation
                        anim_data["char_x"] += math.sin(t * 15.0) * 4.0
                        if t > 0.42:
                            anim_data["state"] = "THROW"
                            
                    elif anim_data["state"] == "THROW":
                        # BALANCE LE MESSAGE EN PLEIN DANS LA FACE !
                        prog = min(1.0, (t - 0.42) / 0.28)
                        ease = 1.0 - math.pow(1.0 - prog, 3)
                        
                        start_bx = sw - 200
                        start_by = sh * 0.42
                        anim_data["board_x"] = start_bx + (target_cx - start_bx) * ease
                        anim_data["board_y"] = start_by + (target_cy - start_by) * ease
                        anim_data["board_scale"] = 0.15 + (1.08 - 0.15) * ease
                        anim_data["board_rot"] = 45.0 * (1.0 - ease)
                        
                        # Le personnage saute vers le haut du panneau
                        anim_data["char_x"] += (target_cx - anim_data["char_x"]) * 0.20
                        anim_data["char_y"] += ((target_cy - bh//2 - 25) - anim_data["char_y"]) * 0.20
                        
                        if prog >= 1.0:
                            anim_data["state"] = "REBOUND"
                            anim_data["rebound_t"] = 0.0
                            # Nuages de poussière d'impact
                            for _ in range(14):
                                anim_data["dust"].append({
                                    "x": target_cx + random.uniform(-bw*0.45, bw*0.45),
                                    "y": target_cy + bh*0.48 + random.uniform(-15, 15),
                                    "r": random.uniform(18, 42),
                                    "life": 1.0
                                })
                            # Secousse légère de la fenêtre active pour l'impact
                            try:
                                fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
                                if fg_hwnd:
                                    rect = wintypes.RECT()
                                    ctypes.windll.user32.GetWindowRect(fg_hwnd, ctypes.byref(rect))
                                    threading.Thread(target=_shake_window_briefly, args=(fg_hwnd, rect.left, rect.top), daemon=True).start()
                            except Exception:
                                pass
                                
                    elif anim_data["state"] == "REBOUND":
                        # Rebond élastique 3D avec amortissement harmonique
                        anim_data["rebound_t"] += 0.06
                        rt = anim_data["rebound_t"]
                        damping = math.exp(-rt * 3.6)
                        rebound = 0.16 * damping * math.sin(rt * 20.0)
                        anim_data["board_scale"] = 1.0 + rebound
                        anim_data["board_rot"] = 4.0 * damping * math.cos(rt * 16.0)
                        
                        anim_data["char_x"] = target_cx
                        anim_data["char_y"] = target_cy - bh//2 - 25
                        
                        if rt > 1.2:
                            anim_data["state"] = "SETTLED"
                            anim_data["board_scale"] = 1.0
                            anim_data["board_rot"] = 0.0
                            
                    elif anim_data["state"] == "SETTLED":
                        anim_data["char_y"] = (target_cy - bh//2 - 25) + math.sin(t * 3.0) * 3.0
                        
                    elif anim_data["state"] == "EXIT":
                        # Remontée ultra-rapide vers le haut
                        anim_data["close_t"] += 0.08
                        anim_data["board_y"] -= math.pow(anim_data["close_t"] * 24.0, 2)
                        anim_data["char_y"] -= math.pow(anim_data["close_t"] * 24.0, 2)
                        if anim_data["board_y"] < -bh:
                            _cleanup_and_destroy()
                            return
                            
                    new_dust = []
                    for d in anim_data["dust"]:
                        d["r"] += 1.6
                        d["life"] -= 0.05
                        if d["life"] > 0:
                            new_dust.append(d)
                    anim_data["dust"] = new_dust
                    
                    _render()
                    win.after(16, _tick_anim)
                except Exception:
                    _cleanup_and_destroy()

            def _render():
                canvas.delete("all")
                
                # 1. Poussière cartoon d'impact
                for d in anim_data["dust"]:
                    dr = d["r"]
                    canvas.create_oval(d["x"] - dr, d["y"] - dr*0.5, d["x"] + dr, d["y"] + dr*0.5, fill="#cbd5e1", outline="")
                    
                # 2. Panneau Géant (70% de l'écran avec rebond & échelle 3D)
                scale = anim_data["board_scale"]
                cur_bw = int(bw * scale)
                cur_bh = int(bh * scale)
                cx = int(anim_data["board_x"])
                cy = int(anim_data["board_y"])
                
                bx1 = cx - cur_bw // 2
                by1 = cy - cur_bh // 2
                bx2 = cx + cur_bw // 2
                by2 = cy + cur_bh // 2
                
                # Ombre portée 3D du panneau géant
                canvas.create_rectangle(bx1 + 16, by1 + 16, bx2 + 16, by2 + 16, fill="#0f172a", outline="")
                
                # Cadre en bois rustique caramel / chêne chaud (Zéro néon !)
                canvas.create_rectangle(bx1, by1, bx2, by2, fill="#78350f", outline="#451a03", width=max(4, int(8 * scale)))
                canvas.create_rectangle(bx1 + 14, by1 + 14, bx2 - 14, by2 - 14, fill="#92400e", outline="#78350f", width=max(2, int(4 * scale)))
                
                # Clous en laiton aux 4 coins
                nail_r = max(4, int(10 * scale))
                for (nx, ny) in [(bx1 + 24, by1 + 24), (bx2 - 24, by1 + 24), (bx1 + 24, by2 - 24), (bx2 - 24, by2 - 24)]:
                    canvas.create_oval(nx - nail_r, ny - nail_r, nx + nail_r, ny + nail_r, fill="#f59e0b", outline="#78350f", width=2)
                    
                # Parchemin intérieur crème / ivoire chaleureux
                canvas.create_rectangle(bx1 + 30, by1 + 30, bx2 - 30, by2 - 30, fill="#fef3c7", outline="#fde68a", width=3)
                
                # Ruban rouge supérieur ÉNORME
                rub_y = by1 + int(60 * scale)
                rub_h = int(32 * scale)
                rub_indent = int(65 * scale)
                canvas.create_polygon([
                    (bx1 + rub_indent, rub_y - rub_h), (bx2 - rub_indent, rub_y - rub_h),
                    (bx2 - rub_indent + 15, rub_y), (bx2 - rub_indent, rub_y + rub_h),
                    (bx1 + rub_indent, rub_y + rub_h), (bx1 + rub_indent - 15, rub_y)
                ], fill="#dc2626", outline="#991b1b", width=3)
                
                header_font_size = max(11, int(26 * scale))
                canvas.create_text(cx, rub_y, text="📬 MESSAGE DE AHMED 📬", font=("Impact", header_font_size, "bold"), fill="#ffffff")
                
                # Nettoyage et formatage du message
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
                    
                display_msg = f"« {clean_msg} »"
                
                # Calibrage dynamique pour un texte VRAIMENT ÉNORME
                msg_len = len(display_msg)
                if msg_len < 60:
                    base_font_sz = 38
                elif msg_len < 140:
                    base_font_sz = 30
                else:
                    base_font_sz = 24
                    
                actual_font_sz = max(10, int(base_font_sz * scale))
                
                # Ombre douce sous le texte pour le relief
                canvas.create_text(
                    cx + 2, cy + int(10 * scale) + 2, text=display_msg,
                    font=("Impact", actual_font_sz), fill="#94a3b8",
                    width=int(cur_bw * 0.84), justify="center"
                )
                # Texte noir anthracite net
                canvas.create_text(
                    cx, cy + int(10 * scale), text=display_msg,
                    font=("Impact", actual_font_sz), fill="#0f172a",
                    width=int(cur_bw * 0.84), justify="center"
                )
                
                # Sceau de cire rouge géant officiel en bas à gauche
                seal_x = bx1 + int(90 * scale)
                seal_y = by2 - int(75 * scale)
                seal_r = int(34 * scale)
                if seal_r > 8:
                    canvas.create_oval(seal_x - seal_r, seal_y - seal_r, seal_x + seal_r, seal_y + seal_r, fill="#b91c1c", outline="#7f1d1d", width=3)
                    canvas.create_text(seal_x, seal_y, text="POSTE\\nOFFICIELLE", font=("Impact", max(6, int(9 * scale)), "bold"), fill="#fef08a", justify="center")
                    
                # Bouton Cartoon 3D Géant en bas au centre
                btn_w = int(320 * scale)
                btn_h = int(60 * scale)
                btn_x1 = cx - btn_w // 2 + int(40 * scale)
                btn_y1 = by2 - int(95 * scale)
                btn_x2 = btn_x1 + btn_w
                btn_y2 = btn_y1 + btn_h
                
                if btn_w > 40:
                    canvas.create_rectangle(btn_x1 + 4, btn_y1 + 4, btn_x2 + 4, btn_y2 + 4, fill="#0f172a", outline="")
                    btn_tag = canvas.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#16a34a", outline="#14532d", width=3)
                    canvas.create_line(btn_x1 + 8, btn_y1 + 5, btn_x2 - 8, btn_y1 + 5, fill="#86efac", width=3)
                    btn_txt_sz = max(9, int(18 * scale))
                    btn_text = canvas.create_text(btn_x1 + btn_w//2, btn_y1 + btn_h//2, text="J'AI COMPRIS ! 👍", font=("Impact", btn_txt_sz, "bold"), fill="#ffffff")
                    
                    canvas.tag_bind(btn_tag, "<Button-1>", lambda e: _start_close())
                    canvas.tag_bind(btn_text, "<Button-1>", lambda e: _start_close())
                    canvas.tag_bind(btn_tag, "<Enter>", lambda e: canvas.itemconfig(btn_tag, fill="#22c55e"))
                    canvas.tag_bind(btn_tag, "<Leave>", lambda e: canvas.itemconfig(btn_tag, fill="#16a34a"))
                    
                # 3. Dessin du Personnage Cartoon (Livreur Express)
                char_x = anim_data["char_x"]
                char_y = anim_data["char_y"]
                c_scale = min(1.2, max(0.6, scale * 1.1))
                
                if anim_data["state"] in ("SETTLED", "REBOUND"):
                    # Posé au-dessus du panneau avec gants blancs tenant le bord
                    gw = int(22 * c_scale)
                    gh = int(18 * c_scale)
                    canvas.create_oval(cx - int(120*c_scale), by1 - 5, cx - int(80*c_scale), by1 + gh, fill="#ffffff", outline="#0f172a", width=2)
                    canvas.create_oval(cx + int(80*c_scale), by1 - 5, cx + int(120*c_scale), by1 + gh, fill="#ffffff", outline="#0f172a", width=2)
                    
                canvas.create_oval(char_x - int(38*c_scale), char_y - int(15*c_scale), char_x + int(38*c_scale), char_y + int(42*c_scale), fill="#1d4ed8", outline="#0f172a", width=3)
                canvas.create_oval(char_x - 5, char_y + 2, char_x + 5, char_y + 12, fill="#facc15", outline="")
                canvas.create_oval(char_x - 5, char_y + 18, char_x + 5, char_y + 28, fill="#facc15", outline="")
                
                head_y = char_y - int(45 * c_scale)
                head_r = int(34 * c_scale)
                canvas.create_oval(char_x - head_r, head_y - head_r, char_x + head_r, head_y + head_r, fill="#fed7aa", outline="#c2410c", width=3)
                canvas.create_oval(char_x - head_r, head_y + 4, char_x - int(15*c_scale), head_y + int(20*c_scale), fill="#fca5a5", outline="")
                canvas.create_oval(char_x + int(15*c_scale), head_y + 4, char_x + head_r, head_y + int(20*c_scale), fill="#fca5a5", outline="")
                
                canvas.create_oval(char_x - int(24*c_scale), head_y - int(20*c_scale), char_x - int(4*c_scale), head_y + int(8*c_scale), fill="#ffffff", outline="#0f172a", width=2)
                canvas.create_oval(char_x + int(4*c_scale), head_y - int(20*c_scale), char_x + int(24*c_scale), head_y + int(8*c_scale), fill="#ffffff", outline="#0f172a", width=2)
                canvas.create_oval(char_x - int(16*c_scale), head_y - int(14*c_scale), char_x - int(8*c_scale), head_y - int(2*c_scale), fill="#0f172a", outline="")
                canvas.create_oval(char_x + int(8*c_scale), head_y - int(14*c_scale), char_x + int(16*c_scale), head_y - int(2*c_scale), fill="#0f172a", outline="")
                canvas.create_oval(char_x - int(14*c_scale), head_y - int(12*c_scale), char_x - int(11*c_scale), head_y - int(7*c_scale), fill="#ffffff", outline="")
                canvas.create_oval(char_x + int(10*c_scale), head_y - int(12*c_scale), char_x + int(13*c_scale), head_y - int(7*c_scale), fill="#ffffff", outline="")
                
                canvas.create_arc(char_x - int(20*c_scale), head_y + 4, char_x + int(20*c_scale), head_y + int(28*c_scale), start=180, extent=180, fill="#450a0a", outline="#0f172a", width=2)
                canvas.create_polygon([(char_x - 10, head_y + 14), (char_x, head_y + 22), (char_x + 10, head_y + 14)], fill="#ffffff", outline="")
                
                cap_y = head_y - int(28 * c_scale)
                canvas.create_oval(char_x - int(42*c_scale), cap_y - int(18*c_scale), char_x + int(42*c_scale), cap_y + int(12*c_scale), fill="#1e3a8a", outline="#0f172a", width=3)
                canvas.create_arc(char_x - int(46*c_scale), cap_y - int(4*c_scale), char_x + int(46*c_scale), cap_y + int(24*c_scale), start=0, extent=180, fill="#0f172a", outline="")
                canvas.create_oval(char_x - int(10*c_scale), cap_y - int(10*c_scale), char_x + int(10*c_scale), cap_y + int(8*c_scale), fill="#facc15", outline="#713f12", width=1)
                canvas.create_text(char_x, cap_y - 1, text="★", font=("Arial", max(8, int(11*c_scale)), "bold"), fill="#78350f")
                
            _tick_anim()
            
            if HAS_WINSOUND:
                try:
                    import winsound
                    def _play_chime():
                        try:
                            winsound.Beep(880, 120)
                            winsound.Beep(1320, 180)
                        except Exception:
                            pass
                    threading.Thread(target=_play_chime, daemon=True).start()
                except Exception:
                    pass
            
            if not root:
                win.mainloop()
        except Exception:
            pass
            
    if root:
        root.after(0, _create_gui)
    else:
        threading.Thread(target=_create_gui, daemon=True).start()

'''

content = content[:idx_start] + new_func + content[idx_end:]

with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Compilation et validation de {SCRIPT_PATH}...")
py_compile.compile(SCRIPT_PATH, doraise=True)
print("SUCCESS: show_troll_window_on_client mis à jour avec lancer géant et rebond !")

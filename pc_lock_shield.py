# -*- coding: utf-8 -*-
"""
================================================================================
    GHOST BIOMETRIC LOCK SHIELD - MODERNE (HTML5/CSS3/JS WEBVIEW2) & BLE RSSI
================================================================================
Fonctionnalités :
1. Interface utilisateur moderne, épurée et haute technologie en HTML5/CSS3/JavaScript
   via Edge WebView2 (PyWebView) : particules 60 FPS, radar néon, animations fluides.
2. Verrouillage total et impénétrable (Plein écran Kiosk, Alt+Tab, Win, TaskMgr bloqués).
3. Raccourci secret discret (Ctrl + Shift + Alt + U) : ouvre une modal de saisie du PIN
   sans aucun bouton visible sur l'écran.
4. Mesure de distance par Bluetooth BLE RSSI : verrouille à l'éloignement sans couper MQTT.
5. Gestion intelligente de l'activation/désactivation de la proximité pour éviter
   tout spam de verrouillage.
6. Service permanent 24/7 en arrière-plan sans fenêtre console.
================================================================================
"""

import os
import sys
import time
import json
import socket
import threading
import subprocess
import asyncio
import ctypes
from ctypes import wintypes
import winreg
import atexit
import webview
from PIL import Image

try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

try:
    from bleak import BleakScanner
    HAS_BLEAK = True
except ImportError:
    HAS_BLEAK = False

# ==============================================================================
# CONFIGURATION & CONSTANTES
# ==============================================================================
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ghost_shield.log")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
DEVICE_NAME = socket.gethostname().lower()
MQTT_TOPIC_STATUS = f"ghost_lock/{DEVICE_NAME}/status"
MQTT_TOPIC_CMD = f"ghost_lock/{DEVICE_NAME}/cmd"
MQTT_TOPIC_HEARTBEAT = f"ghost_lock/{DEVICE_NAME}/heartbeat"

SECRET_BACKUP_PIN = "1234"
RSSI_NEAR_THRESHOLD = -74  # dBm : l'utilisateur est près/au bureau -> réarme l'auto-verrouillage
RSSI_LOCK_THRESHOLD = -77  # dBm : l'utilisateur s'éloigne -> déclenche le verrouillage automatique


# Codes de touches Windows
WH_KEYBOARD_LL = 13
VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_F4 = 0x73
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12

# ==============================================================================
# HOOK CLAVIER BAS-NIVEAU
# ==============================================================================
keyboard_hook = None
hook_active = False

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

def _low_level_keyboard_proc(nCode, wParam, lParam):
    global hook_active
    if nCode >= 0 and hook_active:
        kbd = KBDLLHOOKSTRUCT.from_address(lParam)
        vk = kbd.vkCode
        alt_pressed = (kbd.flags & 0x20) != 0

        ctrl_down = (ctypes.windll.user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0
        shift_down = (ctypes.windll.user32.GetAsyncKeyState(VK_SHIFT) & 0x8000) != 0
        alt_down = (ctypes.windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000) != 0 or alt_pressed

        # Raccourci discret : Ctrl + Shift + Alt + U
        if vk == ord('U') and ctrl_down and shift_down and alt_down:
            if shield_instance:
                shield_instance.prompt_discrete_pin()
            return 1

        if vk in (VK_LWIN, VK_RWIN):
            return 1
        if alt_pressed and vk in (VK_TAB, VK_ESCAPE, VK_F4):
            return 1
        if ctrl_down and vk == VK_ESCAPE:
            return 1

    return ctypes.windll.user32.CallNextHookEx(keyboard_hook, nCode, wParam, lParam)

_hook_func = HOOKPROC(_low_level_keyboard_proc)

def install_keyboard_lock():
    global keyboard_hook, hook_active
    if keyboard_hook is None:
        hook_active = True
        mod = ctypes.windll.kernel32.GetModuleHandleW(None)
        keyboard_hook = ctypes.windll.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL, _hook_func, mod, 0
        )

def uninstall_keyboard_lock():
    global keyboard_hook, hook_active
    hook_active = False
    if keyboard_hook is not None:
        ctypes.windll.user32.UnhookWindowsHookEx(keyboard_hook)
        keyboard_hook = None

# ==============================================================================
# GESTION SYSTEME WINDOWS
# ==============================================================================
def set_taskbar_visible(visible=True):
    try:
        hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 5 if visible else 0)
    except Exception:
        pass

def set_taskmgr_disabled(disabled=True):
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        if disabled:
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        else:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "DisableTaskMgr")
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass
    except Exception:
        pass

@atexit.register
def cleanup_system():
    uninstall_keyboard_lock()
    set_taskbar_visible(True)
    set_taskmgr_disabled(False)

# ==============================================================================
# CAPTURE HAUTE VITESSE DU BUREAU (WIN32 GDI - ~35ms)
# ==============================================================================
def capture_desktop_background(output_path):
    """Capture instantanée du bureau Windows réel via GDI BitBlt sans ralentir le verrouillage"""
    try:
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass

        SM_XVIRTUALSCREEN = 76
        SM_YVIRTUALSCREEN = 77
        SM_CXVIRTUALSCREEN = 78
        SM_CYVIRTUALSCREEN = 79

        left = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        top = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
        width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
        height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

        if width <= 0 or height <= 0:
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            left, top = 0, 0

        hdesktop = user32.GetDesktopWindow()
        hdesktop_dc = user32.GetWindowDC(hdesktop)
        hmem_dc = gdi32.CreateCompatibleDC(hdesktop_dc)
        hbitmap = gdi32.CreateCompatibleBitmap(hdesktop_dc, width, height)
        h_old_bitmap = gdi32.SelectObject(hmem_dc, hbitmap)

        SRCCOPY = 0x00CC0020
        gdi32.BitBlt(hmem_dc, 0, 0, width, height, hdesktop_dc, left, top, SRCCOPY)

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ('biSize', wintypes.DWORD),
                ('biWidth', wintypes.LONG),
                ('biHeight', wintypes.LONG),
                ('biPlanes', wintypes.WORD),
                ('biBitCount', wintypes.WORD),
                ('biCompression', wintypes.DWORD),
                ('biSizeImage', wintypes.DWORD),
                ('biXPelsPerMeter', wintypes.LONG),
                ('biYPelsPerMeter', wintypes.LONG),
                ('biClrUsed', wintypes.DWORD),
                ('biClrImportant', wintypes.DWORD)
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = width
        bmi.biHeight = -height  # top-down DIB
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        buffer_len = width * height * 4
        buffer = ctypes.create_string_buffer(buffer_len)

        gdi32.GetDIBits(hmem_dc, hbitmap, 0, height, buffer, ctypes.byref(bmi), 0)

        # Nettoyage des handles GDI
        gdi32.SelectObject(hmem_dc, h_old_bitmap)
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hmem_dc)
        user32.ReleaseDC(hdesktop, hdesktop_dc)

        im = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA', 0, 1)
        im = im.convert('RGB')
        im.save(output_path, 'JPEG', quality=85)
        return True
    except Exception as e:
        log(f"[!] Erreur capture écran GDI: {e}")
        return False

# ==============================================================================
# API JS-PYTHON POUR LE FRONTEND WEB
# ==============================================================================
class LockJsApi:
    def verify_pin(self, pin):
        if str(pin).strip() == SECRET_BACKUP_PIN:
            log("[+] Code maître correct saisi dans l'interface web.")
            if shield_instance:
                threading.Thread(target=shield_instance.unlock, daemon=True).start()
            return True
        else:
            log(f"[!] Code maître erroné saisi : {pin}")
            return False

# ==============================================================================
# VÉRIFICATION DE PROCESSUS SILENCIEUSE (SANS AUCUNE FENÊTRE CMD/CONSOLE)
# ==============================================================================
class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]

def is_process_running_win32(process_name):
    """Vérifie en mémoire vive via l'API Win32 sans jamais ouvrir de fenêtre ou exécuter cmd"""
    TH32CS_SNAPPROCESS = 0x00000002
    h_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if h_snapshot == -1:
        return False
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    target_bytes = process_name.lower().encode("utf-8")
    
    found = False
    if ctypes.windll.kernel32.Process32First(h_snapshot, ctypes.byref(entry)):
        while True:
            if entry.szExeFile.lower() == target_bytes:
                found = True
                break
            if not ctypes.windll.kernel32.Process32Next(h_snapshot, ctypes.byref(entry)):
                break
    ctypes.windll.kernel32.CloseHandle(h_snapshot)
    return found

# ==============================================================================
# BOUCLIER DE VERROUILLAGE MODERNE
# ==============================================================================
shield_instance = None

class BiometricLockShield:
    def __init__(self):
        global shield_instance
        shield_instance = self
        self.window = None
        self.is_locked = False
        
        # Proximité Bluetooth
        self.current_rssi = None
        self.last_ble_seen = 0.0
        self.last_heartbeat_time = time.time()
        self.auto_lock_enabled = True
        self.was_near_since_unlock = False
        self.last_unlock_time = 0.0
        
        # MQTT
        self.mqtt_client = None
        self.setup_mqtt()
        
        # Bleak Scanner
        if HAS_BLEAK:
            self.ble_thread = threading.Thread(target=self._run_ble_scanner, daemon=True)
            self.ble_thread.start()
            
        # Watchdog de proximité (Anti-Spam)
        self.watchdog_thread = threading.Thread(target=self._proximity_watchdog, daemon=True)
        self.watchdog_thread.start()

        # Émission périodique du statut (Heartbeat)
        self.status_beacon_thread = threading.Thread(target=self._status_beacon_loop, daemon=True)
        self.status_beacon_thread.start()

        # Suivi d'inactivité du viewer (fermeture auto de ghost_script si quitté > 5 min)
        self.viewer_is_open = False
        self.viewer_last_left_timestamp = 0.0
        self.last_viewer_heartbeat = 0.0
        self.ghost_watchdog_thread = threading.Thread(target=self._ghost_script_watchdog, daemon=True)
        self.ghost_watchdog_thread.start()

    def setup_mqtt(self):
        if not HAS_MQTT:
            return
        try:
            client_id = f"ghost_pc_lock_{int(time.time())}"
            try:
                self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
            except Exception:
                try:
                    self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
                except Exception:
                    self.mqtt_client = mqtt.Client(client_id=client_id)
            
            offline_payload = json.dumps({
                "device": DEVICE_NAME,
                "locked": self.is_locked,
                "online": False,
                "time_str": "Déconnecté"
            })
            self.mqtt_client.will_set(MQTT_TOPIC_STATUS, offline_payload, qos=1, retain=False)

            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            log(f"[!] Erreur MQTT: {e}")

    def _on_mqtt_connect(self, client, userdata, flags, rc, *args):
        is_ok = (rc == 0) or (hasattr(rc, "is_failure") and not rc.is_failure)
        if is_ok:
            log(f"[+] Connecté au broker MQTT ({MQTT_BROKER})")
            client.subscribe(MQTT_TOPIC_CMD)
            client.subscribe(MQTT_TOPIC_HEARTBEAT)
            self.publish_status()
        else:
            log(f"[!] Échec connexion MQTT: {rc}")

    def _on_mqtt_message(self, client, userdata, msg, *args):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic = msg.topic
            
            if topic == MQTT_TOPIC_HEARTBEAT:
                self.last_heartbeat_time = time.time()
                
            elif topic == MQTT_TOPIC_CMD:
                action = payload.get("action")
                if action == "unlock":
                    log("[*] Reçu ordre de DÉVERROUILLAGE (Empreinte validée sur Redmi A3) !")
                    self.unlock()
                elif action == "lock":
                    log("[*] Reçu ordre de VERROUILLAGE (Empreinte validée sur Redmi A3) !")
                    self.lock()
                elif action == "set_auto_lock":
                    enabled = payload.get("enabled", True)
                    self.auto_lock_enabled = enabled
                    self.last_ble_seen = 0.0  # Réinitialise pour empêcher tout verrouillage résiduel
                    log(f"[*] Auto-verrouillage à distance réglé à : {enabled}")
                elif action in ("launch_ghost_script", "start_ghost_script"):
                    log("[*] Reçu ordre de LANCEMENT de GHOST SCRIPT (Empreinte validée sur Redmi A3) !")
                    self.launch_ghost_script()
                elif action in ("viewer_resumed", "viewer_heartbeat"):
                    self.viewer_is_open = True
                    self.viewer_last_left_timestamp = 0.0
                    self.last_viewer_heartbeat = time.time()
                    if action == "viewer_resumed":
                        log("[*] Le viewer est actif sur le téléphone. Compteur de fermeture réinitialisé.")
                elif action in ("viewer_left", "viewer_closed"):
                    self.viewer_is_open = False
                    self.viewer_last_left_timestamp = time.time()
                    log("[*] Le viewer a été quitté sur le téléphone. Fermeture automatique de ghost_script.exe prévue dans 5 minutes (300s).")
        except Exception as e:
            log(f"[!] Erreur traitement message: {e}")

    def _is_ghost_script_process_running(self):
        return is_process_running_win32("ghost_script.exe")

    def launch_ghost_script(self):
        """Lance ghost_script.exe UNIQUEMENT sur demande expresse depuis l'application mobile"""
        log("[*] Demande de lancement de ghost_script.exe...")
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Réinitialise les timestamps du viewer
        self.viewer_is_open = True
        self.viewer_last_left_timestamp = 0.0
        self.last_viewer_heartbeat = time.time()

        if self._is_ghost_script_process_running():
            log("[i] ghost_script.exe est déjà en cours d'exécution.")
            return

        candidates = [
            os.path.join(base_dir, "ghost_script.exe"),
            os.path.join(base_dir, "dist", "ghost_script.exe"),
            os.path.join(base_dir, "dist", "ghost_script_updated.exe"),
        ]
        
        exe_to_launch = None
        for cand in candidates:
            if os.path.isfile(cand):
                exe_to_launch = cand
                break

        if exe_to_launch:
            try:
                log(f"[+] Démarrage du processus : {exe_to_launch}")
                subprocess.Popen(
                    [exe_to_launch],
                    cwd=base_dir,
                    creationflags=0x08000000
                )
                log("[OK] ghost_script.exe lancé avec succès en arrière-plan !")
            except Exception as e:
                log(f"[!] Erreur au lancement de {exe_to_launch}: {e}")
        else:
            py_cand = os.path.join(base_dir, "ghost_script.py")
            if os.path.isfile(py_cand):
                try:
                    log("[+] Fallback : lancement de ghost_script.py...")
                    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                    subprocess.Popen(
                        [python_exe, py_cand],
                        cwd=base_dir,
                        creationflags=0x08000000
                    )
                    log("[OK] ghost_script.py lancé avec succès !")
                except Exception as e:
                    log(f"[!] Erreur au lancement de ghost_script.py: {e}")
            else:
                log("[!] Aucun exécutable ou script ghost_script trouvé !")

    def stop_ghost_script(self):
        """Ferme immédiatement et proprement ghost_script.exe via MQTT et terminaison de processus"""
        log("[*] Fermeture automatique de ghost_script.exe en cours...")
        
        # 1. Envoi de l'ordre d'auto-extinction MQTT à ghost_script
        try:
            if self.mqtt_client:
                hostname = socket.gethostname().lower()
                try:
                    username = os.getlogin().lower()
                except Exception:
                    username = "zakri"
                c_id = f"{hostname}_{username}".replace(" ", "_")
                kill_payload = json.dumps({"action": "kill_client"})
                
                self.mqtt_client.publish(f"ghost_protocol/stream/zakri/{c_id}/cmd", kill_payload, qos=1)
                self.mqtt_client.publish("ghost_protocol/stream/zakri/cmd", kill_payload, qos=1)
        except Exception as e:
            log(f"[!] Erreur notification MQTT kill: {e}")

        # 2. Sécurité supplémentaire par taskkill sans console
        try:
            subprocess.run(["taskkill", "/F", "/IM", "ghost_script.exe"], capture_output=True, creationflags=0x08000000)
        except Exception:
            pass

        self.viewer_is_open = False
        self.viewer_last_left_timestamp = 0.0
        self.last_viewer_heartbeat = 0.0
        log("[OK] ghost_script.exe a été fermé avec succès.")

    def _ghost_script_watchdog(self):
        """Surveille ghost_script.exe et le ferme si le viewer est quitté depuis plus de 5 minutes (300s)"""
        while True:
            time.sleep(3)
            
            if not self._is_ghost_script_process_running():
                continue

            now = time.time()

            # Cas 1 : Le viewer a été quitté (action viewer_left / viewer_closed reçue)
            if not self.viewer_is_open and self.viewer_last_left_timestamp > 0:
                elapsed = now - self.viewer_last_left_timestamp
                if elapsed >= 300:  # 5 minutes (300 secondes)
                    log(f"[!] Le viewer a été quitté depuis {int(elapsed)}s (> 5 minutes). Fermeture automatique de ghost_script.exe...")
                    self.stop_ghost_script()

            # Cas 2 : Perte de signal sans notification explicite (fermeture brutale / réseau coupé)
            elif self.viewer_is_open and self.last_viewer_heartbeat > 0:
                elapsed = now - self.last_viewer_heartbeat
                if elapsed >= 315:  # 5 minutes + 15s de battement
                    log(f"[!] Aucun signal du viewer depuis {int(elapsed)}s (> 5 minutes). Fermeture automatique de ghost_script.exe...")
                    self.stop_ghost_script()

    def _status_beacon_loop(self):
        while True:
            time.sleep(2.5)
            self.publish_status()

    def _run_ble_scanner(self):
        async def scan_loop():
            def on_detection(device, adv_data):
                name = (device.name or "").lower()
                if "ghostlock" in name or "redmi" in name or "0000ffe0" in str(adv_data.service_uuids):
                    self.current_rssi = adv_data.rssi
                    self.last_ble_seen = time.time()

            try:
                scanner = BleakScanner(detection_callback=on_detection)
                await scanner.start()
                while True:
                    await asyncio.sleep(1)
            except Exception as e:
                log(f"[!] Erreur Bleak: {e}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scan_loop())

    def _proximity_watchdog(self):
        """Verrouille si le téléphone s'éloigne (après avoir été présent au bureau)"""
        time.sleep(3)
        weak_count = 0
        while True:
            time.sleep(1.0)
            if not self.auto_lock_enabled or self.is_locked:
                time.sleep(0.5)
                continue

            now = time.time()

            # RÈGLE VITALE : Si le viewer est ouvert sur le téléphone, l'utilisateur consulte son écran à distance.
            # L'auto-verrouillage par distance BLE est mis en PAUSE pour ne pas interrompre le visionnage !
            is_viewer_active = self.viewer_is_open or ((now - self.last_viewer_heartbeat) < 15.0)
            if is_viewer_active:
                weak_count = 0
                time.sleep(1.0)
                continue

            # Vérification si la balise BLE du téléphone a été vue récemment (< 12 secondes)
            is_seen = (self.last_ble_seen > 0) and ((now - self.last_ble_seen) < 12.0)

            # 1. Détection immédiate du retour à proximité : RÉARMEMENT INSTANTANÉ
            if is_seen and self.current_rssi is not None:
                if self.current_rssi >= RSSI_NEAR_THRESHOLD:
                    if not self.was_near_since_unlock:
                        self.was_near_since_unlock = True
                        log(f"[+] Signal proche détecté (RSSI: {self.current_rssi} dBm >= {RSSI_NEAR_THRESHOLD} dBm). Système de verrouillage à l'éloignement RÉARMÉ !")
                        self.publish_status()
                    weak_count = 0

                elif self.current_rssi < RSSI_LOCK_THRESHOLD:
                    # Signal affaibli (< -77 dBm) : l'utilisateur s'éloigne
                    # Ne déclenche QUE si le système est réarmé (l'utilisateur est venu près depuis le déverrouillage)
                    # et que la cinématique d'ouverture est passée (> 8s)
                    if self.was_near_since_unlock and (now - self.last_unlock_time) > 8.0:
                        weak_count += 1
                        if weak_count >= 3:  # 3 secondes consécutives de signal faible
                            log(f"[!] ÉLOIGNEMENT DÉTECTÉ ({self.current_rssi} dBm < {RSSI_LOCK_THRESHOLD} dBm). Verrouillage automatique !")
                            self.was_near_since_unlock = False
                            weak_count = 0
                            self.lock()
                    else:
                        weak_count = 0
                else:
                    # Zone tampon de transition (-74 dBm à -77 dBm)
                    weak_count = 0
            else:
                # Balise hors de portée : ne déclenche QUE si l'utilisateur était présent au bureau depuis le déverrouillage
                if self.was_near_since_unlock and (now - self.last_unlock_time) > 8.0:
                    if self.last_ble_seen > 0 and (now - self.last_ble_seen) > 12.0:
                        log("[!] TÉLÉPHONE HORS DE PORTÉE (Quitté le bureau). Verrouillage automatique !")
                        self.was_near_since_unlock = False
                        self.last_ble_seen = 0.0
                        weak_count = 0
                        self.lock()


    def publish_status(self):
        if not self.mqtt_client:
            return
        try:
            data = {
                "device": DEVICE_NAME,
                "locked": self.is_locked,
                "online": True,
                "rssi": self.current_rssi,
                "armed": self.was_near_since_unlock,
                "timestamp": time.time(),
                "time_str": time.strftime("%H:%M:%S")
            }
            self.mqtt_client.publish(MQTT_TOPIC_STATUS, json.dumps(data), qos=1, retain=False)
        except Exception:
            pass

    def lock(self):
        if self.is_locked:
            return
        self.is_locked = True
        self.was_near_since_unlock = False
        log("[!] Verrouillage du PC activé. Lancement de l'animation de fermeture spatiale...")
        
        # 1. Capture instantanée (35ms) du vrai bureau Windows avant d'afficher la fenêtre
        try:
            bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_bg.jpg")
            capture_desktop_background(bg_path)
        except Exception as e:
            log(f"[!] Erreur pré-capture fond d'écran: {e}")

        set_taskbar_visible(False)
        set_taskmgr_disabled(True)
        install_keyboard_lock()
        
        if self.window:
            try:
                # Étape 1 : Prépare l'affichage identique au bureau réel (aucun saut visuel)
                self.window.evaluate_js("prepareLock()")
                self.window.show()
                # Étape 2 : Déclenche l'animation lente de flou spatial et de fermeture du cadenas
                self.window.evaluate_js("triggerLock()")
            except Exception as e:
                log(f"[!] Erreur affichage fenêtre lock: {e}")

        self.publish_status()

    def unlock(self):
        if not self.is_locked:
            return
        self.is_locked = False
        self.last_unlock_time = time.time()
        self.was_near_since_unlock = False
        self.last_ble_seen = 0.0
        self.current_rssi = None
        log("[+] Déverrouillage biométrique validé. Lancement de la cinématique Apple Vision Pro longue (6.4s)...")
        
        if self.window:
            try:
                self.window.evaluate_js("triggerUnlock()")
            except Exception:
                pass
            threading.Thread(target=self._delayed_hide, daemon=True).start()

        self.publish_status()


    def _delayed_hide(self):
        # À 5.5s : Restauration des contrôles système alors que le bureau est quasiment net à 95%
        time.sleep(5.5)
        uninstall_keyboard_lock()
        set_taskbar_visible(True)
        set_taskmgr_disabled(False)
        
        # À 6.4s : Le bureau est à 100% net (2.4s de défloutage après 3.8s de cinématique), masquage 100% invisible
        time.sleep(0.9)
        if not self.is_locked and self.window:
            try:
                self.window.hide()
                log("[OK] Bureau Windows révélé en netteté (cinématique longue 6.4s terminée) sans coupure.")
            except Exception:
                pass

    def prompt_discrete_pin(self):
        if self.window and self.is_locked:
            try:
                self.window.evaluate_js("openPinModal()")
            except Exception:
                pass

# ==============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    log(f"=== GHOST BIOMETRIC LOCK SHIELD (HTML5/CSS3/JS WEBVIEW2) ===")
    log(f"Machine: {DEVICE_NAME}")
    log(f"Broker MQTT: {MQTT_BROKER}")
    log(f"Topic Statut: {MQTT_TOPIC_STATUS}")
    log(f"Topic Ordres: {MQTT_TOPIC_CMD}")
    log(f"Raccourci discret secret: Ctrl + Shift + Alt + U")
    
    shield = BiometricLockShield()
    api = LockJsApi()
    
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lock_ui.html")
    bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_bg.jpg")
    if not os.path.exists(bg_path):
        capture_desktop_background(bg_path)
    
    # hidden=True est CRUCIAL pour éviter tout flash blanc au lancement de l'application
    shield.window = webview.create_window(
        'GhostLock Shield',
        url=html_path,
        fullscreen=True,
        on_top=True,
        frameless=True,
        hidden=True,
        background_color='#05060b',
        js_api=api
    )

    def on_webview_ready():
        if "--unlocked" in sys.argv or "--bg" in sys.argv or "--background" in sys.argv:
            # Mode démarrage en arrière-plan sans verrouillage initial
            log("[*] Bouclier actif en arrière-plan (Prêt 24h/24 sans verrouillage initial).")
            shield.publish_status()
        elif "--test" in sys.argv:
            shield.lock()
            def test_cycle():
                time.sleep(4)
                shield.unlock()
                time.sleep(7)
                shield.window.destroy()
            threading.Thread(target=test_cycle, daemon=True).start()
        else:
            # PAR DÉFAUT (et avec --lock) : Verrouillage absolu immédiat dès le démarrage
            log("[*] Démarrage GhostLock avec VERROUILLAGE IMMÉDIAT au lancement !")
            shield.lock()


    webview.start(on_webview_ready)

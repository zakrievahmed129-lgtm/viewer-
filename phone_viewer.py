# -*- coding: utf-8 -*-
"""
================================================================================
           GHOST PROTOCOL - PHONE STREAM VIEWER (REDMI A3 / VISION PRO)
================================================================================
Auteur      : Antigravity AI & zakri
Description : Viewer PC haute performance permettant de visualiser en direct 
              l'écran et la caméra du Xiaomi Redmi A3 (Android Go Edition)
              via streaming matériel MJPEG basse latence et contrôle MQTT.
================================================================================
"""

import os
import sys
import time
import json
import threading
import webbrowser
import urllib.request
from datetime import datetime
import webview
import paho.mqtt.client as mqtt

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TARGET_PC = "pc-zakriev"
TOPIC_STREAM_STATUS = f"ghost_lock/{TARGET_PC}/phone_stream/status"
TOPIC_STREAM_CMD = f"ghost_lock/{TARGET_PC}/phone_stream/cmd"

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)


class PhoneViewerBridge:
    """
    Pont d'appel non-bloquant entre JavaScript et Python.
    Toutes les opérations réseaux sont asynchrones pour garantir
    que l'interface ne gèle JAMAIS.
    """
    def __init__(self, app):
        self._app = app

    def getStreamStatus(self):
        """
        Interrogation instantanée en mémoire (0.01 ms).
        Évite tout interblocage COM / WebView2.
        """
        return {
            "ip": self._app.phone_ip,
            "port": 8888,
            "mode": self._app.last_mode,
            "is_active": self._app.last_is_active
        }

    def sendStreamCommand(self, target_mode):
        """
        Envoie l'ordre MQTT de façon asynchrone sans bloquer l'UI.
        """
        def _send():
            if target_mode == "screen":
                payload = {"action": "start_screen"}
            elif target_mode == "camera_back":
                payload = {"action": "start_camera", "lens": "back"}
            elif target_mode == "camera_front":
                payload = {"action": "start_camera", "lens": "front"}
            elif target_mode == "stop":
                payload = {"action": "stop"}
            else:
                payload = {"action": target_mode}
            self._app.publish_cmd(payload)

        threading.Thread(target=_send, daemon=True).start()
        return True

    def sendPhoneNotification(self, title, message):
        """
        Envoie une notification personnalisée avec son et vibration au Redmi A3.
        """
        def _send():
            final_title = title.strip() if title and title.strip() else "Message du PC de zakri 💻"
            final_msg = message.strip() if message and message.strip() else "Transmission en direct reçue depuis le PC !"
            payload = {
                "action": "notification",
                "title": final_title,
                "message": final_msg,
                "timestamp": int(time.time() * 1000)
            }
            # Publication sur le canal de stream et sur le canal général
            self._app.publish_cmd(payload)
            if self._app.mqtt_client and self._app.mqtt_client.is_connected():
                try:
                    self._app.mqtt_client.publish(f"ghost_lock/{TARGET_PC}/cmd", json.dumps(payload), qos=1)
                except Exception:
                    pass
            print(f"[>] Notification envoyée au téléphone : {payload}")

        threading.Thread(target=_send, daemon=True).start()
        return True

    def toggleKeepScreenOn(self, enabled):
        """
        Active ou désactive le maintien de l'écran allumé (anti-veille) sur le Redmi A3.
        """
        def _send():
            payload = {
                "action": "keep_screen_on",
                "enabled": bool(enabled)
            }
            self._app.publish_cmd(payload)
            print(f"[>] Commande anti-veille envoyée : {payload}")

        threading.Thread(target=_send, daemon=True).start()
        return True

    def setManualIp(self, ip):
        """
        Force manuellement l'adresse IP du Redmi A3.
        """
        self._app.phone_ip = ip.strip()
        return True

    def openInBrowser(self):
        """
        Ouvre directement le flux dans le navigateur web par défaut (Chrome, Edge, etc.)
        """
        url = f"http://{self._app.phone_ip}:8888"
        webbrowser.open(url)
        return True

    def captureSnapshot(self):
        """
        Télécharge une image instantanée du flux et l'enregistre sur le disque dur.
        """
        try:
            url = f"http://{self._app.phone_ip}:8888/stream.mjpg"
            req = urllib.request.Request(url, headers={'User-Agent': 'GhostViewer/1.0'})
            with urllib.request.urlopen(req, timeout=2.5) as response:
                content = b""
                for _ in range(40):
                    chunk = response.read(4096)
                    if not chunk:
                        break
                    content += chunk
                    start = content.find(b"\xff\xd8")
                    end = content.find(b"\xff\xd9", start + 2) if start != -1 else -1
                    if start != -1 and end != -1:
                        jpeg_bytes = content[start:end + 2]
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"redmi_a3_capture_{timestamp}.jpg"
                        filepath = os.path.join(CAPTURE_DIR, filename)
                        with open(filepath, "wb") as f:
                            f.write(jpeg_bytes)
                        return filename
        except Exception as e:
            print(f"[!] Erreur capture photo : {e}")
        return None


class PhoneViewerApp:
    def __init__(self):
        self.mqtt_client = None
        self.is_running = True
        self.phone_ip = "127.0.0.1"
        self.last_mode = "idle"
        self.last_is_active = False

        self.start_mqtt()

    def start_mqtt(self):
        def mqtt_thread_func():
            try:
                client_id = f"ghost_phone_viewer_{int(time.time())}"
                try:
                    self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
                except Exception:
                    self.mqtt_client = mqtt.Client(client_id=client_id)

                self.mqtt_client.on_connect = self.on_mqtt_connect
                self.mqtt_client.on_message = self.on_mqtt_message
                self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=30)
                self.mqtt_client.loop_forever()
            except Exception as e:
                print(f"[!] MQTT Exception: {e}")

        t = threading.Thread(target=mqtt_thread_func, daemon=True)
        t.start()

    def on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        print(f"[*] Connecté au broker MQTT (code {rc})")
        client.subscribe(TOPIC_STREAM_STATUS, qos=1)
        self.publish_cmd({"action": "get_status"})

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            self.phone_ip = payload.get("ip", self.phone_ip)
            self.last_mode = payload.get("mode", "idle")
            self.last_is_active = payload.get("is_active", False)
        except Exception as e:
            print(f"[!] Erreur décodage status MQTT : {e}")

    def publish_cmd(self, payload_dict):
        if self.mqtt_client and self.mqtt_client.is_connected():
            try:
                msg = json.dumps(payload_dict)
                self.mqtt_client.publish(TOPIC_STREAM_CMD, msg, qos=1)
                print(f"[>] Commande envoyée au téléphone : {msg}")
            except Exception as e:
                print(f"[!] Erreur publish MQTT : {e}")


def main():
    app = PhoneViewerApp()
    bridge = PhoneViewerBridge(app)

    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone_viewer.html")
    if not os.path.exists(html_file):
        print(f"[!] Fichier introuvable : {html_file}")
        sys.exit(1)

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    window = webview.create_window(
        title="Ghost Protocol • Redmi A3 Stream Viewer (Vision Pro)",
        html=html_content,
        js_api=bridge,
        width=1120,
        height=820,
        min_size=(680, 520),
        background_color="#06070B"
    )

    # Fermeture propre sans freeze
    def on_closed():
        app.is_running = False
        os._exit(0)

    window.events.closed += on_closed

    webview.start(debug=False)


if __name__ == "__main__":
    main()

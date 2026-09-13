# -*- coding: utf-8 -*-
import time
import socket
import threading
import io
from PIL import ImageGrab
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "ghost_protocol/stream/zakri_test_screencast"

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Sub: Connecté au broker avec le code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Sub: Image reçue ! Taille = {len(msg.payload)} octets")

def start_subscriber():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

def start_publisher():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    
    print("Pub: Démarrage de l'envoi de captures...")
    for i in range(5):
        try:
            screenshot = ImageGrab.grab()
            buf = io.BytesIO()
            screenshot.save(buf, format='JPEG', quality=50)
            jpeg_data = buf.getvalue()
            
            print(f"Pub: Envoi image {i+1} ({len(jpeg_data)} octets)...")
            client.publish(TOPIC, jpeg_data, qos=0)
            time.sleep(1.0)
        except Exception as e:
            print(f"Pub Error: {e}")
            
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    # Démarrer le subscriber dans un thread
    sub_thread = threading.Thread(target=start_subscriber, daemon=True)
    sub_thread.start()
    
    time.sleep(2.0)
    
    # Lancer le publisher dans le thread principal
    start_publisher()
    
    time.sleep(3.0)
    print("Test terminé.")

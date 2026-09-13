import json
import socket
import time
import paho.mqtt.client as mqtt

DEVICE_NAME = socket.gethostname().lower()
MQTT_TOPIC_CMD = f"ghost_lock/{DEVICE_NAME}/cmd"
MQTT_BROKER = "broker.hivemq.com"

client = mqtt.Client(client_id="test_unlocker")
client.connect(MQTT_BROKER, 1883, 60)
payload = json.dumps({"action": "unlock", "from": "redmi_a3"})
print(f"Publishing unlock to {MQTT_TOPIC_CMD}: {payload}")
client.publish(MQTT_TOPIC_CMD, payload, qos=1)
client.disconnect()
print("Sent successfully!")

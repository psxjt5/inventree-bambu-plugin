"""
BambuMQTTService: Manages the MQTT connection between the worker and individual printers.
"""

# MQTT connections.
import ssl
import json
import time
import paho.mqtt.client as mqtt

# Worker cache (front end server can read)
from django.core.cache import cache

class BambuMQTTService:

    def __init__(self, ip, port, token, machine, message_callback):
        self.ip = ip
        self.port = port
        self.token = token
        self.message_callback=lambda s, data: message_callback(machine, s, data)

        self.client = mqtt.Client(clean_session=True)
        self.client.username_pw_set("bblp", token)

        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)

        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def start(self):
        print("[BambuMQTTService] Starting Bambu listener...")
        self.client.connect(self.ip, self.port, keepalive=60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[BambuMQTTService] Connected successfully")
            client.subscribe("device/+/report")
        else:
            print(f"[BambuMQTTService] Connection failed: {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"[BambuMQTTService] Unexpected disconnect (rc={rc})")
        else:
            print("[BambuMQTTService] Clean disconnect")

    def on_message(self, client, userdata, msg):
        if not msg.payload:
            return

        try:
            payload = json.loads(msg.payload.decode())
        except Exception as e:
            print(f"[BambuMQTTService] JSON error: {e}")
            return

        serial = self.extract_serial(msg.topic)
        if not serial:
            return

        data = payload

        cache.set(
        f"bambu:{serial}",
        {
            "payload": payload,
            "last_seen": time.time(),
        },
        timeout=60
        )

        # Call the maching callback function
        if self.message_callback:
            try:
                self.message_callback(serial, payload)
            except Exception as e:
                print(f"[BambuMQTTService] Callback error: {e}")

    def extract_serial(self, topic):
        parts = topic.split("/")
        if len(parts) >= 3:
            return parts[1]
        return None
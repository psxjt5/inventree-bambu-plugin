"""
BambuMQTTService: Manages the MQTT connection between the worker and individual printers.
"""

# MQTT connections.
import ssl
import json
import time
import threading

import paho.mqtt.client as mqtt

# Worker cache (front end server can read)
from django.core.cache import cache

class BambuMQTTService:

    # Some printers only return all parameters if a "pushall" command is sent, and so this will be done periodically.
    PUSHALL_INTERVAL = 600 # 10 Minutes

    # Printers should be sending messages regularly, if messages aren't detected for this duration we can assume something is wrong.
    STALE_TIMEOUT = 30 # 30 Seconds

    def __init__(self, ip, port, token, serial, machine, message_callback):
        self.ip = ip
        self.port = port
        self.token = token
        self.serial = serial
        self.machine = machine

        self.message_callback=lambda s, data: message_callback(machine, s, data)
        
        self.last_message = None
        self.last_pushall = None
        self.connected = False

        self.client = mqtt.Client(clean_session=True)

        self.client.username_pw_set("bblp", token)

        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)

        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def start(self):
        print("[BambuMQTTService] Starting MQTT listener...")

        self.client.connect(self.ip, self.port, keepalive=60)

        self.client.loop_start()

        # Background monitoring loop
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[BambuMQTTService] Connected successfully")

            client.subscribe(f"device/{self.serial}/report")

            # Send a "pushall" upon connecting to get all parameters.
            self.connected = True;
            self.last_message = None
        else:
            print(f"[BambuMQTTService] Connection failed: {rc}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"[BambuMQTTService] Subscription active for {self.machine.name}")

        self.request_pushall()

    def on_disconnect(self, client, userdata, rc):
        self.connected = False;

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
        
        self.last_message = time.time()

        # This printer's cache key
        cache_key = f"bambu:{serial}"

        # Existing data (from previous snapshots)
        existing = cache.get(cache_key, {})
        existing_payload = existing.get("payload", {})

        # Merge in the new data
        merged_payload = self.deep_merge(existing_payload, payload)

        # Update the cache with the new (merged) data
        cache.set(
            cache_key,
            {
                "payload": merged_payload,
                "last_seen": self.last_message,
            },
            timeout=3600
        )

        # Call the matching callback function
        if self.message_callback:
            try:
                self.message_callback(serial, merged_payload)
            except Exception as e:
                print(f"[BambuMQTTService] Callback error: {e}")

    # Send a "pushall" command to the printer to get all field values.
    def request_pushall(self):

        now = time.time()

        # Only send a pushall if required.
        if now - self.last_pushall < 10:
            return

        topic = f"device/{self.serial}/request"

        payload = {
            "pushing": {
                "sequence_id": "0",
                "command": "pushall"
            }
        }

        self.client.publish(topic, json.dumps(payload))

        self.last_pushall = time.time()

        print(f"[BambuMQTTService] Requested pushall from {self.machine.name}")

    # Monitors incoming messages and requests full refreshes ("pushall") periodically.
    def monitor_loop(self):
        while True:
            now = time.time()

            # No messages for too long
            if self.connected and self.last_message and now - self.last_message > self.STALE_TIMEOUT:
                print(f"[BambuMQTTService] Printer stale: {self.machine.name}")

                try:
                    self.request_pushall()
                except Exception as e:
                    print(f"[BambuMQTTService] pushall failed: {e}")

            # Periodic full refresh
            if now - self.last_pushall > self.PUSHALL_INTERVAL:
                try:
                    self.request_pushall()
                except Exception as e:
                    print(f"[BambuMQTTService] periodic pushall failed: {e}")

            time.sleep(5)

    # Merge updated fields with existing fields (where all data hasn't been received).
    def deep_merge(self, old, new):

        if not isinstance(old, dict) or not isinstance(new, dict):
            return new

        merged = dict(old)

        for key, value in new.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self.deep_merge(merged[key], value)
            else:
                merged[key] = value

        return merged

    def extract_serial(self, topic):
        parts = topic.split("/")
        if len(parts) >= 3:
            return parts[1]
        return None
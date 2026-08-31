"""
BambuMQTTService: Manages the MQTT connection between the worker and individual printers.
"""

# MQTT connections.
import ssl
import json
import time
import threading
import copy

import paho.mqtt.client as mqtt

# Worker cache (front end server can read)
from django.core.cache import cache

class BambuMQTTService:

    # Some printers only return all parameters if a "pushall" command is sent, and so this will be done periodically.
    PUSHALL_INTERVAL = 600 # 10 Minutes

    # Printers should be sending messages regularly, if messages aren't detected for this duration we can assume something is wrong.
    STALE_TIMEOUT = 30 # 30 Seconds

    def __init__(self, printerName, ip, port, token, serial, message_callback, connection_callback):
        self.printerName = printerName
        self.ip = ip
        self.port = port
        self.token = token
        self.serial = serial

        self.message_callback=lambda: message_callback()
        self.connection_callback=lambda connectionStatus: connection_callback(connectionStatus)
        
        self.last_message = None
        self.last_pushall = 0.0

        self.thread = None

        self.client = mqtt.Client(clean_session=True)

        # TODO: Make this a parameter.
        self.client.username_pw_set("bblp", token)

        self.client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.tls_insecure_set(True)

        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    # Open a connection to the printer over MQTT
    def start(self):
        self.log("Starting MQTT Listener")

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        ).start()

    # MQTT connection and monitoring thread
    def run(self):

        next_pushall = time.monotonic() + self.PUSHALL_INTERVAL

        while True:
            try:

                if not self.client.is_connected():

                    result = self.client.connect(
                        self.ip,
                        self.port,
                        keepalive=60
                    )

                    self.log(f"MQTT Connection Requested: {result}")
                
                self.client.loop(timeout=1.0)

                now = time.monotonic()

                # Detect if printer seems to have gone silent
                if self.client.is_connected() and self.last_message is not None and now - self.last_message > self.STALE_TIMEOUT:
                    self.log(f"Printer stale")
                    self.request_pushall()

                # Send periodic PushAll messages
                if now >= next_pushall:
                    self.request_pushall()
                    next_pushall = now + self.PUSHALL_INTERVAL

            except Exception as exc:
                self.log(f"MQTT loop error: {exc}")
                time.sleep(1)

    # Connect Event
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.log("MQTT Connected Successfully")

            client.subscribe(f"device/{self.serial}/report")
        else:
            self.log(f"MQTT Connection Failed: {rc}")

        #self.connection_callback(self.client.is_connected())

    # Subscribe Event
    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.log(f"MQTT Subscription active")

        self.request_pushall()

    # Disconnect Event
    def on_disconnect(self, client, userdata, rc):
        self.last_message = None

        if rc != 0:
            self.log(f"Unexpected Disconnect (rc={rc})")
        else:
            self.log(f"Clean Disconnect")

        self.connection_callback(self.client.is_connected())

    # Message Received Event
    # TODO: Stop using the serial number as the message ID and instead use the machine PK
    def on_message(self, client, userdata, msg):
        if not msg.payload:
            return

        try:
            payload = json.loads(msg.payload.decode())
        except Exception as e:
            self.log(f"JSON error: {e}")
            return

        # Extract the Serial Number
        serialNumber = self.extract_serial(msg.topic)

        if not serialNumber:
            return
        
        self.last_message = time.time()

        # This printer's cache key
        # TODO: Swap to the Machine PK
        cache_key = f"bambu:{serialNumber}"

        # Get the existing data (from previous snapshots)
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
                self.message_callback()
            except Exception as e:
                self.log(f"Callback error: {e}")

    # Send a "pushall" command to the printer to get all field values.
    def request_pushall(self):

        if not self.client.is_connected():
            return

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

        result = self.client.publish(topic, json.dumps(payload))

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            self.log(f"PushAll publish failed: {result.rc}")

        self.last_pushall = time.time()

        self.log(f"Requested PushAll")

    # Merge updated fields with existing fields (where all data hasn't been received).
    def deep_merge(self, old, new):

        if not isinstance(old, dict) or not isinstance(new, dict):
            return new

        merged = copy.deepcopy(old)

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

    # Extract the serial number of the printer from the MQTT Payload
    def extract_serial(self, topic):
        parts = topic.split("/")
        if len(parts) >= 3:
            return parts[1]
        return None

    # Log a message about this MQTT Service
    def log(self, message):
            print(f"[BambuMQTTService - {self.printerName}] - {message}")
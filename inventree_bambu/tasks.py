import time
import json
import ssl
import paho.mqtt.client as mqtt
from django.core.cache import cache

def start_bambu_listener(machine_id, ip, token):
    """Persistent MQTT listener running in worker"""

    client = mqtt.Client()
    client.username_pw_set("bblp", token)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    def on_connect(client, userdata, flags, rc):
        print(f"[MQTT] Connected for machine {machine_id}: {rc}")
        client.subscribe("device/+/report")

    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        cache.set(f"bambu:{machine_id}", payload, timeout=60)

        try:
            from machine.models import Machine
            from .threed_printer import ThreeDPrinterStatus

            data = json.loads(payload)
            state_str = data["print"].get("gcode_state", "UNKNOWN")
            machine = Machine.objects.get(pk=machine_id)

            status = getattr(
                ThreeDPrinterStatus,
                state_str.upper(),
                ThreeDPrinterStatus.UNKNOWN
            )

            machine.set_status(status)

        except Exception as e:
            print(f"[MQTT] Status update error: {e}")

    client.on_connect = on_connect
    client.on_message = on_message

    # Single connect
    client.connect(ip, 8883)

    # Handles reconnects automatically
    client.loop_forever()
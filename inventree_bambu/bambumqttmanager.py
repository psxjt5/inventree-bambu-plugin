import threading
from .bambumqttservice import BambuMQTTService

_services = {}


def start_bambu_mqtt_service(ip, port, token):
    """
    Starts a MQTT service for the specified printer.
    Multiple instances are guarded against.
    """

    key = f"{ip}:{port}"

    if key in _services:
        return

    service = BambuMQTTService(ip, port, token)

    thread = threading.Thread(
        target=service.start,
        daemon=True
    )
    thread.start()

    _services[key] = service

    print(f"[BambuMQTTManager] Started service for {key}")
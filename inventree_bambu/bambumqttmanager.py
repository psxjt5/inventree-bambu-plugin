import threading
from .bambumqttservice import BambuMQTTService

class BambuMQTTManager:

    def __init__(self):
        self.service = {};
    
    def start_bambu_mqtt_service(self, ip, port, token):
        """
        Starts a MQTT service for the specified printer.
        Multiple instances are guarded against.
        """

        key = f"{ip}:{port}"

        if key in self.services:
            return

        service = BambuMQTTService(ip, port, token)

        thread = threading.Thread(
            target=service.start,
            daemon=True
        )
        thread.start()

        self.services[key] = service

        print(f"[BambuMQTTManager] Started service for {key}")
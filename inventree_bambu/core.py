"""Machine drivers and support for Bambu Lab 3D printers."""

import threading
import json
import socket
import paho.mqtt.client as mqtt
import ssl

from plugin import InvenTreePlugin
from plugin.mixins import MachineDriverMixin
from .threed_printer import ThreeDPrinterBaseDriver, ThreeDPrinterMachine, ThreeDPrinterStatus

from . import PLUGIN_VERSION


class InvenTreeBambuPlugin(MachineDriverMixin, InvenTreePlugin):

    """InvenTreeBambuPlugin - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "InvenTreeBambuPlugin"
    NAME = "InvenTreeBambuPlugin"
    SLUG = "inventreebambuplugin"
    DESCRIPTION = "Machine drivers and support for Bambu Lab 3D printers."
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "James Todd"
    WEBSITE = "https://github.com/psxjt5/inventree-bambu-plugin"
    LICENSE = "MIT"

    # Optionally specify supported InvenTree versions
    # MIN_VERSION = '0.18.0'
    # MAX_VERSION = '2.0.0'

    # Render custom UI elements to the plugin settings page
    #ADMIN_SOURCE = "Settings.js:renderPluginSettings"

    def get_machine_drivers(self) -> list:
        print("Registering Bambu Lab Printing Driver")
        return [BambuLabPrinterDriver]
    
    def get_machine_types(self) -> list:
        print("Registering 3D Printer Type")
        return [ThreeDPrinterMachine]
    
    
class BambuLabPrinterDriver(ThreeDPrinterBaseDriver):
    """Bambu Lab 3D Printer driver"""

    SLUG = "bambulab"
    NAME = "BambuLab 3D Printer"
    MACHINE_NAME = "Bambu Lab 3D Printer"
    DESCRIPTION = "Driver for Bambu Lab 3D printers"

    MACHINE_SETTINGS = {
        "IP_ADDRESS": {
            "name": "IP Address",
            "description": "Printer IP address",
            "default": "",
            "required": True,
        },
        "ACCESS_TOKEN": {
            "name": "Access Token",
            "description": "Printer API token",
            "default": "",
            "required": True,
        },
    }

    def init_machine(self, machine):
        """Called when machine is initialized"""
        print("Initialising Machine")
        self.latest_mqtt_message = None

        if self.test_connection(machine):
            machine.set_status(ThreeDPrinterStatus.IDLE)
            threading.Thread(
                target=self._mqtt_thread,
                args=(machine,),
                daemon=True
            ).start()
            print("Connection test successful")
        else:
            machine.set_status(ThreeDPrinterStatus.UNKNOWN)
            print("Connection test failed")

    def test_connection(self, machine) -> bool:
        """Check if the printer is reachable over MQTT."""
        ip = machine.get_setting("IP_ADDRESS", "D")
        port = 8883  # MQTT port for Bambu Lab printers in local mode

        try:
            with socket.create_connection((ip, port), timeout=3):
                return True
        except Exception:
            return False
        
    def get_status(self, machine):
        """Return current machine status from MQTT cache."""
        import json

        # self.latest_mqtt_message should be updated by your MQTT listener
        payload = self.latest_mqtt_message

        if not payload:
            return {"state": "offline"}

        try:
            data = json.loads(payload)
            device = data["print"]["device"]
            job = data["print"]
            
            state_str = data["print"].get("gcode_state", "UNKNOWN")
            layer = job.get("layer_num", 0)
            total = job.get("total_layer_num", 0)
            progress = int(layer / total * 100) if total else 0

            return {
                "state": state_str.lower(),  # "idle", "printing", etc.
                "progress": progress,
                "bed_temp": device["bed_temp"],
                "nozzle_temp": device["nozzle"]["info"][0]["temp"],
            }

        except Exception as e:
            return {"state": "offline", "error": str(e)}
        
    def _update_status_from_mqtt(self, machine):
        if not self.latest_mqtt_message:
            return

        try:
            data = json.loads(self.latest_mqtt_message)
            state_str = data["print"].get("gcode_state", "UNKNOWN")

            if not hasattr(ThreeDPrinterStatus, state_str.upper()):
                print(f"Unknown printer state: {state_str}")

            status = getattr(
                ThreeDPrinterStatus,
                state_str.upper(),
                ThreeDPrinterStatus.UNKNOWN
            )

            machine.set_status(status)

        except Exception as e:
            print(f"Error parsing MQTT payload: {e}")
    
    def _mqtt_thread(self, machine):
        """Persistent MQTT listener with auto-reconnect."""
        self.latest_mqtt_message = None

        while True:
            try:
                client = mqtt.Client()
                client.username_pw_set("bblp", machine.get_setting("ACCESS_TOKEN", "D"))
                client.tls_set()  # ensure TLS
                client.tls_set(cert_reqs=ssl.CERT_NONE)
                client.tls_insecure_set(True)

                def on_message(client, userdata, msg):
                    self.latest_mqtt_message = msg.payload.decode()
                    self._update_status_from_mqtt(machine)

                client.on_message = on_message

                # Use '+' to listen for any serial number
                client.connect(machine.get_setting("IP_ADDRESS", "D"), 8883)
                client.subscribe(f"device/+/report")
                client.loop_forever()  # blocks and reconnects automatically

            except Exception as e:
                print(f"MQTT connection error: {e}")
                import time
                time.sleep(5)
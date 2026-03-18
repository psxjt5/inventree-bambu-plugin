"""Machine drivers and support for Bambu Lab 3D printers."""

import threading
import json
import socket
import paho.mqtt.client as mqtt

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

        if self.test_connection(machine):
            machine.set_status(ThreeDPrinterStatus.CONNECTED)
        else:
            machine.set_status(ThreeDPrinterStatus.DISCONNECTED)

    def test_connection(self, machine) -> bool:
        """Check if the printer is reachable over MQTT."""
        ip = machine.get_setting("IP_ADDRESS", "M")
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
            
            state_str = data["print"]["upgrade_state"]["status"]
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
    
    ## Helper Functions
    def mqtt_listener(self, machine):
        client = mqtt.Client()
        client.username_pw_set("bblp", machine.get_setting("ACCESS_TOKEN", "M"))
        client.connect(machine.get_setting("IP_ADDRESS", "M"), 8883)
        
        def on_message(client, userdata, msg):
            self.latest_mqtt_message = msg.payload.decode()

        client.on_message = on_message
        client.subscribe(f"device/{machine.serial}/report")
        client.loop_start()
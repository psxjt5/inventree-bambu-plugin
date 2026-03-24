"""Machine drivers and support for Bambu Lab 3D printers."""

from .bambumqttmanager import BambuMQTTManager

import time
import socket

from django.http import JsonResponse
from django.core.cache import cache

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
            "description": "Printer IP Address",
            "default": "",
            "required": True,
        },
        "ACCESS_TOKEN": {
            "name": "Access Token",
            "description": "Printer API Token",
            "default": "",
            "required": True,
        },
        "SERIAL": {
            "name": "Serial Number",
            "description": "Printer Serial Number",
            "default": "",
            "required": True,
        }
    }

    DASHBOARD_WIDGETS = [
        {
            "component": "BambuDashboardWidget",
            "title": "Bambu Printer",
        }
    ]

    API_URLS = {
        "machine": "get_machine_info",
    }

    def init_machine(self, machine):
        """Called when machine is initialized"""
        self.initialise(machine)

    def restart_machine(self, machine):
        """Called when machine is restarted"""
        self.initialise(machine)

    def initialise(self, machine):
        print(f"[BambuLabPrinterDriver] Initialising Machine {machine.name}")
        machine.set_status(machine.MACHINE_STATUS.UNKNOWN)
        print("[BambuLabPrinterDriver] Machine status class:", machine.MACHINE_STATUS)
        print("[BambuLabPrinterDriver] Unknown value:", machine.MACHINE_STATUS.UNKNOWN)
        print("[BambuLabPrinterDriver] Choices:", getattr(machine.MACHINE_STATUS, 'choices', None))

        # if not self.validate_required_settings(machine):
        #     machine.set_status(ThreeDPrinterStatus.UNKNOWN)
        #     return
        
        # self.mqtt_manager = BambuMQTTManager()

        # if self.test_connection(machine):
        #     self.mqtt_manager.start_bambu_mqtt_service(
        #         ip=machine.get_setting("IP_ADDRESS", "D"),
        #         port=8883,
        #         token=machine.get_setting("ACCESS_TOKEN", "D"),
        #     )

        #     # Initialize status from cache
        #     # serial = machine.get_setting("SERIAL", "D")
        #     # data = cache.get(f"bambu:{serial}")
        #     # print(f"[BambuLabPrinterDriver] Fetching initial status: {data}")
        #     # if data and time.time() - data.get("last_seen", 0) < 30:
        #     #     state = data["payload"].get("print", {}).get("gcode_state")
        #     #     machine.set_status(self.map_state(state))
        #     # else:
        #     machine.set_status(ThreeDPrinterStatus.UNKNOWN)
        #     print(f"[BambuLabPrinterDriver] Connection test successful for {machine.name}")

        # else:
        #     machine.set_status(ThreeDPrinterStatus.UNKNOWN)
        #     print("[BambuLabPrinterDriver] Connection test failed")

    def validate_required_settings(self, machine) -> bool:
        """
        Ensure that all required machine settings are filled.

        Returns True if valid, False if any are missing.
        """
        required_fields = ["IP_ADDRESS", "ACCESS_TOKEN", "SERIAL"]

        missing = []
        for field in required_fields:
            value = machine.get_setting(field, "D")
            if not value:
                missing.append(field)

        if missing:
            print(f"[BambuLabPrinterDriver] Machine '{machine.name}' missing required settings: {missing}")
            return False

        return True

    def map_state(self, state: str):
        """
        Convert Bambu Lab gcode_state to ThreeDPrinterStatus.
        
        Parameters:
            state (str): Value of 'print.gcode_state' from MQTT
        
        Returns:
            ThreeDPrinterStatus
        """
        mapping = {
            "IDLE": ThreeDPrinterStatus.IDLE,
            "READY": ThreeDPrinterStatus.IDLE,
            "RUNNING": ThreeDPrinterStatus.RUNNING,
            "PAUSED": ThreeDPrinterStatus.PAUSED,
            "FINISHED": ThreeDPrinterStatus.FINISHED,
            "FAILED": ThreeDPrinterStatus.ERROR,
        }

        return mapping.get(state, ThreeDPrinterStatus.UNKNOWN)

    def get_status(self, machine):
        print(f"[BambuLabPrinterDriver] Getting status for {machine.name}")
        return ThreeDPrinterStatus.UNKNOWN

        serial = machine.get_setting("SERIAL", "D")
        if not serial:
            return ThreeDPrinterStatus.UNKNOWN

        data = cache.get(f"bambu:{serial}")

        if not data:
            return ThreeDPrinterStatus.UNKNOWN

        # Offline detection
        if time.time() - data["last_seen"] > 30:
            return ThreeDPrinterStatus.OFFLINE

        payload = data["payload"]

        state = payload.get("print", {}).get("gcode_state")

        return self.map_state(state)

    def test_connection(self, machine) -> bool:
        """Check if the printer is reachable over MQTT."""
        ip = machine.get_setting("IP_ADDRESS", "D")
        print(f"[BambuLabPrinterDriver] Connection test for {machine.name} at {ip}.")
        port = 8883

        try:
            with socket.create_connection((ip, port), timeout=3):
                print(f"[BambuLabPrinterDriver] Connection test successful for {machine.name} at {ip}.")
                return True
        except Exception:
            print(f"[BambuLabPrinterDriver] Connection test failed for {machine.name} at {ip}.")
            return False
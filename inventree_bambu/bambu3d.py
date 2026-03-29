from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _

from inventree_3d.threed import ThreeDPrinterBaseDriver, ThreeDPrinterMachine
from .bambumqttmanager import BambuMQTTManager

import socket

class BambuLab3DPrinterDriver(ThreeDPrinterBaseDriver):
    """BambuLab 3D Printing machine driver."""

    SLUG = "bambu-lab-3d-printer"
    NAME = "Bambu Lab 3D Printer"
    DESCRIPTION = "Bambu Lab 3D Printer driver for InvenTree"

    def __init__(self, *args, **kwargs):
        self.MACHINE_SETTINGS = {
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

        super().__init__(*args, **kwargs)

    def init_machine(self, machine):
        """Machine initialise hook"""
        print(f"[BambuLab3DPrinterDriver] Initialising Machine {machine.name}")

        # Check machine settings have been filled
        if not self.validate_required_settings(machine):
            print(f"[BambuLab3DPrinterDriver] Machine misconfigured {machine.name}")
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.MISCONFIGURED)
            return
        
        # Perform an initial connection test to the machine
        if not self.test_connection(machine):
            return
        
        # Begin the MQTT service for this machine
        self.mqtt_manager = BambuMQTTManager()
        self.mqtt_manager.start_bambu_mqtt_service(
            ip=machine.get_setting("IP_ADDRESS", "D"),
            port=8883,
            token=machine.get_setting("ACCESS_TOKEN", "D"),
            machine=machine,
            callback=self.message_received
        )
        
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
    
    def test_connection(self, machine) -> bool:
        """Check if the printer is reachable over the network."""
        ip = machine.get_setting("IP_ADDRESS", "D")
        print(f"[BambuLab3DPrinterDriver] Connection test for {machine.name} at {ip}.")
        port = 8883

        try:
            with socket.create_connection((ip, port), timeout=3):
                print(f"[BambuLab3DPrinterDriver] Connection test successful for {machine.name} at {ip}.")
                machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.CONNECTED)
                machine.set_status_text("Connection Test Successful.")
                return True
        except Exception:
            print(f"[BambuLab3DPrinterDriver] Connection test failed for {machine.name} at {ip}.")
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.DISCONNECTED)
            machine.set_status_text("Connection Test Unsuccessful.")
            return False
        
    def message_received(self, machine, serial, data):
        print(f"[BambuLab3DPrinterDriver] MQTT message for {machine.name}.")

        self.mqtt_set_status(machine, data.get("print", {}).get("gcode_state"))

    def mqtt_set_status(self, machine, state):
        if state == "IDLE":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.IDLE)
        elif state == "PREPARE":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PREPARING)
        elif state == "SLICING":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PREPARING)
        elif state == "RUNNING":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PRINTING)
        elif state == "PAUSE":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PAUSED)
        elif state == "FINISH":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.FINISHED)
        elif state == "FAILED":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.FAILED)



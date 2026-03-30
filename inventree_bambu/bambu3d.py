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

        self.MACHINE_PROPERTIES = {
            "MODEL": {
                "name": "Model",
                "description": "Printer Model",
                "type": "string",
            },
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
        
        # Determine the Model
        model = self.get_model(machine.get_setting("SERIAL", "D"))
        machine.set_properties([
            {'key': 'Model', 'value': f'{model}'},
        ])
        
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
        
    def get_model(self, sn: str) -> str:
        sn_map = {
            "31B": "H2C",
            "094": "H2D",
            "239": "H2D Pro",
            "093": "H2S",
            "00M": "X1C",
            "03W": "X1E",
            "01P": "P1S",
            "01S": "P1P",
            "039": "A1",
            "030": "A1 Mini"
        }
        prefix = sn[:3]
        return sn_map.get(prefix, "Unknown")

    def message_received(self, machine, serial, data):
        # Get the latest machine instance
        machine = ThreeDPrinterMachine.objects.get(pk=machine.pk)

        # Set the status of the printer.
        self.mqtt_set_status(machine, data.get("print", {}).get("gcode_state"))

        machine.save();

    def mqtt_set_status(self, machine, state):
        print(f"[BambuLab3DPrinterDriver] Setting status for {machine.name}: {state}.")
        if state == "IDLE":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.IDLE)
            machine.set_status_text("Printer Idle")
        elif state == "PREPARE":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PREPARING)
            machine.set_status_text("Print Preparing")
        elif state == "SLICING":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PREPARING)
            machine.set_status_text("Print Preparing")
        elif state == "RUNNING":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PRINTING)
            machine.set_status_text("Printing")
        elif state == "PAUSE":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.PAUSED)
            machine.set_status_text("Print Paused")
        elif state == "FINISH":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.FINISHED)
            machine.set_status_text("Print Completed")
        elif state == "FAILED":
            machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.FAILED)
            machine.set_status_text("Print Failed")



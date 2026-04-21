"""
Bambu3D: Bambu 3D Printing Driver.
"""

from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _

from inventree_3d.threed import ThreeDPrinterBaseDriver, ThreeDPrinterMachine
from .bambumqttmanager import BambuMQTTManager
from .bambudata import BambuData

#from plugin.base.event.events import trigger_event

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
        
        # Perform an initial connection test to the machine
        if not self.test_connection(machine):
            return
        
        # Initialise the properties
        print(f"[BambuLab3DPrinterDriver] Initialising machine properties for {machine.name}")
        self.init_properties(machine)
        
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
        
    def init_properties(self, machine):
        machine.set_properties([
            {'key': 'Model', 'value': ''},
            {'key': 'AMS Units', 'value': ''},
            {'key': 'Job Progress', 'value': '', 'type': 'progress', 'max_progress': '100'},
            {'key': 'Layer Progress', 'value': '', 'type': 'progress', 'max_progress': '100'},
            {'key': 'Current Layer', 'value': ''},
            {'key': 'Total Layers', 'value': ''},
            {'key': 'Remaining Time', 'value': ''},
            {'key': 'File Name', 'value': ''},
            {'key': 'Nozzle Temperature', 'value': ''},
            {'key': 'Nozzle Target Temperature', 'value': ''},
            {'key': 'Bed Temperature', 'value': ''},
            {'key': 'Bed Target Temperature', 'value': ''},
            {'key': 'Cooling Fan Speed', 'value': ''},
            {'key': 'Heatbreak Fan Speed', 'value': ''},
            {'key': 'Big Fan 1 Speed', 'value': ''},
            {'key': 'Big Fan 2 Speed', 'value': ''},
        ])

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
        # Set the status of the printer.
        self.mqtt_set_status(machine, BambuData.getStatus(serial))

        # Set the properties of the printer.
        self.update_property(machine, 'Model', BambuData.getModel(serial))
        self.update_property(machine, 'AMS Units', BambuData.getAMSUnitCount(serial))
        self.update_property(machine, 'Job Progress', BambuData.getProgress(serial))
        self.update_property(machine, 'Layer Progress', BambuData.getLayerProgress(serial))
        self.update_property(machine, 'Current Layer', BambuData.getCurrentLayer(serial))
        self.update_property(machine, 'Total Layers', BambuData.getTotalLayers(serial))
        self.update_property(machine, 'Remaining Time', BambuData.getRemainingTime(serial))
        self.update_property(machine, 'File Name', BambuData.getFileName(serial))
        self.update_property(machine, 'Nozzle Temperature', BambuData.getNozzleTemperature(serial))
        self.update_property(machine, 'Nozzle Target Temperature', BambuData.getNozzleTargetTemperature(serial))
        self.update_property(machine, 'Bed Temperature', BambuData.getBedTemperature(serial))
        self.update_property(machine, 'Bed Target Temperature', BambuData.getBedTargetTemperature(serial))
        self.update_property(machine, 'Cooling Fan Speed', BambuData.getCoolingFanSpeed(serial))
        self.update_property(machine, 'Heatbreak Fan Speed', BambuData.getHeatBreakFanSpeed(serial))
        self.update_property(machine, 'Big Fan 1 Fan Speed', BambuData.getBigFan1Speed(serial))
        self.update_property(machine, 'Big Fan 2 Fan Speed', BambuData.getBigFan2Speed(serial))

        #trigger_event(f'machine_config.saved', id=machine.pk, model='MachineConfig')

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

    def mqtt_set_model(self, machine, model):
        print(f"[BambuLab3DPrinterDriver] Setting model for {machine.name}: {model}.")

        self.update_property(machine, "Model", model)

    def mqtt_set_amsunits(self, machine, amsunits):
        print(f"[BambuLab3DPrinterDriver] Setting AMS units for {machine.name}: {amsunits}.")

        self.update_property(machine, "AMS Units", amsunits)

    def update_property(self, machine, key, value):
        # Get full property objects
        properties = {
            prop['key']: prop.copy()
            for prop in machine.get_properties()
        }

        if key in properties:
            properties[key]['value'] = value
        else:
            # fallback if property doesn't exist yet
            properties[key] = {'key': key, 'value': value}

        # Rebuild with full metadata preserved
        machine.set_properties(list(properties.values()))



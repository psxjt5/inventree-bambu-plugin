from inventree_3d.threed import ThreeDPrinterBaseDriver, ThreeDPrinterMachine
from .bambumqttservice import BambuMQTTService
from .bambudata import BambuData
from .notifications import Notifications

import socket
import threading

class BambuPrinterController:

    def __init__(self, machine):
        self.machine = machine

        self.ipAddress: str | None = None
        self.accessToken: str | None = None
        self.serial: str | None = None
        # TODO: Make this configurable (setting with default value of 8883)
        self.port: int = 8883

        self.connected: bool = False
        self.mqtt_service: BambuMQTTService | None = None
        
        self.status: str | None = None
        self.hms_codes = []


    def initialise(self):
        self.log("Initialising")

        # Check machine settings have been filled
        if not self.validate_required_settings():
            return

        self.set_printer_settings()

        # Perform an initial connection test to the machine
        if not self.test_connection():
            # Currently this returns, meaning that if the initial connection test fails the machine will need to be restarted to try again.
            # TODO: Make this try again periodically.
            return

        self.init_properties()

        self.init_mqtt_service()

        return


    # Ensure that InvenTree Printer settings have been filled
    def validate_required_settings(self) -> bool:
            
            required_fields = ["IP_ADDRESS", "ACCESS_TOKEN", "SERIAL"]
            missing = []

            for field in required_fields:
                value = self.machine.get_setting(field, "D")
                if not value:
                    missing.append(field)
    
            if missing:
                self.log(f"missing required settings: {missing}")
                self.machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.MISCONFIGURED)

                return False
    
            return True

    # Fetch the printer settings
    def set_printer_settings(self):
         self.ipAddress = self.machine.get_setting("IP_ADDRESS", "D")
         self.accessToken = self.machine.get_setting("ACCESS_TOKEN", "D")
         self.serial = self.machine.get_setting("SERIAL", "D")

    # Test the connection to the machine
    def test_connection(self) -> bool:
        self.log(f"Testing Connection")

        try:
            with socket.create_connection((self.ipAddress, self.port), timeout=3):
                self.log("Connection Test Successful")
                self.machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.CONNECTED)
                self.machine.set_status_text("Connection Test Successful.")
                return True
        except Exception:
            self.log("Connection Test Unsuccessful")
            self.machine.set_status(ThreeDPrinterMachine.MACHINE_STATUS.DISCONNECTED)
            self.machine.set_status_text("Connection Test Unsuccessful.")
            return False

    # Initialise machine property fields
    def init_properties(self):
        self.log("Initialising Properties")

        self.machine.set_properties([
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

    # Create an MQTT Service for the machine
    def init_mqtt_service(self):
         
        self.mqtt_service = BambuMQTTService(self.machine.name, self.ipAddress, self.port, self.accessToken, self.serial, self.message_received, self.connection_changed)

        self.mqtt_service.start();

        self.log("Started MQTT Service")


    # Gets triggered by the MQTT service when a new MQTT message is received.
    #TODO: Identifier needs to become machine.pk (not serial).
    def message_received(self):
        # Set the status of the printer.
        # Data is pulled from the cache (where it will have been stored against the printer's serial).
        self.set_status(BambuData.getStatus(self.serial))

        # Set the properties of the printer.
        self.update_property('Model', BambuData.getModel(self.serial))
        self.update_property('AMS Units', BambuData.getAMSUnitCount(self.serial))
        self.update_property('Job Progress', BambuData.getProgress(self.serial))
        self.update_property('Layer Progress', BambuData.getLayerProgress(self.serial))
        self.update_property('Current Layer', BambuData.getCurrentLayer(self.serial))
        self.update_property('Total Layers', BambuData.getTotalLayers(self.serial))
        self.update_property('Remaining Time', BambuData.getRemainingTime(self.serial))
        self.update_property('File Name', BambuData.getFileName(self.serial))
        self.update_property('Nozzle Temperature', BambuData.getNozzleTemperature(self.serial))
        self.update_property('Nozzle Target Temperature', BambuData.getNozzleTargetTemperature(self.serial))
        self.update_property('Bed Temperature', BambuData.getBedTemperature(self.serial))
        self.update_property('Bed Target Temperature', BambuData.getBedTargetTemperature(self.serial))
        self.update_property('Cooling Fan Speed', BambuData.getCoolingFanSpeed(self.serial))
        self.update_property('Heatbreak Fan Speed', BambuData.getHeatBreakFanSpeed(self.serial))
        self.update_property('Big Fan 1 Speed', BambuData.getBigFan1Speed(self.serial))
        self.update_property('Big Fan 2 Speed', BambuData.getBigFan2Speed(self.serial))

    # Gets triggered by the MQTT service when the connection state changes.
    def connection_changed(self, connectedStatus):
        if (connectedStatus == self.connected):
            return

        self.connected = connectedStatus

        if (connectedStatus):
            Notifications.printer_online_notification(self.machine.name, self.machine.pk)
        else:
            Notifications.printer_offline_notification(self.machine.name, self.machine.pk)


    # Sets the status of the machine (if changed).
    def set_status(self, newStatus):

        # Check for HMS Errors
        if (newStatus == "IDLE" or newStatus == "PAUSE") and BambuData.hasHMSErrorCodes(self.serial):
            newStatus = "ERROR"

        # If the state hasn't changed return.
        if newStatus == self.status:
            return

        self.log(f"Setting Status: {newStatus}")

        # Convert the status to an InvenTree compatiable status
        convertedStatus = BambuPrinterController.convert_status(newStatus)
        self.machine.set_status(convertedStatus)

        self.machine.set_status_text(self.convert_status_text(newStatus))

        # Send a status update notification
        if self.status is not None:
            try:
                self.send_status_notification(newStatus)
            except Exception as e:
                self.log(f"Notification error: {e}")

        # Store the new state
        self.status = newStatus

    # Sends the relevant notification when a status change occurs
    def send_status_notification(self, newStatus):
        match newStatus:
            case "IDLE":
                return
            case "PREPARE":
                return
            case "SLICING":
                return
            case "RUNNING":
                if self.status == "PAUSE":
                    Notifications.print_resumed_notification(self.machine.name, self.machine.pk)
                else:
                    Notifications.print_started_notification(self.machine.name, self.machine.pk)

                return
            case "PAUSE":
                Notifications.print_paused_notification(self.machine.name, self.machine.pk)
                return
            case "FINISH":
                Notifications.print_finished_notification(self.machine.name, self.machine.pk)
                return
            case "FAILED":
                Notifications.print_stopped_notification(self.machine.name, self.machine.pk)
                return
            case "ERROR":
                Notifications.printer_error_notification(self.machine.name, self.machine.pk, self.build_hms_error_output())
                return
            case _:
                return

    # Builds an error notification message
    def build_hms_error_output(self):
        errors = BambuData.getAllHMSErrorCodes(self.serial)

        error_messages = []

        for error in errors:
            description = BambuData.getHMSCodeDescription(
                self.serial,
                error
            )

            if description:
                error_messages.append(
                    f"• {error}\n  {description}"
                )
            else:
                error_messages.append(
                    f"• {error}\n  Description unavailable."
                )

        message = "Printer errors have been reported:\n\n" + "\n\n".join(error_messages)

        return message


    # Update a machine property
    def update_property(self, key, value):

        # Copy full property objects (NOT just values)
        properties = {}

        for k, v in self.machine.properties_dict.items():
            if isinstance(v, dict):
                properties[k] = v.copy()
            else:
                # fallback (shouldn't really happen, but safe)
                properties[k] = {'key': k, 'value': v}

        # Update the target property
        if key in properties:
            properties[key]['value'] = value
        else:
            properties[key] = {'key': key, 'value': value}

        # Reapply properties with metadata preserved
        self.machine.set_properties(list(properties.values()))

    # Log a message about this machine
    def log(self, message):
         print(f"[BambuPrinterController - {self.machine.name}] - {message}")

    # Convert an MQTT status to a ThreeD status
    @staticmethod
    def convert_status(status):
        match status:
            case "IDLE":
                return ThreeDPrinterMachine.MACHINE_STATUS.IDLE
            case "PREPARE":
                return ThreeDPrinterMachine.MACHINE_STATUS.PREPARING
            case "SLICING":
                return ThreeDPrinterMachine.MACHINE_STATUS.PREPARING
            case "RUNNING":
                return ThreeDPrinterMachine.MACHINE_STATUS.PRINTING
            case "PAUSE":
                return ThreeDPrinterMachine.MACHINE_STATUS.PAUSED
            case "FINISH":
                return ThreeDPrinterMachine.MACHINE_STATUS.FINISHED
            case "FAILED":
                return ThreeDPrinterMachine.MACHINE_STATUS.FAILED
            case "ERROR":
                return ThreeDPrinterMachine.MACHINE_STATUS.ERROR
            case _:
                return ThreeDPrinterMachine.MACHINE_STATUS.UNKNOWN

    # Convert an MQTT status to status text
    @staticmethod
    def convert_status_text(status):
        match status:
            case "IDLE":
                return "Printer Idle"
            case "PREPARE":
                return "Print Preparing"
            case "SLICING":
                return "Print Preparing"
            case "RUNNING":
                return "Printing"
            case "PAUSE":
                return "Print Paused"
            case "FINISH":
                return "Print Completed"
            case "FAILED":
                return "Print Failed"
            case "ERROR":
                return "Printer Error"
            case _:
                return ""
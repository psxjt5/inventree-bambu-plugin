"""Machine drivers and support for Bambu Lab 3D printers."""

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
        import requests

        ip = machine.get_setting("IP_ADDRESS", "M")
        token = machine.get_setting("ACCESS_TOKEN", "M")

        try:
            r = requests.get(
                f"http://{ip}/status",
                headers={"Authorization": f"Bearer {token}"},
                timeout=3,
            )
            return r.status_code == 200
        except Exception:
            return False
        
    def get_status(self, machine):
        import requests

        ip = machine.get_setting("IP_ADDRESS", "M")
        token = machine.get_setting("ACCESS_TOKEN", "M")

        try:
            r = requests.get(
                f"http://{ip}/status",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            data = r.json()

            return {
                "state": ThreeDPrinterStatus.CONNECTED,
                "progress": data.get("progress"),
                "hotend_temp": data.get("hotend_temp"),
                "bed_temp": data.get("bed_temp"),
            }

        except Exception as e:
            return {
                "state": ThreeDPrinterStatus.DISCONNECTED,
                "error": str(e),
            }
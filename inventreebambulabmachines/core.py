"""Machine drivers and support for Bambu Lab 3D printers."""

from plugin import InvenTreePlugin
from plugin.machine import BaseMachineType
from plugin.machine.machine_types import BaseMachine

from . import PLUGIN_VERSION


class InvenTreeBambuLabMachines(InvenTreePlugin):

    """InvenTreeBambuLabMachines - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "InvenTreeBambuLabMachines"
    NAME = "InvenTreeBambuLabMachines"
    SLUG = "inventreebambulabmachines"
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
    ADMIN_SOURCE = "Settings.js:renderPluginSettings"

    def get_machine_drivers(self):
        return [BambuLabPrinterDriver]
    
    
class BambuLabPrinterDriver(BaseMachineType):
    """Bambu Lab 3D Printer driver"""

    SLUG = "bambulab"
    NAME = "BambuLab 3D Printer"
    MACHINE_NAME = "Bambu Lab 3D Printer"
    MACHINE_CLASS = BaseMachine
    DESCRIPTION = "Driver for Bambu Lab 3D printers"

    def __init__(self, *args, **kwargs):

        self.MACHINE_SETTINGS = {
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

        super().__init__(*args, **kwargs)

    def init_machine(self, machine):
        """Called when machine is initialized"""

        if self.test_connection(machine):
            machine.set_status("idle")
        else:
            machine.set_status("offline")

    def test_connection(self, machine) -> bool:
        import requests

        ip = machine.get_setting("IP_ADDRESS")
        token = machine.get_setting("ACCESS_TOKEN")

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

        ip = machine.get_setting("IP_ADDRESS")
        token = machine.get_setting("ACCESS_TOKEN")

        try:
            r = requests.get(
                f"http://{ip}/status",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            data = r.json()

            return {
                "state": "online",
                "progress": data.get("progress"),
                "hotend_temp": data.get("hotend_temp"),
                "bed_temp": data.get("bed_temp"),
            }

        except Exception as e:
            return {
                "state": "offline",
                "error": str(e),
            }
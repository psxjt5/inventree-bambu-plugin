"""3D Printing Support for InvenTree.

Adds support for 3D printing drivers to integrate into various parts of the system.
"""

from . import PLUGIN_VERSION

# InvenTree plugin libs
from report.models import LabelTemplate
from plugin import InvenTreePlugin
from plugin.machine import BaseMachineType
from .bambu3d import BambuLab3DPrinterDriver

# Backwards compatibility imports
try:
    from plugin.mixins import MachineDriverMixin, UserInterfaceMixin, SettingsMixin
except ImportError:

    class MachineDriverMixin:
        """Dummy mixin for backwards compatibility."""

        pass

class Bambu3DPlugin(MachineDriverMixin, UserInterfaceMixin, SettingsMixin, InvenTreePlugin):
    """BambuLab 3D Printing support for InvenTree."""

    AUTHOR = "James Todd"
    DESCRIPTION = "BambuLab 3D Printing support for InvenTree"
    VERSION = PLUGIN_VERSION

    MIN_VERSION = "0.16.0"

    NAME = "Bambu 3D Printing"
    SLUG = "bambu-3d-printing"
    TITLE = "BambuLab 3D Printing Support"

    def get_machine_drivers(self) -> list:
        print("Registering BambuLab 3D Printer Machine")
        return [BambuLab3DPrinterDriver]
    
    def get_ui_dashboard_items(self, request, context: dict, **kwargs):
        #if not request.user or not request.user.is_staff:
        #    return []
        
        items = []

        items.append({
            'key': 'Inventree-Bambu-Dashboard',
            'title': 'Bambu 3D Printer Dashboard',
            'description': 'Dashboard item for Bambu Lab 3D Printers.',
            'icon': 'ti:dashboard:outline',
            'source': self.plugin_static_file('Dashboard.js:renderBambuDashboardItem'),
            'context': {
                # Provide additional context data to the dashboard item
                'settings': self.get_settings_dict()
            },
            'options': {
                'width': 5,
                'height': 3
            }
        })

        return items
"""
Bambu3D_Plugin: Primary plugin registry (entry point).

3D Printing Support for InvenTree.

Adds support for 3D printing drivers to integrate into various parts of the system.
"""

from . import PLUGIN_VERSION

# InvenTree plugin libs
from report.models import LabelTemplate
from plugin import InvenTreePlugin
from plugin.machine import BaseMachineType
from .bambu3d import BambuLab3DPrinterDriver
from .bambuapi import BambuAPI

from django.urls import path

# Backwards compatibility imports
try:
    from plugin.mixins import MachineDriverMixin, UrlsMixin, UserInterfaceMixin, SettingsMixin
except ImportError:

    class MachineDriverMixin:
        """Dummy mixin for backwards compatibility."""

        pass

class Bambu3DPlugin(MachineDriverMixin, UrlsMixin, UserInterfaceMixin, SettingsMixin, InvenTreePlugin):
    """BambuLab 3D Printing support for InvenTree."""

    AUTHOR = "James Todd"
    DESCRIPTION = "BambuLab 3D Printing support for InvenTree"
    VERSION = PLUGIN_VERSION

    MIN_VERSION = "0.16.0"

    NAME = "Inventree Bambu"
    SLUG = "inventree_bambu"
    TITLE = "BambuLab 3D Printing Support"

    def get_machine_drivers(self) -> list:
        print("[BambuLab3DPrinterPlugin] Registering BambuLab 3D Printer Machine")
        return [BambuLab3DPrinterDriver]
    
    def setup_urls(self):
        print("[BambuLab3DPrinterPlugin] Registering BambuLab 3D API URLs")

        return [
            path("get_printer_data/<str:machine_serial>", BambuAPI.get_printer_data),
        ]
    
    def get_ui_dashboard_items(self, request, context: dict, **kwargs):
        print("[BambuLab3DPrinterPlugin] Registering Dashboard Widgets")
        #if not request.user or not request.user.is_staff:
        #    return []
        
        items = []

        items.append({
            'key': 'Inventree_Bambu-Dashboard',
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

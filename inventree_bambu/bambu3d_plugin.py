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
from django.contrib.auth.models import Group
from .notifications import Notifications

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

    @staticmethod
    def get_notification_groups():
        return [
            (str(group.pk), group.name)
            for group in Group.objects.order_by('name')
        ]

    AUTHOR = "James Todd"
    DESCRIPTION = "BambuLab 3D Printing support for InvenTree"
    VERSION = PLUGIN_VERSION

    MIN_VERSION = "0.16.0"

    NAME = "Inventree Bambu"
    SLUG = "inventree_bambu"
    TITLE = "BambuLab 3D Printing Support"

    SETTINGS = {
        'THREED_GROUP': {
            'name': '3D Printing Group',
            'description': 'Bambu 3D Printing users group.',
            'choices': get_notification_groups,
        },
    }

    USER_SETTINGS = {
        "NOTIFY_PRINT_START": {
            "name": "Print Started Notifications",
            "description": "Receive a notification when a print is started.",
            "default": True,
            "type": "boolean",
            "validator": bool
        },
        "NOTIFY_PRINT_ERROR": {
            "name": "Print Error Notifications",
            "description": "Receive a notification when a printer error occurs.",
            "default": True,
            "type": "boolean",
            "validator": bool
        },
        "NOTIFY_PRINT_FINISHED": {
            "name": "Print Finished Notifications",
            "description": "Receive a notification when a print finishes.",
            "default": True,
            "type": "boolean",
            "validator": bool
        },
        "NOTIFY_PRINTER_ONLINE": {
            "name": "Printer Online Notifications",
            "description": "Receive a notification when a printer comes online.",
            "default": True,
            "type": "boolean",
            "validator": bool
        },
        "NOTIFY_PRINTER_OFFLINE": {
            "name": "Printer Offline Notifications",
            "description": "Receive a notification when a printer goes offline.",
            "default": True,
            "type": "boolean",
            "validator": bool
        }
    }
    
    def __init__(self):
        super().__init__()

        print("[BambuLab3DPrinterPlugin] Plugin initialised")

        if not self.get_setting('THREED_GROUP'):
            Notifications.setup_group_notification(self.plugin_config())

    def get_machine_drivers(self) -> list:
        print("[BambuLab3DPrinterPlugin] Registering BambuLab 3D Printer Machine")
        return [BambuLab3DPrinterDriver]
    
    def setup_urls(self):
        print("[BambuLab3DPrinterPlugin] Registering BambuLab 3D API URLs")

        return [
            path("get_printer_data/<str:machine_serial>", BambuAPI.get_printer_data),
            path("get_dashboard_widget_data", BambuAPI.get_dashboard_widget_data),
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

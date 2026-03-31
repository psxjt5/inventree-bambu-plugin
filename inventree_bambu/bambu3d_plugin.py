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
    from plugin.mixins import MachineDriverMixin
except ImportError:

    class MachineDriverMixin:
        """Dummy mixin for backwards compatibility."""

        pass

class Bambu3DPlugin(MachineDriverMixin, InvenTreePlugin):
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
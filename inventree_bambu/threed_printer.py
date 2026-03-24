"""3D Printer machine type."""

from typing import cast

from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _

from generic.states import ColorEnum
from machine.machine_type import BaseDriver, BaseMachineType, MachineStatus
from stock.models import StockLocation

# Base Driver (Inherited by user-written specific printer drivers.)
class ThreeDPrinterBaseDriver(BaseDriver):
    """Base driver for 3D printer machines.
    """

    machine_type = '3d-printer'

    USE_BACKGROUND_WORKER = True

# Enum containing printer statuses.
class ThreeDPrinterStatus(MachineStatus):
    """Label printer status codes.

    Attributes:
        UNKNOWN: The printer status is unknown (e.g. there is no active connection to the printer)
        IDLE: The printer is connected and waiting for a job
        PRINTING: The printer is currently printing a job
        WARNING: The printer is in an unknown warning condition
        ERROR: The printer is in an unknown error condition
    """

    UNKNOWN = 0, _('Unknown'), ColorEnum.secondary
    IDLE = 1, _('Idle'), ColorEnum.success
    RUNNING = 2, _('Printing'), ColorEnum.primary
    PAUSED = 3, _('Paused'), ColorEnum.warning
    FINISHED = 4, _('Finished'), ColorEnum.success
    ERROR = 5, _('Error'), ColorEnum.danger

# Machine Type
class ThreeDPrinterMachine(BaseMachineType):
    """3D printer machine type."""

    SLUG = '3d-printer'
    NAME = _('3D Printer')
    DESCRIPTION = _('Control 3D Printers.')

    base_driver = ThreeDPrinterBaseDriver

    MACHINE_SETTINGS = {
        'LOCATION': {
            'name': _('Printer Location'),
            'description': _('Scope the printer to a specific location'),
            'model': 'stock.stocklocation',
        }
    }

    MACHINE_STATUS: type[ThreeDPrinterStatus] = ThreeDPrinterStatus

    default_machine_status = ThreeDPrinterStatus.UNKNOWN

    @property
    def location(self):
        """Access the machines location instance using this property."""
        location_pk = self.get_setting('LOCATION', 'M')

        if not location_pk:
            return None

        return StockLocation.objects.get(pk=location_pk)
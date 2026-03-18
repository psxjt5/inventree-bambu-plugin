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


class ThreeDPrinterBaseDriver(BaseDriver):
    """Base driver for 3D printer machines.
    """

    machine_type = '3D-printer'

    USE_BACKGROUND_WORKER = True


class ThreeDPrinterStatus(MachineStatus):
    """Label printer status codes.

    Attributes:
        CONNECTED: The printer is connected and ready to print
        UNKNOWN: The printer status is unknown (e.g. there is no active connection to the printer)
        PRINTING: The printer is currently printing a label
        WARNING: The printer is in an unknown warning condition
        NO_MEDIA: The printer is out of media (e.g. the label spool is empty)
        PAPER_JAM: The printer has a paper jam
        DISCONNECTED: The driver cannot establish a connection to the printer
        ERROR: The printer is in an unknown error condition
    """

    CONNECTED = 100, _('Connected'), ColorEnum.success
    UNKNOWN = 101, _('Unknown')# , ColorEnum.secondary
    PRINTING = 110, _('Printing'), ColorEnum.primary
    WARNING = 200, _('Warning'), ColorEnum.warning
    NO_MEDIA = 301, _('No media'), ColorEnum.warning
    PAPER_JAM = 302, _('Paper jam'), ColorEnum.warning
    DISCONNECTED = 400, _('Disconnected'), ColorEnum.danger
    ERROR = 500, _('Error'), ColorEnum.danger


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
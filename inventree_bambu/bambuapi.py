"""
BambuAPI: API methods for Bambu Lab printers.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .bambudata import BambuData

class BambuAPI:

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_printer_data(request, machine_serial):
        """Return data for a specific printer"""

        print("[BambuAPI] Get Printer Data")

        data = {
            "serial": machine_serial,
            "status": BambuData.getStatus(machine_serial),
            "model": BambuData.getModel(machine_serial),
            "ams_count": BambuData.getAMSUnitCount(machine_serial)
        }

        return Response(data)




"""
BambuAPI: API methods for Bambu Lab printers.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class BambuAPI:

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def example_endpoint(request, machine_id):
        """Return data for a specific printer"""

        data = {
            "id": machine_id,
            "name": f"Printer {machine_id}",
            "state": "idle",
            "progress": None,
        }

        return Response(data)
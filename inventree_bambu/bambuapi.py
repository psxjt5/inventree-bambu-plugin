"""
BambuAPI: API methods for Bambu Lab printers.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

class BambuAPI:
    
    @api_view(["GET"])
    def example_endpoint(request):
        """Very basic test endpoint"""

        data = [
            {
                "id": 1,
                "name": "Printer 1",
                "state": "idle",
                "progress": None,
            },
            {
                "id": 2,
                "name": "Printer 2",
                "state": "running",
                "progress": 42,
            },
        ]

        return Response(data)
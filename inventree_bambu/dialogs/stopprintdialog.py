from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from ..bambuutils import BambuUtils, PrinterNotFound, PrinterMQTTServiceNotFound


class StopPrintDialog(generics.GenericAPIView):
    """Stop the current print (no fields; the dialog just confirms)."""

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Serializer  # empty, but lets the InvenTree dialog load

    def post(self, request, pk):
        """Stops the current print."""
        try:
            mqtt = BambuUtils.get_printer_mqtt_service(pk)  # however you look up the controller
        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)
        except PrinterMQTTServiceNotFound:
            return Response({"error": "Printer MQTT Service not found"}, status=404)
        
        mqtt.request_stop_print()
        
        return Response(status=202)
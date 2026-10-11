from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..bambuutils import BambuUtils, PrinterNotFound, PrinterFTPSServiceNotFound

class MoveSerializer(serializers.Serializer):
    path = serializers.CharField()
    names = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    destination = serializers.CharField(label="Move to")


class MovePrinterFiles(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MoveSerializer

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        base = data["path"].rstrip("/")

        try:
            BambuUtils.get_printer_ftps_service(pk).move_files([f"{base}/{name}" for name in data["names"]], data["destination"])
        
        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)
        
        except PrinterFTPSServiceNotFound:
            return Response({"error": "Printer FTPS Service not found"}, status=404)
        
        return Response(status=200)
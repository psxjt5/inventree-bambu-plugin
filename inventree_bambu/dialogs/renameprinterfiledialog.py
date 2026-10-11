from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..bambuutils import BambuUtils, PrinterNotFound, PrinterFTPSServiceNotFound


class RenamePrinterFileSerializer(serializers.Serializer):
    path = serializers.CharField() # current folder, sent hidden from the UI
    old_name = serializers.CharField()
    new_name = serializers.CharField(label="New name", max_length=255)

    def validate_name(self, value):
        value = value.strip()
        if not value or "/" in value:
            raise serializers.ValidationError('Enter a file name without "/"')
        return value


class RenamePrinterFileDialog(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RenamePrinterFileSerializer
    
    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        base = data["path"].rstrip("/")

        try:
            return Response({"directories": BambuUtils.get_printer_ftps_service(pk).rename_file(base, data['old_name'], data['new_name'])})
        
        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)
            raise serializers.ValidationError({"name": "Printer not found"})
        
        except PrinterFTPSServiceNotFound:
            return Response({"error": "Printer FTPS Service not found"}, status=404)
            raise serializers.ValidationError({"name": "Printer FTPS Service not found"})
        
        return Response(status=200)
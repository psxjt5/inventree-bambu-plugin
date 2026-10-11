from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..bambuutils import BambuUtils, PrinterNotFound, PrinterFTPSServiceNotFound

#from machine.models import MachineSetting
class CreateDirectorySerializer(serializers.Serializer):
    path = serializers.CharField()  # current folder, sent hidden from the UI
    name = serializers.CharField(label="Folder name", max_length=255)

    def validate_path(self, value):
        if not value.startswith("/"):
            raise serializers.ValidationError("Path must be absolute")
        return value

    def validate_name(self, value):
        value = value.strip()
        if not value or "/" in value:
            raise serializers.ValidationError('Enter a folder name without "/"')
        return value

class CreatePrinterDirectoryDialog(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateDirectorySerializer

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        base = serializer.validated_data["path"].rstrip("/")
        full_path = f"{base}/{serializer.validated_data['name']}"

        try:
            return Response({"directories": BambuUtils.get_printer_ftps_service(pk).create_directory(full_path)})

        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)
            raise serializers.ValidationError({"name": "Printer not found"})

        except PrinterFTPSServiceNotFound:
            return Response({"error": "Printer FTPS Service not found"}, status=404)
            raise serializers.ValidationError({"name": "Printer FTPS Service not found"})

        return Response({"path": full_path}, status=201)
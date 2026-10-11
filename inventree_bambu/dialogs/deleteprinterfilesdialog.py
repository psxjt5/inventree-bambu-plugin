from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..bambuutils import BambuUtils, PrinterNotFound, PrinterFTPSServiceNotFound

class DeleteSerializer(serializers.Serializer):
    path = serializers.CharField()
    names = serializers.ListField(child=serializers.CharField(), allow_empty=False)

class DeletePrinterFilesDialog(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteSerializer

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        base = data["path"].rstrip("/")

        try:
            BambuUtils.get_printer_ftps_service(pk).delete_files(data["path"], data["names"])
        
        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)
        
        except PrinterFTPSServiceNotFound:
            return Response({"error": "Printer FTPS Service not found"}, status=404)
        
        return Response(status=200)
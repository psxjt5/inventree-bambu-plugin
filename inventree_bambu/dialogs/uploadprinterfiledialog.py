import ftplib
import os

from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..bambuftpsservice import BambuFTPSService


class UploadFileSerializer(serializers.Serializer):
    path = serializers.CharField()  # current folder, sent hidden from the UI
    file = serializers.FileField(label="File")

    def validate_file(self, value):
        name = os.path.basename(value.name)
        if not name or name in (".", ".."):
            raise serializers.ValidationError("Invalid file name")
        return value


class UploadPrinterFile(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        upload = serializer.validated_data["file"]
        base = serializer.validated_data["path"].rstrip("/")
        remote_path = f"{base}/{os.path.basename(upload.name)}"

        # ...look up ip_address / access_token as in get_printer_files...

        try:
            BambuFTPSService(ip_address, access_token).upload_fileobj(upload, remote_path)
        except ftplib.error_perm as e:
            raise serializers.ValidationError({"file": str(e)})

        return Response({"path": remote_path}, status=201)
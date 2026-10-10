from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class CreateDirectorySerializer(serializers.Serializer):
    path = serializers.CharField()  # current folder, sent hidden from the UI
    name = serializers.CharField(label="Folder name", max_length=255)

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

        # ...look up ip_address / access_token as in get_printer_files...

        try:
            BambuFTPSService(ip_address, access_token).create_directory(full_path)
        except ftplib.error_perm as e:
            # Shown under the "Folder name" field in the dialog
            raise serializers.ValidationError({"name": str(e)})

        return Response({"path": full_path}, status=201)
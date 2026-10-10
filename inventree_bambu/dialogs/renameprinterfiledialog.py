from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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

        # ...look up ip_address / access_token...

        try:
            BambuFTPSService(ip_address, access_token).rename(
                f"{base}/{data['old_name']}",
                f"{base}/{data['new_name']}",
            )
        except ftplib.error_perm as e:
            raise serializers.ValidationError({"new_name": str(e)})

        return Response(status=200)
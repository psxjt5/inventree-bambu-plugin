from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

        # ...look up ip_address / access_token...

        try:
            BambuFTPSService(ip_address, access_token).delete_paths(
                [f"{base}/{name}" for name in data["names"]]
            )
        except ftplib.error_perm as e:
            raise serializers.ValidationError({"non_field_errors": [str(e)]})

        return Response(status=200)
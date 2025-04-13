from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse

import ultraimport

Engine = ultraimport("__dir__/../../encryption/engine.py", "Engine")

class FileGenerateKeyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return HttpResponse(Engine().generate_random_key(), content_type="application/octet-stream")


class FileEncryptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        key = bytes(request.headers["X-Encryption-Key"].encode("utf-8"))
        raw_data = request.FILES["file"].file.read()

        encoded = Engine().encode(raw_data, key)

        return HttpResponse(encoded, content_type="application/octet-stream")


class FileDecryptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        key = bytes(request.headers["X-Encryption-Key"].encode("utf-8"))
        encrypted_data = request.FILES["file"].file.read()

        decoded = Engine().decode(encrypted_data, key)

        return HttpResponse(decoded, content_type="application/octet-stream")

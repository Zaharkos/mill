from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse

class FileEncryptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Encryption layer


class FileDecryptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
                
        # TODO: Decryption layer

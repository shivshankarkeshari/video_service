from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status


class VideoUploadView(APIView):
    def get(self, req):
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
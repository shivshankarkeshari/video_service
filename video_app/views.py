from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from moviepy.editor import VideoFileClip
from .serializer import VideoSerializer, SharedLinkSerializer
from .models import Video, SharedLink
from datetime import datetime, timedelta
from django.http import FileResponse

class CustomAPIView(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]


from contextlib import ExitStack
from functools import partial

class VideoFileOperation:
    def __init__(self):
        self.max_duration = 25
        self.min_duration = 5

    def get_video_duration(self, file_path):
        try:
            clip = VideoFileClip(file_path)
            duration = clip.duration  # in seconds
            clip.close()
            return duration, None
        except Exception as e:
            return None, Response({'error': f'Error processing video: {str(e)}'}, status=500)
    
    def validate_video_duration(self, duration):
        if duration>=self.min_duration and duration<=self.max_duration:
            return None, None
        else:
            return None, Response({'error': f"video duration should be in between {self.min_duration}-{self.max_duration} sec"}, status=200)
    


oo = VideoFileOperation()

class UploadVideoView(CustomAPIView):
    """
    Allow users to upload videos with configurable limits of size and duration
    - maximum size: e.g. 5 mb, 25 mb
    - minimum and maximum duration: e.g. 25 secs, 5 secs
    """
    def file_size_check(self, file_obj):
        max_size = 25 * 1024 * 1024  # 25 MB
        if file_obj.size > max_size:
            return None, Response({'error': 'File size exceeds 25 MB limit'}, status=400)
        None, None


    def post(self, req):
        file_obj = req.data.get("file", None)
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=400)
        
        max_size = 25 * 1024 * 1024  # 25 MB
        if file_obj.size > max_size:
            return None, Response({'error': 'File size exceeds 25 MB limit'}, status=400)
        

        # Save file temporarily to analyze it
        temp_file_path = f'media/temp_{file_obj.name}'
        with open(temp_file_path, 'wb+') as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
        
        with ExitStack() as stack:
            stack.callback(partial(os.remove, temp_file_path))
            duration, err = oo.get_video_duration(temp_file_path)
            if err:
                return err
            _, err =  oo.validate_video_duration(duration)
            if err:
                return err
            
            # Save video metadata to database
            video = Video.objects.create(
                file=file_obj,
                size=file_obj.size,
                duration=duration,
            )
            return Response(VideoSerializer(video).data, status=201)

        

class CreateSharedLinkView(CustomAPIView):

    def post(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=404)

        # Get expiry duration from the request (default to 24 hours)
        expiry_hours = int(request.data.get('expiry_hours', 24))
        expiry_time = datetime.now() + timedelta(hours=expiry_hours)

        # Create a shared link
        shared_link = SharedLink.objects.create(video=video, expiry_time=expiry_time)
        serializer = SharedLinkSerializer(shared_link)

        return Response(serializer.data, status=201)


class AccessSharedLinkView(CustomAPIView):
    def get(self, request, token):
        try:
            shared_link = SharedLink.objects.get(token=token)
        except SharedLink.DoesNotExist:
            return Response({'error': 'Invalid or expired link'}, status=404)

        # Check if the link has expired
        if shared_link.is_expired():
            return Response({'error': 'This link has expired'}, status=410)

        # Serve the video file
        video_file = shared_link.video.file
        return FileResponse(video_file, as_attachment=True)


class MergeVideoView(CustomAPIView):

    def post(self, req):
        return Response({'error': 'No file uploaded'}, status=200)


class TrimVideoView(CustomAPIView):

    def post(self, req):
        return Response({'error': 'No file uploaded'}, status=200)


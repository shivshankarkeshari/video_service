
import os
from datetime import datetime, timedelta
from contextlib import ExitStack
from functools import partial

from django.http import FileResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from .serializer import VideoSerializer, SharedLinkSerializer
from .models import Video, SharedLink
from .utils import video_file_editor


class CustomAPIView(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]


class UploadVideoView(CustomAPIView):
    """
    Allow users to upload videos with configurable limits of size and duration
    - maximum size: e.g. 5 mb, 25 mb
    - minimum and maximum duration: e.g. 25 secs, 5 secs
    """

    def post(self, req):
        file_obj = req.data.get("file", None)
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        max_size = 25 * 1024 * 1024  # 25 MB
        if file_obj.size > max_size:
            return None, Response({'error': 'File size exceeds 25 MB limit'}, status=status.HTTP_400_BAD_REQUEST)
        

        # Save file temporarily to analyze it
        temp_file_path = f'media/temp_{file_obj.name}'
        with open(temp_file_path, 'wb+') as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
        
        with ExitStack() as stack:
            stack.callback(partial(os.remove, temp_file_path))

            duration, err = video_file_editor.get_video_duration(temp_file_path)
            if err:
                return Response(err, status.HTTP_400_BAD_REQUEST)
            
            _, err =  video_file_editor.validate_video_duration(duration)
            if err:
                return Response(err, status.HTTP_400_BAD_REQUEST)
            
            # Save video metadata to database
            video = Video.objects.create(
                file=file_obj,
                size=file_obj.size,
                duration=duration,
                user=req.user
            )
            return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)

 
class GetVideoByIdView(CustomAPIView):
    def get(self, req, video_id):
        try:
            # Fetch the video by ID
            video = Video.objects.get(id=video_id, user=req.user)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

        video_file = video.file
        return FileResponse(video_file, as_attachment=True)

           
class CreateSharedLinkView(CustomAPIView):

    def post(self, req, video_id):
        try:
            video = Video.objects.get(id=video_id, user=req.user)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=404)

        # Get expiry duration from the request (default to 24 hours)
        expiry_hours = int(req.data.get('expiry_hours', 24))
        expiry_time = datetime.now() + timedelta(hours=expiry_hours)

        # Create a shared link
        shared_link = SharedLink.objects.create(video=video, expiry_time=expiry_time)
        serializer = SharedLinkSerializer(shared_link)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccessSharedLinkView(CustomAPIView):
    def get(self, req, token):
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


class TrimVideoView(CustomAPIView):
    def post(self, req, video_id):
        try:
            video = Video.objects.get(id=video_id, user=req.user)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get start and end times from the request
        start_time = float(req.data.get('start_time', 0))
        end_time = float(req.data.get('end_time', video.duration))

        # Validate start and end times
        if start_time < 0 or end_time > video.duration or start_time >= end_time:
            return Response({'error': 'Invalid start or end time'}, status=status.HTTP_400_BAD_REQUEST)

        res, err = video_file_editor.trim_video(video, start_time, end_time)
        
        return Response(res or err, status=status.HTTP_200_OK if not err else status.HTTP_500_INTERNAL_SERVER_ERROR)


class MergeVideosView(CustomAPIView):
    def post(self, req):
        video_ids = req.data.get('video_ids', [])
        if not video_ids or len(video_ids) < 2:
            return Response({'error': 'At least two videos are required for merging'}, status=status.HTTP_400_BAD_REQUEST)

        videos = Video.objects.filter(id__in=video_ids, user=req.user)
        if len(videos) != len(video_ids):
            return Response({'error': 'One or more videos not found'}, status=status.HTTP_404_NOT_FOUND)

        res, err = video_file_editor.merge_video([video.file.path for video in videos], req.user)

        return Response(res or err, status=status.HTTP_200_OK if not err else status.HTTP_500_INTERNAL_SERVER_ERROR)

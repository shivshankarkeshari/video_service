
import os
from django.core.files.base import ContentFile
from io import BytesIO
from moviepy.editor import VideoFileClip, concatenate_videoclips

from .models import Video


class VideoFileEditor:
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
            return None, {'error': f'Error processing video: {str(e)}'}
    
    def validate_video_duration(self, duration):
        if duration>=self.min_duration and duration<=self.max_duration:
            return None, None
        else:
            return None, {'error': f"video duration should be in between {self.min_duration}-{self.max_duration} sec"}

    def trim_video(self, video_obj: Video, start_time: float, end_time: float):
        try:
            # Open video file using moviepy
            video_path = video_obj.file.path
            clip = VideoFileClip(video_path).subclip(start_time, end_time)

            # Save the trimmed video to memory
            output_buffer = BytesIO()
            output_filename = f"trimmed_{os.path.basename(video_obj.file.name)}"
            clip.write_videofile(output_filename, codec="libx264", verbose=False, logger=None)
            clip.close()

            # Save trimmed video as a new Video instance
            trimmed_video = Video.objects.create(
                file=ContentFile(open(output_filename, 'rb').read(), name=output_filename),
                size=os.path.getsize(output_filename),
                duration=end_time - start_time,
                user=video_obj.user
            )

            # Clean up temporary file
            os.remove(output_filename)

            return {'message': 'Video trimmed successfully', 'trimmed_video_id': trimmed_video.id}, None
        except Exception as e:
            return None, {'error': str(e)}

    def merge_video(self, video_file_paths, user):
        try:
            # Load video clips
            video_clips = []
            for path in video_file_paths:
                video_clips.append(VideoFileClip(path))

            # Merge videos
            merged_clip = concatenate_videoclips(video_clips)

            # Save the merged video to memory
            output_buffer = BytesIO()
            output_filename = "merged_video.mp4"
            merged_clip.write_videofile(output_filename, codec="libx264", verbose=False, logger=None)
            merged_clip.close()

            # Save merged video as a new Video instance
            merged_video = Video.objects.create(
                file=ContentFile(open(output_filename, 'rb').read(), name=output_filename),
                size=os.path.getsize(output_filename),
                duration=sum([clip.duration for clip in video_clips]),
                user=user
            )

            # Clean up temporary file
            os.remove(output_filename)

            return {'message': 'Videos merged successfully', 'merged_video_id': merged_video.id}, None
        except Exception as e:
            return None, {'error': str(e)}


video_file_editor = VideoFileEditor()

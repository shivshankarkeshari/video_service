

from rest_framework import serializers
from .models import Video, SharedLink

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'



class SharedLinkSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()

    class Meta:
        model = SharedLink
        fields = ['id', 'video', 'token', 'expiry_time', 'link']

    def get_link(self, obj):
        return f"/video/shared/{obj.token}/"
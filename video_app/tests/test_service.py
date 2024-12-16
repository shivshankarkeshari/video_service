

from django.test import SimpleTestCase, Client, TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.urls import reverse
import os
from video_app.models import *
from rest_framework import status

class TestVideoService(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shiv',
                                             email='shiv@gmail.com',
                                             password='1234567890')
        Token.objects.create(user=self.user)
        self.client = Client()
        
        # one video upload to test cases where we need to upload video before run
        self.file_path = "./video_app/tests/sample_960x540.mp4"
        self.test_upload_video(self.file_path)
        self.video_obj = Video.objects.first()


    def test_upload_video(self, file_path=None):
        res_without_file = self.client.post(
            path=reverse('upload-video'),
            headers={"Authorization": f"Token {self.user.auth_token.key}"}
        )
        assert (res_without_file.status_code==status.HTTP_400_BAD_REQUEST and res_without_file.data=={'error': 'No file uploaded'})

        if not file_path:
            # mp4 file 1.3MB
            file_path = "./video_app/tests/sample_960x540.mp4"
        res_with_file = self.client.post(
            path=reverse('upload-video'),
            headers={"Authorization": f"Token {self.user.auth_token.key}"},
            data={"file": open(file_path, "rb")}
        )
        assert res_with_file.status_code==status.HTTP_201_CREATED
        assert res_with_file.data.get("size", 0)==os.path.getsize(file_path)
    

    def test_get_video_by_id(self):
        # not allocated id check
        res = self.client.get(
            path=reverse('get-video-by-id', kwargs={"video_id":3211}),
            headers={"Authorization": f"Token {self.user.auth_token.key}"},
        )
        assert res.status_code==404

        video_obj = Video.objects.first()
        if not video_obj:
            assert False
        res = self.client.get(
            path=reverse('get-video-by-id', kwargs={"video_id": video_obj.id}),
            headers={"Authorization": f"Token {self.user.auth_token.key}"},
        )

        # status check
        assert res.status_code==status.HTTP_200_OK 

        if res.status_code==status.HTTP_200_OK:
            #file size check      
            with open('./response.mp4', 'wb+') as destination:
                for chunk in res.streaming_content:
                    destination.write(chunk)
            assert os.path.getsize("./response.mp4")==os.path.getsize(self.file_path)  
            os.remove('./response.mp4')     
    

    def test_create_shared_link(self):
        video_obj = Video.objects.first()
        res = self.client.post(
            path=reverse('create-shared-link', kwargs={"video_id": video_obj.id}),
            headers={"Authorization": f"Token {self.user.auth_token.key}"}
        )
        assert res.status_code==status.HTTP_201_CREATED
        if res.status_code==status.HTTP_201_CREATED:
            token = res.data.get("token", None)
            if not token:
                assert False
    
    def test_get_shared_video(self):
        self.test_create_shared_link()
        shared_video_obj = SharedLink.objects.first()
        if not shared_video_obj:
            assert False

        res = self.client.get(
            path=reverse('access-shared-link', kwargs={"token": str(shared_video_obj.token)}),
            headers={"Authorization": f"Token {self.user.auth_token.key}"}
        )

        assert res.status_code==status.HTTP_200_OK

    
    def test_trim_video(self):
        start_time = 2
        end_time = 10
        res = self.client.post(
            path=reverse('trim-video', kwargs={"video_id": self.video_obj.id}),
            headers={"Authorization": f"Token {self.user.auth_token.key}"},
            data={
                    "start_time": start_time,
                    "end_time": end_time
                }
        )
        assert res.status_code==200
        if res.status_code==200:
            new_video_id = res.data.get("trimmed_video_id", None)
            if not new_video_id:
                assert False
            assert Video.objects.get(id=new_video_id).duration==end_time-start_time
    
    def test_merge_video(self):
        assert 1==1


from django.urls import path, include

from . import views


"""
3. Allow trimming a video
    - for a given video clip (previously uploaded) shorten it from start or end
4. Allow merging video clips
    - for a given list of video clips (previously uploaded) stitch them into a single video file
5. Allow link sharing with time-based expiry (assume the expiry time)
6. Write unit and e2e tests. Add the command for test coverage.
7. Use SQLite as the database (commit it to the repo)
8. API Docs as Swagger Endpoint or Postman Collection json 

"""
urlpatterns = [
    path("upload", views.UploadVideoView.as_view()),
    path("merge", views.MergeVideoView.as_view()),
    path("trim", views.TrimVideoView.as_view()),
    path('shared/create/<int:video_id>/', views.CreateSharedLinkView.as_view(), name='create-shared-link'),
    path('shared/<uuid:token>/', views.AccessSharedLinkView.as_view(), name='access-shared-link'),
]

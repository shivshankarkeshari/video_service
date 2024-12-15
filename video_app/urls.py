
from django.urls import path, include

from . import views


urlpatterns = [
    path("upload", views.UploadVideoView.as_view()),
    path('<int:video_id>/', views.GetVideoByIdView.as_view(), name='get-video-by-id'),
    path("merge", views.MergeVideosView.as_view(), name='merge-videos'),
    path('trim/<int:video_id>/', views.TrimVideoView.as_view(), name='trim-video'),
    path('shared/create/<int:video_id>/', views.CreateSharedLinkView.as_view(), name='create-shared-link'),
    path('shared/<uuid:token>/', views.AccessSharedLinkView.as_view(), name='access-shared-link'),
]

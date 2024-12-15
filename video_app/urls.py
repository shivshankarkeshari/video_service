
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.VideoUploadView.as_view()),
]

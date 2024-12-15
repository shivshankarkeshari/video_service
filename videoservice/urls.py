

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("video/", include("video_app.urls")),
    # path("account/", include("account.urls")),
]

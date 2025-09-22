from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = "core"
router = DefaultRouter()

import content.urls

urlpatterns = [
    path("", include(router.urls)),
]

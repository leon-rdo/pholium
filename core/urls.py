from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ImageViewSet

app_name = "core"
router = DefaultRouter()

router.register(r"images", ImageViewSet, basename="image")

import content.urls
import portfolio.urls

urlpatterns = [
    path("", include(router.urls)),
]

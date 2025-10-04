from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ImageViewSet

app_name = "core"
router = DefaultRouter()

router.register(r"images", ImageViewSet, basename="image")

from content.urls import content_router
from portfolio.urls import portfolio_router
from blog.urls import blog_router

router.registry.extend(content_router.registry)
router.registry.extend(portfolio_router.registry)
router.registry.extend(blog_router.registry)

urlpatterns = [
    path("", include(router.urls)),
]

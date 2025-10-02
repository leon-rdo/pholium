from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ImageViewSet

app_name = "core"
router = DefaultRouter()

router.register(r"images", ImageViewSet, basename="image")

# Importar e estender routers de outros apps
from content.urls import content_router
from portfolio.urls import portfolio_router

router.registry.extend(content_router.registry)
router.registry.extend(portfolio_router.registry)

urlpatterns = [
    path("", include(router.urls)),
]

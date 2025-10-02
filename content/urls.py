from rest_framework.routers import DefaultRouter

from content.views import (
    SiteSettingViewSet,
    ContentBlockViewSet,
    NavigationItemViewSet,
    TestimonialViewSet,
    ContactMessageViewSet,
)

app_name = "content"

content_router = DefaultRouter()
content_router.register(r"site-settings", SiteSettingViewSet)
content_router.register(r"content-blocks", ContentBlockViewSet)
content_router.register(r"navigation-items", NavigationItemViewSet)
content_router.register(r"testimonials", TestimonialViewSet)
content_router.register(r"contact-messages", ContactMessageViewSet)

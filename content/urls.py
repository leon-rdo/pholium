from core.urls import router

from content.views import (
    SiteSettingViewSet,
    ContentBlockViewSet,
    NavigationItemViewSet,
    TestimonialViewSet,
    ContactMessageViewSet,
)

app_name = "content"

router.register(r"site-settings", SiteSettingViewSet)
router.register(r"content-blocks", ContentBlockViewSet)
router.register(r"navigation-items", NavigationItemViewSet)
router.register(r"testimonials", TestimonialViewSet)
router.register(r"contact-messages", ContactMessageViewSet)

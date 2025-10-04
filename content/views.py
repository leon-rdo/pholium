from rest_framework import viewsets

from core.utils.filters import AutoFilterMixin, AutoFilterTranslationMixin

from .models import (
    SiteSetting,
    ContentBlock,
    NavigationItem,
    Testimonial,
    ContactMessage,
)
from .serializers import (
    SiteSettingSerializer,
    ContentBlockSerializer,
    NavigationItemSerializer,
    TestimonialSerializer,
    ContactMessageSerializer,
)


class SiteSettingViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = SiteSetting.objects.all().prefetch_related("translations")
    serializer_class = SiteSettingSerializer


class ContentBlockViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = ContentBlock.objects.all().prefetch_related("translations")
    serializer_class = ContentBlockSerializer


class NavigationItemViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = NavigationItem.objects.all().prefetch_related("translations", "parent")
    serializer_class = NavigationItemSerializer


class TestimonialViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Testimonial.objects.all().prefetch_related("translations")
    serializer_class = TestimonialSerializer


class ContactMessageViewSet(AutoFilterMixin, viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

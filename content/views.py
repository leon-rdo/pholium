from rest_framework import viewsets

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


class SiteSettingViewSet(viewsets.ModelViewSet):
    queryset = SiteSetting.objects.all().prefetch_related("translations")
    serializer_class = SiteSettingSerializer


class ContentBlockViewSet(viewsets.ModelViewSet):
    queryset = ContentBlock.objects.all().prefetch_related("translations")
    serializer_class = ContentBlockSerializer


class NavigationItemViewSet(viewsets.ModelViewSet):
    queryset = NavigationItem.objects.all().prefetch_related("translations", "parent")
    serializer_class = NavigationItemSerializer


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all().prefetch_related("translations")
    serializer_class = TestimonialSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

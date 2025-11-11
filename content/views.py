from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets

from core.permissions import DjangoModelPermissionsOrAnonCreate
from core.utils.filters import AutoFilterMixin, AutoFilterTranslationMixin

from pholium.settings import EMAIL_HOST, DEFAULT_FROM_EMAIL


User = get_user_model()

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
    permission_classes = [DjangoModelPermissionsOrAnonCreate]

    def perform_create(self, serializer):
        """Save the message and send e-mail to superadmins"""
        instance = serializer.save()

        if EMAIL_HOST:
            try:
                self._send_notification_email(instance)
            except Exception as e:
                pass

    def _send_notification_email(self, message):
        """Send HTML e-mail notification to all superusers"""

        superuser_emails = list(
            User.objects.filter(is_superuser=True, is_active=True, email__isnull=False)
            .exclude(email="")
            .values_list("email", flat=True)
        )

        if not superuser_emails:
            return

        context = {
            "message": message,
            "admin_url": f"{self.request.scheme}://{self.request.get_host()}/admin/content/contactmessage/{message.id}/change/",
        }

        subject = _(f"New contact message: {message.subject}")
        html_content = render_to_string(
            "emails/contact_message_notification.html", context
        )

        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=superuser_emails,
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

from rest_framework import serializers

from core.utils.translations import FlattenTranslatedFieldsMixin, TranslationsField

from .models import (
    SiteSetting,
    ContentBlock,
    NavigationItem,
    Testimonial,
    ContactMessage,
)


class SiteSettingSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
    translations = TranslationsField(
        fields=["site_name", "tagline", "bio", "default_title", "default_description"],
        source="*",
        required=False,
    )

    class Meta:
        model = SiteSetting
        fields = [
            "id",
            "logo",
            "default_image",
            "translations",
        ]


class ContentBlockSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
    translations = TranslationsField(
        fields=["text"],
        source="*",
        required=False,
    )

    class Meta:
        model = ContentBlock
        fields = [
            "id",
            "page_name",
            "key",
            "kind",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class NavigationItemSerializer(
    FlattenTranslatedFieldsMixin, serializers.ModelSerializer
):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=NavigationItem.objects.all(), allow_null=True, required=False
    )
    translations = TranslationsField(
        fields=["label", "title", "url"],
        source="*",
        required=False,
    )

    class Meta:
        model = NavigationItem
        fields = [
            "id",
            "parent",
            "order",
            "is_active",
            "menu_key",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TestimonialSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
    translations = TranslationsField(
        fields=["author_role", "company", "text"],
        source="*",
        required=False,
    )

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "author_name",
            "photo",
            "order",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ContactMessageSerializer(
    FlattenTranslatedFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "name",
            "email",
            "subject",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

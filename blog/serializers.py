from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.utils.auto_flex_fields_serializer import AutoFlexFieldsSerializer
from core.utils.translations import TranslationsField, FlattenTranslatedFieldsMixin

from .models import (
    Category,
    Series,
    Post,
    PostTag,
    Comment,
    PostReaction,
    PostStatus,
    PostVisibility,
    ReactionType,
)


# ==========================
# Category Serializer
# ==========================
class CategorySerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=[
            "name",
            "slug",
            "description",
            "seo_title",
            "meta_description",
        ],
        source="*",
        required=False,
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "parent",
            "translations",
            "is_active",
            "order",
        ]
        read_only_fields = ["id"]


# ==========================
# Series Serializer
# ==========================
class SeriesSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=[
            "title",
            "slug",
            "description",
            "seo_title",
            "meta_description",
        ],
        source="*",
        required=False,
    )

    class Meta:
        model = Series
        fields = [
            "id",
            "translations",
            "is_active",
        ]
        read_only_fields = ["id"]


# ==========================
# Post Serializer
# ==========================
class PostSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=[
            "title",
            "slug",
            "excerpt",
            "body",
            "seo_title",
            "meta_description",
            "canonical_url",
        ],
        source="*",
        required=False,
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "category",
            "series",
            "status",
            "visibility",
            "published_at",
            "allow_comments",
            "is_pinned",
            "reading_time",
            "view_count",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reading_time",
            "view_count",
            "created_at",
            "updated_at",
        ]

    def validate_status(self, value):
        if value not in dict(PostStatus.choices):
            raise serializers.ValidationError(_("Invalid status."))
        return value

    def validate_visibility(self, value):
        if value not in dict(PostVisibility.choices):
            raise serializers.ValidationError(_("Invalid visibility."))
        return value


# ==========================
# PostTag Serializer
# ==========================
class PostTagSerializer(AutoFlexFieldsSerializer):
    class Meta:
        model = PostTag
        fields = [
            "id",
            "post",
            "tag",
            "order",
        ]
        read_only_fields = ["id"]


# ==========================
# Comment Serializer
# ==========================
class CommentSerializer(AutoFlexFieldsSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "parent",
            "user",
            "guest_name",
            "guest_email",
            "guest_website",
            "content",
            "is_approved",
            "ip_address",
            "user_agent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "ip_address",
            "user_agent",
        ]

    def validate(self, attrs):
        # Validate that either user or guest info is provided
        user = attrs.get("user")
        guest_name = attrs.get("guest_name")

        if not user and not guest_name:
            raise serializers.ValidationError(
                _("Either 'user' or 'guest_name' must be provided.")
            )

        # If guest, require email
        if not user and not attrs.get("guest_email"):
            raise serializers.ValidationError(
                _("Guest email is required for anonymous comments.")
            )

        return attrs


# ==========================
# PostReaction Serializer
# ==========================
class PostReactionSerializer(AutoFlexFieldsSerializer):
    class Meta:
        model = PostReaction
        fields = [
            "id",
            "post",
            "user",
            "reaction",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_reaction(self, value):
        if value not in dict(ReactionType.choices):
            raise serializers.ValidationError(_("Invalid reaction type."))
        return value

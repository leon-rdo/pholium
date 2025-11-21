from django.contrib.auth import get_user_model

from core.utils.auto_flex_fields_serializer import AutoFlexFieldsSerializer
from core.utils.translations import FlattenTranslatedFieldsMixin, TranslationsField

from .models import Skill, Project, Experience, Education, Certificate, Achievement

User = get_user_model()


class SkillSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=["name", "slug"],
        source="*",
        required=False,
    )

    class Meta:
        model = Skill
        fields = [
            "id",
            "translations",
            "level",
            "icon",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CertificateSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=["name", "slug", "issuer", "description"],
        source="*",
        required=False,
    )

    class Meta:
        model = Certificate
        fields = [
            "id",
            "translations",
            "issue_date",
            "expiration_date",
            "credential_id",
            "credential_url",
            "skills",
            "featured",
            "sort_order",
            "is_expired",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "is_expired"]


class AchievementSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=["title", "slug", "issuer", "description"],
        source="*",
        required=False,
    )

    class Meta:
        model = Achievement
        fields = [
            "id",
            "translations",
            "achievement_type",
            "date",
            "url",
            "position",
            "tags",
            "skills",
            "project",
            "featured",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ProjectSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=["title", "slug", "summary", "description"],
        source="*",
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "translations",
            "start_date",
            "end_date",
            "website_url",
            "repo_url",
            "cover",
            "status",
            "tags",
            "skills",
            "author",
            "featured",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ExperienceSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=["company", "role", "location", "description"],
        source="*",
        required=False,
    )

    class Meta:
        model = Experience
        fields = [
            "id",
            "translations",
            "start_date",
            "end_date",
            "current",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class EducationSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
    translations = TranslationsField(
        fields=["institution", "degree", "description"],
        source="*",
        required=False,
    )

    class Meta:
        model = Education
        fields = [
            "id",
            "translations",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

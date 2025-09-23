from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.utils.translations import FlattenTranslatedFieldsMixin, TranslationsField

from .models import Skill, Category, Project, Experience, Education

User = get_user_model()


class SkillSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
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


class CategorySerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
    translations = TranslationsField(
        fields=["name", "slug"],
        source="*",
        required=False,
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ProjectSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
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
            "category",
            "tags",
            "skills",
            "author",
            "featured",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ExperienceSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
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


class EducationSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
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

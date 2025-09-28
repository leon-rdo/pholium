from django.contrib import admin
from parler.admin import TranslatableAdmin

from core.admin import ImageInline
from .models import Skill, Category, Project, Experience, Education


@admin.register(Skill)
class SkillAdmin(TranslatableAdmin):
    list_display = ("name", "level", "icon", "slug", "created_at", "updated_at")
    search_fields = ("translations__name", "translations__slug")
    ordering = ("translations__name",)

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("translations__name", "translations__slug")
    ordering = ("translations__name",)

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(TranslatableAdmin):
    list_display = (
        "title",
        "status",
        "category",
        "author",
        "featured",
        "sort_order",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "category", "featured")
    search_fields = (
        "translations__title",
        "translations__slug",
        "translations__summary",
        "translations__description",
    )
    filter_horizontal = ("tags", "skills")
    ordering = ("-featured", "sort_order", "-created_at")
    inlines = [ImageInline]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}


@admin.register(Experience)
class ExperienceAdmin(TranslatableAdmin):
    list_display = (
        "company",
        "role",
        "start_date",
        "end_date",
        "current",
        "location",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "translations__company",
        "translations__role",
        "translations__location",
    )
    list_filter = ("current",)
    ordering = ("-start_date",)
    inlines = [ImageInline]


@admin.register(Education)
class EducationAdmin(TranslatableAdmin):
    list_display = (
        "institution",
        "degree",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
    )
    search_fields = ("translations__institution", "translations__degree")
    ordering = ("-start_date",)
    inlines = [ImageInline]

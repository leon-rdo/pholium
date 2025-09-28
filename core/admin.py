from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from .models import Image, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "language", "created_at", "updated_at")
    search_fields = ("name", "slug", "language")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


class ImageInline(GenericTabularInline):
    model = Image
    extra = 1
    fields = ["file", "image_type", "order", "is_featured"]
    readonly_fields = ["thumbnail", "width", "height", "file_size"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("content_type")


@admin.register(Image)
class ImageAdmin(TranslatableAdmin):
    list_display = [
        "thumbnail_preview",
        "get_title",
        "image_type",
        "content_object",
        "is_featured",
        "order",
        "created_at",
    ]
    list_filter = ["image_type", "is_featured", "created_at"]
    search_fields = ["translations__title", "translations__alt_text"]
    readonly_fields = [
        "thumbnail_preview",
        "width",
        "height",
        "file_size",
        "mime_type",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (_("Image Files"), {"fields": ("file", "thumbnail", "thumbnail_preview")}),
        (
            _("Translations"),
            {
                "fields": (
                    "title",
                    "alt_text",
                    "caption",
                    "credits",
                )
            },
        ),
        (
            _("Metadata"),
            {
                "fields": (
                    "image_type",
                    "order",
                    "is_featured",
                    "width",
                    "height",
                    "file_size",
                    "mime_type",
                )
            },
        ),
        (
            _("Related Object"),
            {"fields": ("content_type", "object_id"), "classes": ("collapse",)},
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_title(self, obj):
        return obj.safe_translation_getter("title", any_language=True) or "-"

    get_title.short_description = _("Title")

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.thumbnail.url,
            )
        elif obj.file:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.file.url,
            )
        return "-"

    thumbnail_preview.short_description = _("Preview")

# admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from core.admin import ImageInline

from .models import (
    SiteSetting,
    ContentBlock,
    NavigationItem,
    Testimonial,
    ContactMessage,
)

# =========================
# Reusable actions
# =========================


@admin.action(description=_("Mark as active"))
def mark_active(modeladmin, request, queryset):
    """
    Generic action to set is_active=True on selected objects.
    Attach only to admins of models that actually have `is_active`.
    """
    queryset.update(is_active=True)


@admin.action(description=_("Mark as inactive"))
def mark_inactive(modeladmin, request, queryset):
    """
    Generic action to set is_active=False on selected objects.
    Attach only to admins of models that actually have `is_active`.
    """
    queryset.update(is_active=False)


# =========================
# SiteSetting
# =========================


@admin.register(SiteSetting)
class SiteSettingAdmin(TranslatableAdmin):
    """
    Site-level settings with translatable text fields (name, tagline, SEO defaults, etc.).
    Keep binary/media or structural fields (e.g., logo) outside translations.
    """

    save_on_top = True

    list_display = ["__str__"]
    search_fields = [
        "translations__site_name",
        "translations__tagline",
        "translations__default_title",
        "translations__default_description",
    ]

    fieldsets = (
        (_("Global"), {"fields": ("logo", "default_image")}),
        (
            _("Translations"),
            {
                "fields": (
                    "site_name",
                    "tagline",
                    "bio",
                    "default_title",
                    "default_description",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        if SiteSetting.objects.exists():
            return False
        return super().has_add_permission(request)


# =========================
# ContentBlock
# =========================


@admin.register(ContentBlock)
class ContentBlockAdmin(TranslatableAdmin):
    """
    Arbitrary content blocks identified by (page_name, key) with translatable text.
    Suitable for sections like hero, footer notices, etc.
    """

    save_on_top = True
    list_per_page = 25

    # If your TimeStamped mixin provides these fields, date_hierarchy will work:
    date_hierarchy = "created_at"

    list_display = ["page_name", "key", "kind", "created_at", "updated_at"]
    list_filter = ["page_name", "kind"]
    search_fields = ["page_name", "key", "translations__text"]
    ordering = ["page_name", "key"]

    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (_("Global"), {"fields": ("page_name", "key", "kind")}),
        (_("Translations"), {"fields": ("text",)}),
        (_("Metadata"), {"fields": ("created_at", "updated_at")}),
    )
    inlines = [ImageInline]


# =========================
# NavigationItem
# =========================


@admin.register(NavigationItem)
class NavigationItemAdmin(TranslatableAdmin):
    """
    Navigation items with hierarchical structure and translated label/title/URL.
    """

    save_on_top = True
    list_per_page = 50

    list_display = ["menu_key", "parent", "label", "order", "is_active", "url"]
    list_editable = ["order", "is_active"]
    list_filter = ["menu_key", "is_active", "parent"]
    search_fields = [
        "translations__label",
        "translations__title",
        "translations__url",
        "url",
    ]
    ordering = ["menu_key", "parent__id", "order"]
    raw_id_fields = ["parent"]
    actions = [mark_active, mark_inactive]

    fieldsets = (
        (
            _("Global"),
            {
                "fields": (
                    "menu_key",
                    "parent",
                    "order",
                    "is_active",
                )
            },
        ),
        (
            _("Translations"),
            {
                "fields": (
                    "label",
                    "title",
                    "url",
                )
            },
        ),
    )


# =========================
# Testimonial
# =========================


@admin.register(Testimonial)
class TestimonialAdmin(TranslatableAdmin):
    """
    Testimonials with translatable text/company/role.
    Keep author name, photo, order as global fields.
    """

    save_on_top = True
    list_per_page = 25

    date_hierarchy = "created_at"

    list_display = ["author_name", "order", "created_at"]
    list_editable = ["order"]
    search_fields = [
        "author_name",
        "translations__author_role",
        "translations__company",
        "translations__text",
    ]
    ordering = ["order", "created_at"]

    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (_("Global"), {"fields": ("author_name", "photo", "order")}),
        (_("Translations"), {"fields": ("author_role", "company", "text")}),
        (_("Metadata"), {"fields": ("created_at", "updated_at")}),
    )


# =========================
# ContactMessage (non-translatable)
# =========================


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Simple contact form submissions (status workflow: new -> read -> archived).
    """

    save_on_top = True
    list_per_page = 50

    date_hierarchy = "created_at"

    list_display = ["name", "email", "subject", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    ordering = ["-created_at"]

    readonly_fields = ["created_at", "updated_at"]

    actions = ["mark_as_new", "mark_as_read", "mark_as_archived"]

    @admin.action(description=_("Mark as new"))
    def mark_as_new(self, request, queryset):
        queryset.update(status="new")

    @admin.action(description=_("Mark as read"))
    def mark_as_read(self, request, queryset):
        queryset.update(status="read")

    @admin.action(description=_("Mark as archived"))
    def mark_as_archived(self, request, queryset):
        queryset.update(status="archived")

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from parler.admin import TranslatableAdmin

from .models import Category, Series, Post, PostTag, Comment, PostReaction, PostStatus
from core.admin import ImageInline


# ==========================
# Inlines
# ==========================
class PostTagInline(admin.TabularInline):
    """
    Through inline to order tags on Post admin.
    """

    model = PostTag
    extra = 0
    fields = (
        "tag",
        "order",
    )
    ordering = ("order",)
    autocomplete_fields = ("tag",)


# ==========================
# Useful Filters
# ==========================
class HasParentFilter(admin.SimpleListFilter):
    title = _("Has parent")
    parameter_name = "has_parent"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, qs):
        if self.value() == "yes":
            return qs.exclude(parent__isnull=True)
        if self.value() == "no":
            return qs.filter(parent__isnull=True)
        return qs


class ApprovedFilter(admin.SimpleListFilter):
    title = _("Approved")
    parameter_name = "is_approved"

    def lookups(self, request, model_admin):
        return (
            ("1", _("Approved")),
            ("0", _("Pending/Rejected")),
        )

    def queryset(self, request, qs):
        if self.value() == "1":
            return qs.filter(is_approved=True)
        if self.value() == "0":
            return qs.filter(is_approved=False)
        return qs


# ==========================
# Category
# ==========================
@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("translated_name", "parent", "is_active", "order", "image_count")
    list_editable = (
        "is_active",
        "order",
    )
    list_filter = ("is_active", HasParentFilter)
    search_fields = (
        "translations__name",
        "translations__slug",
        "translations__description",
    )
    inlines = [ImageInline]
    ordering = ("order", "id")

    fieldsets = (
        (_("Basic"), {"fields": ("parent", "is_active", "order")}),
        (
            _("Translations"),
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "seo_title",
                    "meta_description",
                )
            },
        ),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}

    @admin.display(description=_("Name"))
    def translated_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True)

    @admin.display(description=_("Images"))
    def image_count(self, obj):
        return obj.images.count()


# ==========================
# Series
# ==========================
@admin.register(Series)
class SeriesAdmin(TranslatableAdmin):
    list_display = ("translated_title", "is_active", "image_count", "id")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = (
        "translations__title",
        "translations__slug",
        "translations__description",
    )
    inlines = [ImageInline]
    ordering = ("-id",)

    fieldsets = (
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Translations"),
            {
                "fields": (
                    "title",
                    "slug",
                    "description",
                    "seo_title",
                    "meta_description",
                )
            },
        ),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}

    @admin.display(description=_("Title"))
    def translated_title(self, obj):
        return obj.safe_translation_getter("title", any_language=True)

    @admin.display(description=_("Images"))
    def image_count(self, obj):
        return obj.images.count()


# ==========================
# Post
# ==========================
@admin.register(Post)
class PostAdmin(TranslatableAdmin):
    date_hierarchy = "published_at"
    list_display = (
        "translated_title",
        "status",
        "visibility",
        "author",
        "category",
        "series",
        "is_pinned",
        "published_at",
        "reading_time",
        "view_count",
        "comment_count",
        "reaction_count",
    )
    list_filter = (
        "status",
        "visibility",
        "is_pinned",
        "allow_comments",
        ("author", admin.RelatedOnlyFieldListFilter),
        ("category", admin.RelatedOnlyFieldListFilter),
        ("series", admin.RelatedOnlyFieldListFilter),
    )
    list_editable = (
        "status",
        "visibility",
        "is_pinned",
    )
    search_fields = (
        "translations__title",
        "translations__slug",
        "translations__excerpt",
        "translations__body",
        "author__username",
        "author__email",
    )
    inlines = [PostTagInline, ImageInline]
    autocomplete_fields = (
        "author",
        "category",
        "series",
    )
    readonly_fields = ("reading_time", "view_count", "created_at", "updated_at")
    ordering = ("-is_pinned", "-published_at", "-id")

    fieldsets = (
        (
            _("Publishing"),
            {
                "fields": (
                    "status",
                    "visibility",
                    "published_at",
                    "is_pinned",
                    "allow_comments",
                )
            },
        ),
        (_("Relations"), {"fields": ("author", "category", "series")}),
        (
            _("Metrics (auto)"),
            {"fields": ("reading_time", "view_count", "created_at", "updated_at")},
        ),
        (
            _("Translations"),
            {
                "fields": (
                    "title",
                    "slug",
                    "excerpt",
                    "body",
                    "seo_title",
                    "meta_description",
                    "canonical_url",
                )
            },
        ),
    )

    actions = ["make_published", "make_draft"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author", "category", "series").prefetch_related(
            "images", "comments", "reactions"
        )

    @admin.display(description=_("Title"))
    def translated_title(self, obj):
        return obj.safe_translation_getter("title", any_language=True)

    @admin.display(description=_("Comments"))
    def comment_count(self, obj):
        return obj.comments.count()

    @admin.display(description=_("Reactions"))
    def reaction_count(self, obj):
        return obj.reactions.count()

    @admin.action(description=_("Mark selected posts as published (now)"))
    def make_published(self, request, queryset):
        updated = 0
        for post in queryset:
            post.status = PostStatus.PUBLISHED
            post.save()
            updated += 1
        self.message_user(request, _("%d posts published.") % updated)

    @admin.action(description=_("Mark selected posts as draft"))
    def make_draft(self, request, queryset):
        updated = queryset.update(status=PostStatus.DRAFT)
        self.message_user(request, _("%d posts set to draft.") % updated)


# ==========================
# PostTag (through)
# ==========================
@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ("post", "tag", "order")
    list_editable = ("order",)
    ordering = ("post", "order")
    autocomplete_fields = ("post", "tag")
    search_fields = ("post__translations__title", "tag__name")
    list_filter = (("post", admin.RelatedOnlyFieldListFilter),)

    def get_search_fields(self, request):
        return ("post__translations__title", "tag__name")


# ==========================
# Comment
# ==========================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = (
        "post",
        "short_content",
        "user_or_guest",
        "is_approved",
        "parent",
        "created_at",
    )
    list_filter = (
        ApprovedFilter,
        ("post", admin.RelatedOnlyFieldListFilter),
        ("user", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "content",
        "guest_name",
        "guest_email",
        "post__translations__title",
    )
    autocomplete_fields = ("post", "user", "parent")
    readonly_fields = ("created_at", "updated_at", "ip_address", "user_agent")
    actions = ["approve_selected", "reject_selected"]
    ordering = ("created_at",)

    @admin.display(description=_("Author"))
    def user_or_guest(self, obj):
        return obj.user or f"{obj.guest_name} <{obj.guest_email or '-'}>"

    @admin.display(description=_("Content"))
    def short_content(self, obj):
        return (obj.content or "")[:80] + (
            "…" if obj.content and len(obj.content) > 80 else ""
        )

    @admin.action(description=_("Approve selected"))
    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _("%d comments approved.") % updated)

    @admin.action(description=_("Reject (unapprove) selected"))
    def reject_selected(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _("%d comments unapproved.") % updated)


# ==========================
# PostReaction
# ==========================
@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("post", "user", "reaction", "created_at")
    list_filter = (
        "reaction",
        ("post", admin.RelatedOnlyFieldListFilter),
        ("user", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("post__translations__title", "user__username", "user__email")
    autocomplete_fields = ("post", "user")
    ordering = ("-created_at",)

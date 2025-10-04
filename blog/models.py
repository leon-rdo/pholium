from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse

from parler.models import TranslatableModel, TranslatedFields
from parler.managers import TranslatableQuerySet

from core.models import Image, TimeStamped


# ==========================
# Choices / Enums
# ==========================
class PostStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    SCHEDULED = "scheduled", _("Scheduled")
    PUBLISHED = "published", _("Published")
    ARCHIVED = "archived", _("Archived")


class PostVisibility(models.TextChoices):
    PUBLIC = "public", _("Public")
    UNLISTED = "unlisted", _("Unlisted")
    PRIVATE = "private", _("Private")


class ReactionType(models.TextChoices):
    LIKE = "like", _("Like")
    LOVE = "love", _("Love")
    CLAP = "clap", _("Clap")
    FIRE = "fire", _("Fire")
    WOW = "wow", _("Wow")


# ==========================
# Category
# ==========================
class Category(TranslatableModel, models.Model):
    """
    Categorias hierárquicas de posts.
    """

    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=120),
        slug=models.SlugField(_("Slug"), max_length=140),
        description=models.TextField(_("Description"), blank=True),
        seo_title=models.CharField(_("SEO Title"), max_length=160, blank=True),
        meta_description=models.CharField(
            _("Meta Description"), max_length=160, blank=True
        ),
        meta={
            "unique_together": [("language_code", "slug")],
        },
    )

    is_active = models.BooleanField(_("Is active?"), default=True)
    order = models.PositiveIntegerField(_("Order"), default=0)

    images = GenericRelation(
        Image,
        related_query_name="category",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return (
            self.safe_translation_getter("name", any_language=True)
            or f"Category #{self.pk}"
        )

    @property
    def featured_image(self):
        return (
            self.images.filter(is_featured=True)
            .order_by("order", "-created_at")
            .first()
            or self.images.order_by("order", "-created_at").first()
        )


# ==========================
# Series
# ==========================
class Series(TranslatableModel, models.Model):
    """
    Series of posts (e.g., "Django guide in 5 parts").
    """

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=200),
        slug=models.SlugField(_("Slug"), max_length=220),
        description=models.TextField(_("Description"), blank=True),
        seo_title=models.CharField(_("SEO Title"), max_length=160, blank=True),
        meta_description=models.CharField(
            _("Meta Description"), max_length=160, blank=True
        ),
        meta={
            "unique_together": [("language_code", "slug")],
        },
    )
    is_active = models.BooleanField(_("Is active?"), default=True)

    images = GenericRelation(
        Image,
        related_query_name="series",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    class Meta:
        verbose_name = _("Series")
        verbose_name_plural = _("Series")
        ordering = ["-id"]

    def __str__(self):
        return (
            self.safe_translation_getter("title", any_language=True)
            or f"Series #{self.pk}"
        )

    @property
    def featured_image(self):
        return (
            self.images.filter(is_featured=True)
            .order_by("order", "-created_at")
            .first()
            or self.images.order_by("order", "-created_at").first()
        )


# ==========================
# Post QuerySet / Manager
# ==========================
class PostQuerySet(TranslatableQuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            status=PostStatus.PUBLISHED,
            visibility=PostVisibility.PUBLIC,
            published_at__lte=now,
        )

    def scheduled(self):
        now = timezone.now()
        return self.filter(status=PostStatus.SCHEDULED, published_at__gt=now)

    def visible_for_user(self, user):
        if user and user.is_authenticated:
            return self
        return self.exclude(visibility=PostVisibility.PRIVATE)


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


# ==========================
# Post
# ==========================
class Post(TranslatableModel, TimeStamped):
    """
    Main blog post model.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Author"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    series = models.ForeignKey(
        Series,
        verbose_name=_("Series"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )

    status = models.CharField(
        _("Status"), max_length=12, choices=PostStatus.choices, default=PostStatus.DRAFT
    )
    visibility = models.CharField(
        _("Visibility"),
        max_length=10,
        choices=PostVisibility.choices,
        default=PostVisibility.PUBLIC,
    )
    published_at = models.DateTimeField(_("Publish at"), null=True, blank=True)
    allow_comments = models.BooleanField(_("Allow comments?"), default=True)
    is_pinned = models.BooleanField(_("Pin to top?"), default=False)
    reading_time = models.PositiveIntegerField(
        _("Reading time (min)"), default=0, help_text=_("Estimated in minutes")
    )
    view_count = models.PositiveIntegerField(_("Views"), default=0)

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=250),
        slug=models.SlugField(_("Slug"), max_length=270),
        excerpt=models.TextField(_("Excerpt"), blank=True),
        body=models.TextField(_("Body")),
        seo_title=models.CharField(_("SEO Title"), max_length=160, blank=True),
        meta_description=models.CharField(
            _("Meta Description"), max_length=160, blank=True
        ),
        canonical_url=models.URLField(_("Canonical URL"), blank=True),
        meta={
            "unique_together": [("language_code", "slug")],
        },
    )

    tags = models.ManyToManyField(
        "core.Tag", through="PostTag", related_name="posts", blank=True
    )

    images = GenericRelation(
        Image,
        related_query_name="post",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    objects = PostManager()

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ["-is_pinned", "-published_at", "-id"]
        indexes = [
            models.Index(fields=["status", "visibility"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["is_pinned"]),
        ]

    def __str__(self):
        return (
            self.safe_translation_getter("title", any_language=True)
            or f"Post #{self.pk}"
        )

    def get_absolute_url(self):
        return reverse(
            "blog:post-detail",
            kwargs={"slug": self.safe_translation_getter("slug", any_language=True)},
        )

    @property
    def featured_image(self):
        """
        Returns the featured image of the post or the first by order.
        """
        return (
            self.images.filter(is_featured=True)
            .order_by("order", "-created_at")
            .first()
            or self.images.order_by("order", "-created_at").first()
        )

    def save(self, *args, **kwargs):
        # Auto-define published_at when status changes to PUBLISHED without date
        if self.status == PostStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        # Calculate reading time based on word count (average 200 wpm)
        body = self.safe_translation_getter("body", any_language=True) or ""
        words = len(body.split())
        self.reading_time = max(1, round(words / 200)) if words else 0
        super().save(*args, **kwargs)


# ==========================
# PostTag (through)
# ==========================
class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey("core.Tag", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(_("Order"), default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "tag"], name="unique_post_tag"),
        ]
        verbose_name = _("Post Tag")
        verbose_name_plural = _("Post Tags")
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["post", "order"])]

    def __str__(self):
        return f"{self.post.pk} -> {self.tag.pk}"


# ==========================
# Comments (threaded)
# ==========================
class Comment(TimeStamped):
    """
    Simple threaded comments (1 level or N levels).
    """

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments", verbose_name=_("Post")
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("Parent"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments",
        verbose_name=_("User"),
    )

    guest_name = models.CharField(_("Guest name"), max_length=120, blank=True)
    guest_email = models.EmailField(_("Guest email"), blank=True)
    guest_website = models.URLField(_("Guest website"), blank=True)

    content = models.TextField(_("Content"))
    is_approved = models.BooleanField(_("Approved?"), default=True)
    ip_address = models.GenericIPAddressField(_("IP"), null=True, blank=True)
    user_agent = models.CharField(_("User Agent"), max_length=300, blank=True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["is_approved"]),
        ]

    def __str__(self):
        return f"Comment #{self.pk} on Post #{self.post_id}"


# ==========================
# Reactions
# ==========================
class PostReaction(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="reactions", verbose_name=_("Post")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_reactions",
        verbose_name=_("User"),
    )
    reaction = models.CharField(
        _("Reaction"),
        max_length=12,
        choices=ReactionType.choices,
        default=ReactionType.LIKE,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user", "reaction"], name="unique_user_post_reaction"
            ),
        ]
        verbose_name = _("Post Reaction")
        verbose_name_plural = _("Post Reactions")
        indexes = [models.Index(fields=["post", "reaction"])]

    def __str__(self):
        return f"{self.user_id} {self.reaction} {self.post_id}"

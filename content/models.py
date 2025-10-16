from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

from core.models import TimeStamped


class SiteSetting(TranslatableModel):
    logo = models.ImageField(_("Logo"), upload_to="branding/", blank=True)
    default_image = models.ImageField(_("Default Image"), upload_to="seo/", blank=True)

    translations = TranslatedFields(
        site_name=models.CharField(_("Site Name"), max_length=160, blank=True),
        tagline=models.CharField(_("Tagline"), max_length=200, blank=True),
        bio=models.TextField(_("Bio"), blank=True),
        default_title=models.CharField(_("Default Title"), max_length=160, blank=True),
        default_description=models.CharField(
            _("Default Description"), max_length=200, blank=True
        ),
    )

    def __str__(self):
        return (
            self.safe_translation_getter("site_name", any_language=True)
            or "Site Setting"
        )

    class Meta:
        verbose_name = _("Site Setting")
        verbose_name_plural = _("Site Settings")


class ContentBlock(TranslatableModel, TimeStamped):
    page_name = models.CharField(
        _("Page"), max_length=80
    )  # ex.: "home", "projects", "about"
    key = models.CharField(_("Key"), max_length=80)  # ex.: "hero_title", "cta_text"
    kind = models.CharField(
        _("Kind"),
        max_length=20,
        choices=[("text", _("Text")), ("markdown", _("Markdown")), ("html", _("HTML"))],
        default="text",
    )  # "text", "markdown", "html"

    translations = TranslatedFields(
        text=models.TextField(_("Text"), blank=True),
    )
    images = GenericRelation(
        "core.Image", related_query_name="content_blocks", verbose_name=_("Images")
    )

    def __str__(self):
        return f"{self.page_name} - {self.key}"

    class Meta:
        verbose_name = _("Content Block")
        verbose_name_plural = _("Content Blocks")
        constraints = [
            models.UniqueConstraint(
                fields=["page_name", "key"], name="uq_contentblock_page_key"
            )
        ]
        indexes = [models.Index(fields=["page_name"])]


class NavigationItem(TranslatableModel, TimeStamped):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("Parent"),
    )
    order = models.PositiveIntegerField(
        _("Order"), default=0, validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(_("Is active?"), default=True)
    menu_key = models.SlugField(
        _("Menu Key"), max_length=80, default="header", db_index=True
    )

    translations = TranslatedFields(
        label=models.CharField(_("Label"), max_length=160),
        title=models.CharField(_("Title"), max_length=200, blank=True),
        url=models.CharField(_("URL"), max_length=512, blank=True),
    )

    def __str__(self):
        return (
            self.safe_translation_getter("label", any_language=True)
            or f"Item {self.pk}"
        )

    class Meta:
        verbose_name = _("Navigation Item")
        verbose_name_plural = _("Navigation Items")
        ordering = ["menu_key", "parent_id", "order"]


class Testimonial(TranslatableModel, TimeStamped):
    author_name = models.CharField(_("Author's Name"), max_length=160)
    photo = models.ImageField(_("Photo"), upload_to="testimonials/", blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)

    translations = TranslatedFields(
        author_role=models.CharField(_("Author's Role"), max_length=160, blank=True),
        company=models.CharField(_("Company"), max_length=160, blank=True),
        text=models.TextField(_("Text")),
    )

    def __str__(self):
        return (
            self.author_name
            or f"Testimonial {self.pk}"
        )

    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ["order", "created_at"]


class ContactMessage(TimeStamped):
    name = models.CharField(_("Name"), max_length=160)
    email = models.EmailField(_("E-mail"))
    subject = models.CharField(_("Subject"), max_length=160)
    message = models.TextField(_("Message"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=[
            ("new", _("New")),
            ("read", _("Read")),
            ("archived", _("Archived")),
        ],
        default="new",
    )

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ["-created_at"]

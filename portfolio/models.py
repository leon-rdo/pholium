from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from core.models import TimeStamped


class Skill(TranslatableModel, TimeStamped):
    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=80, unique=False),
        slug=models.SlugField(_("Slug"), max_length=100, blank=True, db_index=True),
    )
    level = models.PositiveSmallIntegerField(
        _("Level"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("From 1 to 5"),
    )
    icon = models.CharField(_("Icon (CSS class, etc.)"), max_length=120, blank=True)

    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")

    def save(self, *args, **kwargs):
        if not self.slug and (self.name or ""):
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or ""


class Category(TranslatableModel, TimeStamped):
    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=80, unique=False),
        slug=models.SlugField(_("Slug"), max_length=100, blank=True, db_index=True),
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def save(self, *args, **kwargs):
        if not self.slug and (self.name or ""):
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or ""


class Project(TranslatableModel, TimeStamped):
    DRAFT, PUBLISHED, ARCHIVED = "draft", "published", "archived"
    STATUS_CHOICES = [
        (DRAFT, _("Draft")),
        (PUBLISHED, _("Published")),
        (ARCHIVED, _("Archived")),
    ]

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=160),
        slug=models.SlugField(_("Slug"), max_length=180, blank=True, db_index=True),
        summary=models.TextField(_("Summary"), blank=True),
        description=models.TextField(_("Description"), blank=True),
    )

    start_date = models.DateField(_("Start date"), null=True, blank=True)
    end_date = models.DateField(_("End date"), null=True, blank=True)
    website_url = models.URLField(_("Website URL"), blank=True)
    repo_url = models.URLField(_("Repository URL"), blank=True)
    cover = models.ImageField(
        _("Cover image"), upload_to="projects/covers/", blank=True
    )
    status = models.CharField(
        _("Status"), max_length=12, choices=STATUS_CHOICES, default=DRAFT
    )
    category = models.ForeignKey(
        "portfolio.Category",
        verbose_name=_("Category"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    tags = models.ManyToManyField(
        "core.Tag", verbose_name=_("Tags"), blank=True, related_name="projects"
    )
    skills = models.ManyToManyField(
        "portfolio.Skill", verbose_name=_("Skills"), blank=True, related_name="projects"
    )
    author = models.ForeignKey(
        "auth.User",
        verbose_name=_("Author"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    featured = models.BooleanField(_("Featured"), default=False)
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-featured", "sort_order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug and (self.title or ""):
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or ""


class Experience(TranslatableModel, TimeStamped):
    translations = TranslatedFields(
        company=models.CharField(_("Company"), max_length=160),
        role=models.CharField(_("Role"), max_length=160),
        location=models.CharField(_("Location"), max_length=160, blank=True),
        description=models.TextField(_("Description"), blank=True),
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"), null=True, blank=True)
    current = models.BooleanField(_("Currently working"), default=False)

    class Meta:
        verbose_name = _("Experience")
        verbose_name_plural = _("Experiences")

    def __str__(self):
        company = self.safe_translation_getter("company", any_language=True) or ""
        role = self.safe_translation_getter("role", any_language=True) or ""
        return f"{company} — {role}".strip(" —")


class Education(TranslatableModel, TimeStamped):
    translations = TranslatedFields(
        institution=models.CharField(_("Institution"), max_length=160),
        degree=models.CharField(_("Degree"), max_length=160, blank=True),
        description=models.TextField(_("Description"), blank=True),
    )
    start_date = models.DateField(_("Start date"), null=True, blank=True)
    end_date = models.DateField(_("End date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Education")

    def __str__(self):
        inst = self.safe_translation_getter("institution", any_language=True) or ""
        deg = self.safe_translation_getter("degree", any_language=True) or ""
        return f"{inst} — {deg}".strip(" —")

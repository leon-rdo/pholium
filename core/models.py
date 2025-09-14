from django.db import models
from django.utils.text import slugify

from django.utils.translation import gettext_lazy as _


class TimeStamped(models.Model):
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True


class Tag(TimeStamped):
    name = models.CharField(_("Name"), max_length=50, unique=True)
    slug = models.SlugField(_("Slug"), max_length=60, unique=True, blank=True)
    language = models.CharField(
        _("Language"),
        max_length=5,
        default="en-us",
        help_text=_("e.g., 'en-us', 'pt-br'"),
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]

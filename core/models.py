from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields


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


class ImageType(models.TextChoices):
    """Image types for categorization"""

    COVER = "cover", _("Cover/Featured Image")
    GALLERY = "gallery", _("Gallery Image")
    LOGO = "logo", _("Logo")
    ICON = "icon", _("Icon")
    SCREENSHOT = "screenshot", _("Screenshot")
    CERTIFICATE = "certificate", _("Certificate")
    TEAM = "team", _("Team Photo")
    DOCUMENT = "document", _("Document/PDF Preview")
    OTHER = "other", _("Other")


class Image(TranslatableModel, TimeStamped):
    """
    Generic Image model to associate images with any model via GenericForeignKey.
    Supports metadata, translations, and automatic thumbnail generation.
    """

    # Main image and thumbnail
    file = models.ImageField(
        _("Image File"), upload_to="images/%Y/%m/", help_text=_("Upload image file")
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to="thumbnails/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Auto-generated or custom thumbnail"),
    )

    # Metadados
    image_type = models.CharField(
        _("Image Type"),
        max_length=20,
        choices=ImageType.choices,
        default=ImageType.GALLERY,
    )
    order = models.PositiveIntegerField(
        _("Display Order"), default=0, validators=[MinValueValidator(0)]
    )
    is_featured = models.BooleanField(
        _("Is Featured?"),
        default=False,
        help_text=_("Mark as featured image for the related object"),
    )

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=200, blank=True),
        alt_text=models.CharField(
            _("Alt Text"),
            max_length=255,
            blank=True,
            help_text=_("Alternative text for accessibility"),
        ),
        caption=models.TextField(_("Caption"), blank=True),
        credits=models.CharField(_("Credits/Attribution"), max_length=200, blank=True),
    )

    # Generic Foreign Key to associate with any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content Type"),
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(_("Object ID"), null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Additional metadata
    width = models.PositiveIntegerField(_("Width"), null=True, blank=True)
    height = models.PositiveIntegerField(_("Height"), null=True, blank=True)
    file_size = models.PositiveIntegerField(
        _("File Size (bytes)"), null=True, blank=True
    )
    mime_type = models.CharField(_("MIME Type"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        ordering = ["order", "-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["image_type"]),
            models.Index(fields=["is_featured"]),
        ]

    def __str__(self):
        return (
            self.safe_translation_getter("title", any_language=True)
            or f"Image #{self.pk}"
        )

    def save(self, *args, **kwargs):
        """Auto-populate image metadata on save"""
        if self.file:
            from PIL import Image as PILImage
            import os

            # Get file size
            if hasattr(self.file, "size"):
                self.file_size = self.file.size

            # Get dimensions
            try:
                with PILImage.open(self.file) as img:
                    self.width, self.height = img.size
                    # Auto-generate thumbnail if not exists
                    if not self.thumbnail:
                        self._generate_thumbnail(img)
            except Exception:
                pass

        super().save(*args, **kwargs)

    def _generate_thumbnail(self, img):
        """Generate thumbnail from the main image"""
        from PIL import Image as PILImage
        from io import BytesIO
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import sys

        # Define thumbnail size
        THUMBNAIL_SIZE = (300, 300)

        # Create thumbnail
        img.thumbnail(THUMBNAIL_SIZE, PILImage.LANCZOS)

        # Save thumbnail to BytesIO
        thumb_io = BytesIO()
        img.save(thumb_io, format="JPEG", quality=85)
        thumb_io.seek(0)

        # Create Django file
        thumb_file = InMemoryUploadedFile(
            thumb_io,
            None,
            f"thumb_{self.file.name}",
            "image/jpeg",
            sys.getsizeof(thumb_io),
            None,
        )

        self.thumbnail = thumb_file

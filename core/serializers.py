from rest_framework import serializers

from core.utils.translations import FlattenTranslatedFieldsMixin, TranslationsField
from .models import Image


class ImageSerializer(FlattenTranslatedFieldsMixin, serializers.ModelSerializer):
    translations = TranslationsField(
        fields=["title", "alt_text", "caption", "credits"],
        source="*",
        required=False,
    )

    class Meta:
        model = Image
        fields = [
            "id",
            "file",
            "thumbnail",
            "translations",
            "image_type",
            "order",
            "is_featured",
            "width",
            "height",
            "created_at",
        ]

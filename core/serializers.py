from core.utils.auto_flex_fields_serializer import AutoFlexFieldsSerializer
from core.utils.translations import FlattenTranslatedFieldsMixin, TranslationsField
from .models import Image


class ImageSerializer(FlattenTranslatedFieldsMixin, AutoFlexFieldsSerializer):
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

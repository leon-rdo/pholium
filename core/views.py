from rest_framework import viewsets

from core.utils.filters import AutoFilterTranslationMixin

from .models import Image
from .serializers import ImageSerializer


class ImageViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

from rest_framework import viewsets

from core.utils.filters import AutoFilterTranslationMixin

from .models import (
    Skill,
    Project,
    Experience,
    Education,
)
from .serializers import (
    SkillSerializer,
    ProjectSerializer,
    ExperienceSerializer,
    EducationSerializer,
)


class SkillViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Skill.objects.all().prefetch_related("translations")
    serializer_class = SkillSerializer


class ProjectViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related("translations")
    serializer_class = ProjectSerializer


class ExperienceViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Experience.objects.all().prefetch_related("translations")
    serializer_class = ExperienceSerializer


class EducationViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Education.objects.all().prefetch_related("translations")
    serializer_class = EducationSerializer

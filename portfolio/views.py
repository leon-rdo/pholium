from rest_framework import viewsets

from core.utils.filters import AutoFilterTranslationMixin

from .models import Skill, Project, Experience, Education, Certificate, Achievement

from .serializers import (
    SkillSerializer,
    ProjectSerializer,
    ExperienceSerializer,
    EducationSerializer,
    CertificateSerializer,
    AchievementSerializer,
)


class SkillViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Skill.objects.all().prefetch_related("translations")
    serializer_class = SkillSerializer


class CertificateViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Certificate.objects.all().prefetch_related("translations", "skills")
    serializer_class = CertificateSerializer


class AchievementViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Achievement.objects.all().prefetch_related(
        "translations", "tags", "skills", "project"
    )
    serializer_class = AchievementSerializer


class ProjectViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related("translations")
    serializer_class = ProjectSerializer


class ExperienceViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Experience.objects.all().prefetch_related("translations")
    serializer_class = ExperienceSerializer


class EducationViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Education.objects.all().prefetch_related("translations")
    serializer_class = EducationSerializer

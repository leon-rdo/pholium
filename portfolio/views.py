from rest_framework import viewsets

from .models import (
    Skill,
    Category,
    Project,
    Experience,
    Education,
)
from .serializers import (
    SkillSerializer,
    CategorySerializer,
    ProjectSerializer,
    ExperienceSerializer,
    EducationSerializer,
)


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all().prefetch_related("translations")
    serializer_class = SkillSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related("translations")
    serializer_class = CategorySerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related("translations", "parent")
    serializer_class = ProjectSerializer


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all().prefetch_related("translations")
    serializer_class = ExperienceSerializer


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all().prefetch_related("translations")
    serializer_class = EducationSerializer

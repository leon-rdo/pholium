from core.urls import router

from .views import (
    SkillViewSet,
    CategoryViewSet,
    ProjectViewSet,
    ExperienceViewSet,
    EducationViewSet,
)

app_name = "portfolio"

router.register(r"skills", SkillViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"experiences", ExperienceViewSet)
router.register(r"educations", EducationViewSet)

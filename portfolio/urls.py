from rest_framework.routers import DefaultRouter
from .views import (
    SkillViewSet,
    ProjectViewSet,
    ExperienceViewSet,
    EducationViewSet,
    CertificateViewSet,
    AchievementViewSet,
)

app_name = "portfolio"

portfolio_router = DefaultRouter()
portfolio_router.register(r"skills", SkillViewSet)
portfolio_router.register(r"certificates", CertificateViewSet)
portfolio_router.register(r"achievements", AchievementViewSet)
portfolio_router.register(r"projects", ProjectViewSet)
portfolio_router.register(r"experiences", ExperienceViewSet)
portfolio_router.register(r"educations", EducationViewSet)

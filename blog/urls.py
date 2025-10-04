from rest_framework.routers import DefaultRouter
from blog.views import (
    CategoryViewSet,
    SeriesViewSet,
    PostViewSet,
    PostTagViewSet,
    CommentViewSet,
    PostReactionViewSet,
)

app_name = "blog"

blog_router = DefaultRouter()

blog_router.register(r"post-categories", CategoryViewSet, basename="post-categories")
blog_router.register(r"series", SeriesViewSet)
blog_router.register(r"posts", PostViewSet)
blog_router.register(r"post-tags", PostTagViewSet)
blog_router.register(r"comments", CommentViewSet)
blog_router.register(r"post-reactions", PostReactionViewSet)

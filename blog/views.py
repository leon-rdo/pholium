import logging

from django.utils import timezone
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import CreateOrListReadOnly
from core.utils.filters import AutoFilterMixin, AutoFilterTranslationMixin

from .models import (
    Category,
    Series,
    Post,
    PostTag,
    Comment,
    PostReaction,
    PostStatus,
)
from .serializers import (
    CategorySerializer,
    SeriesSerializer,
    PostSerializer,
    PostTagSerializer,
    CommentSerializer,
    PostReactionSerializer,
)

logger = logging.getLogger(__name__)


class CategoryViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related("translations")
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs


class SeriesViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Series.objects.all().prefetch_related("translations")
    serializer_class = SeriesSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs


class PostViewSet(AutoFilterTranslationMixin, viewsets.ModelViewSet):
    queryset = Post.objects.all().prefetch_related("translations")
    serializer_class = PostSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            qs = qs.published()

        tags = self.request.query_params.get("tags")
        if tags:
            tag_ids = [t.strip() for t in tags.split(",") if t.strip()]
            qs = qs.filter(tags__id__in=tag_ids).distinct()

        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            Post.objects.filter(pk=instance.pk).update(
                view_count=instance.view_count + 1
            )
            instance.refresh_from_db()
            logger.info(
                f"Post view count incremented - ID: {instance.pk}, new count: {instance.view_count}"
            )
        except Exception as e:
            logger.error(
                f"Failed to increment view count for post {instance.pk}: {str(e)}"
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def published(self, request):
        queryset = self.filter_queryset(self.get_queryset().published())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def scheduled(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = self.filter_queryset(Post.objects.scheduled())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        post = self.get_object()
        if post.status == PostStatus.PUBLISHED:
            logger.warning(
                f"Attempted to publish already published post - ID: {pk}, User: {request.user}"
            )
            return Response(
                {"detail": "Post is already published."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post.status = PostStatus.PUBLISHED
        if not post.published_at:
            post.published_at = timezone.now()
        post.save()

        logger.info(f"Post published - ID: {pk}, User: {request.user}")
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        post = self.get_object()
        post.status = PostStatus.ARCHIVED
        post.save()

        logger.info(f"Post archived - ID: {pk}, User: {request.user}")
        serializer = self.get_serializer(post)
        return Response(serializer.data)


class PostTagViewSet(AutoFilterMixin, viewsets.ModelViewSet):
    queryset = PostTag.objects.all()
    serializer_class = PostTagSerializer


class CommentViewSet(AutoFilterMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [CreateOrListReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            qs = qs.filter(is_approved=True)

        return qs

    def perform_create(self, serializer):
        request = self.request
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]

        instance = serializer.save(
            ip_address=ip_address, user_agent=user_agent, is_approved=False
        )
        logger.info(
            f"New comment created - ID: {instance.pk}, Post: {instance.post_id}, IP: {ip_address}"
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment = self.get_object()
        comment.is_approved = True
        comment.save()

        logger.info(f"Comment approved - ID: {pk}, User: {request.user}")
        serializer = self.get_serializer(comment)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment = self.get_object()
        comment.is_approved = False
        comment.save()

        logger.info(f"Comment rejected - ID: {pk}, User: {request.user}")
        serializer = self.get_serializer(comment)
        return Response(serializer.data)


class PostReactionViewSet(AutoFilterMixin, viewsets.ModelViewSet):
    queryset = PostReaction.objects.all()
    serializer_class = PostReactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        post_id = request.data.get("post")
        reaction_type = request.data.get("reaction")

        if not post_id or not reaction_type:
            return Response(
                {"detail": "Both 'post' and 'reaction' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reaction = PostReaction.objects.get(
                post_id=post_id, user=request.user, reaction=reaction_type
            )
            reaction.delete()
            logger.info(
                f"Reaction removed - Post: {post_id}, User: {request.user}, Type: {reaction_type}"
            )
            return Response(
                {"detail": "Reaction removed.", "added": False},
                status=status.HTTP_200_OK,
            )
        except PostReaction.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            logger.info(
                f"Reaction added - Post: {post_id}, User: {request.user}, Type: {reaction_type}"
            )
            return Response(
                {"detail": "Reaction added.", "added": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

    @action(detail=False, methods=["get"], url_path="summary/(?P<post_id>[^/.]+)")
    def summary(self, request, post_id=None):
        reactions = (
            PostReaction.objects.filter(post_id=post_id)
            .values("reaction")
            .annotate(count=Count("id"))
        )

        summary = {r["reaction"]: r["count"] for r in reactions}
        total = sum(summary.values())

        return Response({"post": post_id, "total": total, "reactions": summary})

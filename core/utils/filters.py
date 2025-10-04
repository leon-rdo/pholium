from django.db import models
from django.db.models import Exists, OuterRef
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.utils.translation import get_language
from django_filters import rest_framework as filters
from django_filters import FilterSet


class AutoFilterMixin:
    """Automatically applies django-filter to all filterable model fields."""

    filter_backends = [filters.DjangoFilterBackend]
    auto_filter_exclude = []
    auto_filter_include = []

    NON_FILTERABLE_FIELDS = (
        models.BinaryField,
        models.FileField,
        models.ImageField,
        GenericRelation,
        GenericForeignKey,
    )

    @classmethod
    def _get_filterable_fields(cls, model):
        """Return filterable field names for a model."""
        filterable = []
        for field in model._meta.get_fields():
            name = field.name
            if name in cls.auto_filter_include:
                filterable.append(name)
                continue
            if (
                name in cls.auto_filter_exclude
                or isinstance(field, (GenericRelation, GenericForeignKey))
                or not hasattr(field, "get_internal_type")
                or isinstance(field, cls.NON_FILTERABLE_FIELDS)
                or (field.auto_created and field.is_relation)
            ):
                continue
            filterable.append(name)
        return filterable

    @classmethod
    def _create_filterset_class(cls, model):
        """Create a FilterSet class dynamically for the given model."""
        fields = cls._get_filterable_fields(model)
        overrides = {}
        for name in fields:
            try:
                f = model._meta.get_field(name)
                if isinstance(f, (models.CharField, models.TextField)):
                    lookups = ["exact", "icontains", "istartswith"]
                elif isinstance(
                    f, (models.IntegerField, models.FloatField, models.DecimalField)
                ):
                    lookups = ["exact", "gte", "lte", "gt", "lt"]
                elif isinstance(f, (models.DateField, models.DateTimeField)):
                    lookups = ["exact", "gte", "lte", "year", "month", "day"]
                elif isinstance(f, models.BooleanField):
                    lookups = ["exact"]
                elif f.is_relation:
                    lookups = ["exact", "in"]
                else:
                    lookups = ["exact"]
                overrides[name] = lookups
            except Exception:
                overrides[name] = ["exact"]

        meta = type("Meta", (), {"model": model, "fields": overrides})
        return type(f"{model.__name__}AutoFilterSet", (FilterSet,), {"Meta": meta})

    def get_queryset(self):
        """Ensure filterset_class is generated for the current model."""
        queryset = super().get_queryset()
        if not getattr(self, "filterset_class", None):
            self.filterset_class = self._create_filterset_class(queryset.model)
        return queryset

    def filter_queryset(self, queryset):
        """Ensure translated field filters apply on the same translation row."""
        model = queryset.model
        translation_model = self._get_translation_model(model)
        if not translation_model:
            return super().filter_queryset(queryset)

        all_languages = str(
            self.request.query_params.get(self.all_languages_param, "")
        ).lower() in {"true", "1", "yes"}

        lang_overridden = any(
            k.startswith("translations__language_code")
            for k in self.request.query_params.keys()
        )

        translation_lookups = {}
        has_translation_filter = False
        for key, value in self.request.query_params.items():
            if not key.startswith("translations__") or key.startswith(
                "translations__language_code"
            ):
                continue
            has_translation_filter = True
            lookup = key.split("translations__", 1)[1]
            if lookup.endswith("__in"):
                value = [v for v in value.split(",") if v]
            translation_lookups[lookup] = value

        apply_exists = (
            has_translation_filter and not all_languages and not lang_overridden
        )
        if apply_exists:
            fk_to_parent = None
            for f in translation_model._meta.get_fields():
                if (
                    getattr(f, "is_relation", False)
                    and getattr(f, "related_model", None) is model
                    and getattr(f, "many_to_one", False)
                ):
                    fk_to_parent = f.name
                    break
            if fk_to_parent:
                current_language = get_language()
                subfilters = {
                    fk_to_parent: OuterRef("pk"),
                    "language_code": current_language,
                }
                subfilters.update(translation_lookups)
                sub_qs = translation_model.objects.filter(**subfilters).values("pk")
                queryset = queryset.filter(Exists(sub_qs))

        queryset = super().filter_queryset(queryset)
        if apply_exists and has_translation_filter:
            queryset = queryset.distinct()
        return queryset


class AutoFilterTranslationMixin(AutoFilterMixin):
    """Extends AutoFilterMixin to support translated fields."""

    DEFAULT_TRANSLATION_FIELDS = [
        "title",
        "name",
        "description",
        "content",
        "slug",
        "meta_description",
        "excerpt",
        "subtitle",
    ]

    auto_translation_fields = []
    all_languages_param = "all_languages"

    @classmethod
    def _get_translation_model(cls, model):
        """Detect the related translation model."""
        for rel in model._meta.related_objects:
            if "translation" in rel.name.lower():
                return rel.related_model
        return None

    @classmethod
    def _get_translatable_fields(cls, translation_model):
        """Return translation model fields that should be filterable."""
        if not translation_model:
            return []
        result = []
        candidates = cls.DEFAULT_TRANSLATION_FIELDS + cls.auto_translation_fields
        for f in translation_model._meta.get_fields():
            if isinstance(f, cls.NON_FILTERABLE_FIELDS) or (
                f.auto_created and f.is_relation
            ):
                continue
            if f.name == "language_code" or f.name in candidates:
                result.append(f.name)
        return result

    @classmethod
    def _create_filterset_class(cls, model):
        """Create FilterSet including translated fields."""
        base = super()._create_filterset_class(model)
        translation_model = cls._get_translation_model(model)
        if not translation_model:
            return base

        translatable = cls._get_translatable_fields(translation_model)
        if not translatable:
            return base

        translation_filters = {}
        for name in translatable:
            try:
                f = translation_model._meta.get_field(name)
                field_name = f"translations__{name}"
                if isinstance(f, (models.CharField, models.TextField)):
                    if name == "language_code":
                        translation_filters[field_name] = ["exact", "in"]
                    else:
                        translation_filters[field_name] = [
                            "exact",
                            "icontains",
                            "istartswith",
                        ]
                elif isinstance(f, (models.IntegerField, models.FloatField)):
                    translation_filters[field_name] = ["exact", "gte", "lte"]
                elif isinstance(f, models.BooleanField):
                    translation_filters[field_name] = ["exact"]
                else:
                    translation_filters[field_name] = ["exact"]
            except Exception:
                continue

        fields = base.Meta.fields.copy()
        fields.update(translation_filters)
        meta = type("Meta", (), {"model": model, "fields": fields})
        return type(
            f"{model.__name__}AutoTranslationFilterSet", (FilterSet,), {"Meta": meta}
        )

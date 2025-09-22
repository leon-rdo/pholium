from django.conf import settings
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from parler.utils.context import switch_language


# ---------------------------------------------------------------------
# 🔧 Language utilities + automatic discovery of translated fields
# ---------------------------------------------------------------------


def _normalize_lang(code: str | None) -> str:
    return (code or "").lower().replace("_", "-")


def _pick_language(request, instance) -> str | None:
    # Priority: ?lang=  >  X-Language  >  Accept-Language
    lang = None
    if request is not None:
        lang = request.query_params.get("lang") or request.headers.get("X-Language")
        if not lang:
            lang = get_language_from_request(request)

    available = {_normalize_lang(c) for c in instance.get_available_languages()}
    lang = _normalize_lang(lang)

    if lang in available:
        return lang
    if "-" in lang and lang.split("-")[0] in available:
        return lang.split("-")[0]

    default_lang = _normalize_lang(
        getattr(
            settings,
            "PARLER_DEFAULT_LANGUAGE_CODE",
            getattr(settings, "LANGUAGE_CODE", "en"),
        )
    )
    if default_lang in available:
        return default_lang

    return next(iter(available), None)


def _translated_field_names_from_instance(instance) -> tuple[str, ...]:
    # Parler lists translated fields here:
    # model._parler_meta.get_all_fields()
    return tuple(
        instance._parler_meta.get_all_fields()
    )  # names like 'title', 'text', etc.


# (ref.: usage of get_all_fields in Parler itself)
# ---------------------------------------------------------------------


class TranslationsField(serializers.Field):
    """
    Allows sending/editing translations in the format:
    {
        "pt-br": {"field1": "...", "field2": "..."},
        "en-us": {"field1": "...", "field2": "..."}
    }
    'fields' is optional: if omitted, it is discovered automatically.
    """

    def __init__(self, *, fields=None, **kwargs):
        self.translation_fields = tuple(fields) if fields else None
        super().__init__(**kwargs)

    def _ensure_fields(self, instance_or_parent_model):
        if self.translation_fields is not None:
            return
        # Discover the list at runtime:
        # - on output, we have the instance -> take from instance._parler_meta
        # - on input, we only have the serializer -> take from Meta.model._parler_meta
        if hasattr(instance_or_parent_model, "_parler_meta"):
            self.translation_fields = tuple(
                instance_or_parent_model._parler_meta.get_all_fields()
            )
        else:
            model = getattr(getattr(self, "parent", None), "Meta", None).model
            self.translation_fields = tuple(model._parler_meta.get_all_fields())

    # source='*' sends the entire model instance to the field
    def to_representation(self, instance):
        self._ensure_fields(instance)
        out = {}
        for tr in instance.translations.all():
            data = {}
            for f in self.translation_fields:
                data[f] = getattr(tr, f, None)
            out[tr.language_code] = data
        return out

    def to_internal_value(self, data):
        self._ensure_fields(None)
        if data is None:
            return {"_translations": {}}
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                _("The 'translations' field must be an object.")
            )

        cleaned = {}
        for lang_code, values in data.items():
            if not isinstance(values, dict):
                raise serializers.ValidationError(
                    _("Translation for '") + {lang_code} + _("' must be an object.")
                )
            entry = {}
            for f in self.translation_fields:
                if f in values:
                    entry[f] = values[f]
            cleaned[lang_code] = entry
        return {"_translations": cleaned}


class FlattenTranslatedFieldsMixin:
    """
    Injects translated fields at the ROOT of the JSON (a single, negotiated language)
    and removes 'translations' from the output.
    No need to list fields: they are discovered automatically from Parler.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("translations", None)

        request = self.context.get("request") if hasattr(self, "context") else None
        lang = _pick_language(request, instance)
        if not lang:
            return data

        # Get values only for the selected language
        # (field names come from Parler)
        names = _translated_field_names_from_instance(instance)
        with switch_language(instance, lang):
            for f in names:
                data[f] = getattr(instance, f, None)

        # If you want to expose the resolved language, uncomment:
        # data["language"] = lang
        return data

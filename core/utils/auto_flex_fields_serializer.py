from rest_flex_fields import FlexFieldsModelSerializer
from django.utils.functional import cached_property


class AutoFlexFieldsSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = None

    @cached_property
    def expandable_fields(self):
        model = self.Meta.model
        expandable = {}
        if not model:
            return expandable
        for field in model._meta.get_fields():
            if field.is_relation and field.related_model:
                related_model = field.related_model
                serializer_name = f"{related_model.__name__}Serializer"
                serializer_path = (
                    f"{related_model._meta.app_label}.serializers.{serializer_name}"
                )
                is_many = field.many_to_many or field.one_to_many
                try:
                    from django.utils.module_loading import import_string

                    import_string(serializer_path)
                    expandable[field.name] = (serializer_path, {"many": is_many})
                except ImportError:
                    pass
        return expandable

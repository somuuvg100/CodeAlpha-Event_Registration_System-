from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = 'events'

    def ready(self):
        try:
            from rest_framework import serializers
            from rest_framework.utils import encoders
            from django_mongodb_backend.fields import ObjectIdAutoField, ObjectIdField
            from bson.objectid import ObjectId

            serializers.ModelSerializer.serializer_field_mapping[ObjectIdAutoField] = serializers.CharField
            serializers.ModelSerializer.serializer_field_mapping[ObjectIdField] = serializers.CharField

            orig_to_rep = serializers.PrimaryKeyRelatedField.to_representation
            def mongo_to_rep(self, value):
                pk = orig_to_rep(self, value)
                return str(pk) if isinstance(pk, ObjectId) else pk
            serializers.PrimaryKeyRelatedField.to_representation = mongo_to_rep

            orig_default = encoders.JSONEncoder.default
            def mongo_encoder_default(self, obj):
                if isinstance(obj, ObjectId):
                    return str(obj)
                return orig_default(self, obj)
            encoders.JSONEncoder.default = mongo_encoder_default
        except ImportError:
            pass

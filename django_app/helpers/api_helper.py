from rest_framework import serializers
from drf_yasg import openapi

def get_serializer_schema(serializer):
    
    properties = {}
    for field_name, field in serializer().fields.items():
        if isinstance(field, serializers.ModelSerializer):
            properties[field_name] = get_serializer_schema(field.__class__)
        else:
            properties[field_name] = openapi.Schema(type=openapi.TYPE_STRING)  # Or use appropriate types
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties
    )


def get_serializer_schema_err(serializer):
    properties = {}
    for field_name, field in serializer().fields.items():
        if isinstance(field, serializers.ModelSerializer):
            properties[field_name] = get_serializer_schema_err(field.__class__)
        else:
            properties[field_name] = openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))  # Or use appropriate types
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties
    )
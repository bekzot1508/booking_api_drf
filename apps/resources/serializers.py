from rest_framework import serializers


class ResourceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class ResourceUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)


class ResourceOutSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    owner_id = serializers.UUIDField()
    created_at = serializers.DateTimeField()

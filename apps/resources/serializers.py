from rest_framework import serializers


class ResourceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

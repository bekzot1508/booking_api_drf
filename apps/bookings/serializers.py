from rest_framework import serializers
from .models import Booking


class BookingListItemSerializer(serializers.ModelSerializer):
    resource_id = serializers.UUIDField(source="resource.id", read_only=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "resource_id",
            "user_id",
            "start_at",
            "end_at",
            "status",
            "created_at",
        ]

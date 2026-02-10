import uuid
from django.db import models
from django.conf import settings


class BookingStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CANCELLED = "cancelled", "Cancelled"


class Booking(models.Model):
    """
    Booking interval: [start_at, end_at)
    status: active/cancelled
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resource = models.ForeignKey(
        "resources.Resource",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    status = models.CharField(
        max_length=16,
        choices=BookingStatus.choices,
        default=BookingStatus.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["resource", "status", "start_at", "end_at"]),
        ]

    def __str__(self):
        return f"{self.resource_id} {self.start_at} - {self.end_at} ({self.status})"

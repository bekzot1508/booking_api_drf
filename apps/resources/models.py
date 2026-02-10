import uuid
from django.db import models
from django.conf import settings


class Resource(models.Model):
    """
    Book qilinadigan obyekt: xona/usta/meeting-room.
    owner — resurs egasi (admin/owner create qiladi).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_resources",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("owner", "name")]  # optional: owner ichida nom takrorlanmasin

    def __str__(self):
        return self.name

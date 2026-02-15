from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from common.exceptions import ValidationError, BusinessRuleViolation, PermissionDenied
from apps.resources.models import Resource
from .models import Booking, BookingStatus
from .selectors import has_overlap


MIN_DURATION = timedelta(minutes=15)


def create_booking(*, user, resource_id: str, start_at, end_at) -> Booking:
    """
    Use-case:
    - validate time
    - prevent overlap
    - create booking safely (transaction + locking)

    Race condition note:
    We lock the Resource row so that two concurrent bookings for the same resource
    can't both pass the overlap check at the same time.
    """
    if start_at >= end_at:
        raise ValidationError("start_at must be < end_at")

    if (end_at - start_at) < MIN_DURATION:
        raise ValidationError(
            "Booking duration is too short",
            details={"min_duration_minutes": 15},
        )

    # Optional: disallow booking in the past (ko‘pincha kerak bo‘ladi)
    if start_at < timezone.now():
        raise ValidationError("start_at cannot be in the past")

    with transaction.atomic():
        # 🔒 Lock resource row (per-resource serialization)
        resource = (
            Resource.objects.select_for_update()
            .only("id")
            .get(id=resource_id)
        )

        if has_overlap(resource_id=str(resource.id), start_at=start_at, end_at=end_at):
            raise BusinessRuleViolation(
                "This resource already has an active booking in the given time range.",
                details={
                    "resource_id": str(resource.id),
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                },
            )

        booking = Booking.objects.create(
            resource_id=resource.id,
            user=user,
            start_at=start_at,
            end_at=end_at,
            status=BookingStatus.ACTIVE,
        )

    return booking


def cancel_booking(*, user, booking_id: str) -> Booking:
    """
    Cancel use-case:
    - lock booking row
    - permission: owner or admin
    - state: only active can be cancelled
    """
    with transaction.atomic():
        booking = (
            Booking.objects.select_for_update()
            .select_related("user")
            .get(id=booking_id)
        )

        is_admin = bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
        is_owner = (str(booking.user_id) == str(user.id))

        if not (is_owner or is_admin):
            raise PermissionDenied("You don't have permission to cancel this booking.")

        if booking.status == BookingStatus.CANCELLED:
            raise BusinessRuleViolation("Booking is already cancelled.")

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=["status", "cancelled_at"])

    return booking


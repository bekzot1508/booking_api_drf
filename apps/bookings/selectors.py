from django.db.models import QuerySet
from django.utils.dateparse import parse_datetime

from common.exceptions import ValidationError
from .models import Booking, BookingStatus
from datetime import datetime


def _parse_dt(value: str, field_name: str):
    if not value:
        return None
    dt = parse_datetime(value)
    if dt is None:
        raise ValidationError(
            "Invalid datetime format",
            details={field_name: "Use ISO format, e.g. 2026-02-09T10:00:00Z"},
        )
    return dt


def list_bookings(
    *,
    resource_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    status: str | None = None,
) -> QuerySet:
    """
    All read/query logic lives here (selector pattern).
    Returned queryset is composable and easy to test.
    """
    qs = Booking.objects.select_related("resource", "user").all()

    if resource_id:
        qs = qs.filter(resource_id=resource_id)

    df = _parse_dt(date_from, "date_from")
    dt = _parse_dt(date_to, "date_to")

    if df and dt and df > dt:
        raise ValidationError("date_from must be <= date_to")

    # interval filtering: booking intersects [date_from, date_to]
    # good default for "show bookings within range"
    if df:
        qs = qs.filter(end_at__gt=df)
    if dt:
        qs = qs.filter(start_at__lt=dt)

    if status:
        if status not in (BookingStatus.ACTIVE, BookingStatus.CANCELLED):
            raise ValidationError("Invalid status", details={"status": "active|cancelled"})
        qs = qs.filter(status=status)

    return qs.order_by("start_at", "created_at")


def has_overlap(*, resource_id: str, start_at: datetime, end_at: datetime) -> bool:
    """
    Overlap exists if:
      new_start < existing_end AND new_end > existing_start
    Only checks ACTIVE bookings.
    """
    return Booking.objects.filter(
        resource_id=resource_id,
        status=BookingStatus.ACTIVE,
        start_at__lt=end_at,
        end_at__gt=start_at,
    ).exists()

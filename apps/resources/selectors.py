from django.db.models import QuerySet
from common.exceptions import ValidationError
from .models import Resource


def list_resources(*, owner_id: str | None = None) -> QuerySet:
    qs = Resource.objects.select_related("owner").all()
    if owner_id:
        qs = qs.filter(owner_id=owner_id)
    return qs.order_by("name", "-created_at")


def get_resource(*, resource_id: str) -> Resource:
    try:
        return Resource.objects.select_related("owner").get(id=resource_id)
    except Resource.DoesNotExist:
        raise ValidationError("Resource not found", details={"resource_id": resource_id})

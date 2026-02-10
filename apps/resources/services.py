from .models import Resource
from common.exceptions import ValidationError


def create_resource(*, owner, name: str) -> Resource:
    name = (name or "").strip()
    if not name:
        raise ValidationError("name is required")

    # optional uniqueness (owner+name) ni service darajasida chiroyli error bilan
    if Resource.objects.filter(owner=owner, name=name).exists():
        raise ValidationError("Resource with this name already exists", details={"name": name})

    return Resource.objects.create(owner=owner, name=name)

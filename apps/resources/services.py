from common.exceptions import ValidationError, PermissionDenied
from .models import Resource


def create_resource(*, owner, name: str) -> Resource:
    name = (name or "").strip()
    if not name:
        raise ValidationError("name is required")

    # optional uniqueness (owner+name) ni service darajasida chiroyli error bilan
    if Resource.objects.filter(owner=owner, name=name).exists():
        raise ValidationError("Resource with this name already exists", details={"name": name})

    return Resource.objects.create(owner=owner, name=name)


def _is_admin(user) -> bool:
    return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))


def update_resource(*, actor, resource: Resource, name: str) -> Resource:
    if not (_is_admin(actor) or str(resource.owner_id) == str(actor.id)):
        raise PermissionDenied("You don't have permission to update this resource.")

    name = (name or "").strip()
    if not name:
        raise ValidationError("name is required")

    if Resource.objects.filter(owner=resource.owner, name=name).exclude(id=resource.id).exists():
        raise ValidationError("Resource with this name already exists", details={"name": name})

    resource.name = name
    resource.save(update_fields=["name"])
    return resource


def delete_resource(*, actor, resource: Resource) -> None:
    if not (_is_admin(actor) or str(resource.owner_id) == str(actor.id)):
        raise PermissionDenied("You don't have permission to delete this resource.")

    resource.delete()


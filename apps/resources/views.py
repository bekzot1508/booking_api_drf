from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response
from common.exceptions import AppError, ValidationError
from common.pagination import paginate_queryset

from .serializers import ResourceCreateSerializer, ResourceUpdateSerializer
from .services import create_resource, update_resource, delete_resource
from .selectors import list_resources, get_resource


class ResourceCollectionView(APIView):
    """
    GET  /resources/?owner=<uuid>&page=&page_size=
    POST /resources/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            owner_id = request.query_params.get("owner")
            page = int(request.query_params.get("page", "1"))
            page_size = int(request.query_params.get("page_size", "10"))

            qs = list_resources(owner_id=owner_id)
            paged = paginate_queryset(qs, page=page, page_size=page_size)
        except ValueError:
            return error_response(ValidationError("page and page_size must be integers"))
        except AppError as e:
            return error_response(e)

        results = [
            {
                "id": str(r.id),
                "name": r.name,
                "owner_id": str(r.owner_id),
                "created_at": r.created_at.isoformat().replace("+00:00", "Z"),
            }
            for r in paged["results"]
        ]

        return Response(
            {
                "count": paged["count"],
                "page": paged["page"],
                "page_size": paged["page_size"],
                "total_pages": paged["total_pages"],
                "results": results,
            },
            status=200,
        )

    def post(self, request):
        ser = ResourceCreateSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Invalid input", "details": ser.errors}},
                status=400,
            )

        try:
            resource = create_resource(owner=request.user, **ser.validated_data)
        except AppError as e:
            return error_response(e)

        return Response(
            {
                "id": str(resource.id),
                "name": resource.name,
                "owner_id": str(resource.owner_id),
                "created_at": resource.created_at.isoformat().replace("+00:00", "Z"),
            },
            status=201,
        )


class ResourceDetailView(APIView):
    """
    GET    /resources/{id}/
    PATCH  /resources/{id}/
    DELETE /resources/{id}/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, resource_id: str):
        try:
            r = get_resource(resource_id=resource_id)
        except AppError as e:
            return error_response(e)

        return Response(
            {
                "id": str(r.id),
                "name": r.name,
                "owner_id": str(r.owner_id),
                "created_at": r.created_at.isoformat().replace("+00:00", "Z"),
            },
            status=200,
        )

    def patch(self, request, resource_id: str):
        ser = ResourceUpdateSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Invalid input", "details": ser.errors}},
                status=400,
            )

        try:
            r = get_resource(resource_id=resource_id)
            r = update_resource(actor=request.user, resource=r, **ser.validated_data)
        except AppError as e:
            return error_response(e)

        return Response(
            {
                "id": str(r.id),
                "name": r.name,
                "owner_id": str(r.owner_id),
                "created_at": r.created_at.isoformat().replace("+00:00", "Z"),
            },
            status=200,
        )

    def delete(self, request, resource_id: str):
        try:
            r = get_resource(resource_id=resource_id)
            delete_resource(actor=request.user, resource=r)
        except AppError as e:
            return error_response(e)

        return Response(status=204)

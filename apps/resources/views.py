from rest_framework.views import APIView
from rest_framework.response import Response

from common.responses import error_response
from common.exceptions import AppError
from .serializers import ResourceCreateSerializer
from .services import create_resource


class ResourceCreateView(APIView):
    def post(self, request):
        ser = ResourceCreateSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {
                    "error":
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "Invalid input",
                            "details": ser.errors
                         }
                },
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

from rest_framework.views import APIView
from rest_framework.response import Response

from common.responses import error_response
from common.exceptions import AppError
from .serializers import RegisterSerializer, LoginSerializer
from .services import register_user, login_user


class RegisterView(APIView):
    authentication_classes = []  # public
    permission_classes = []      # public

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {"error":
                         {
                             "code": "VALIDATION_ERROR", "message": "Invalid input", "details": ser.errors
                         }
            }, status=400)

        try:
            user = register_user(**ser.validated_data)
        except AppError as e:
            return error_response(e)

        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat().replace("+00:00", "Z"),
            },
            status=201)


class LoginView(APIView):
    authentication_classes = []  # public
    permission_classes = []      # public

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {"error":
                        {
                            "code": "VALIDATION_ERROR", "message": "Invalid input", "details": ser.errors
                        }
                },
                status=400)

        try:
            data = login_user(**ser.validated_data)
        except AppError as e:
            return error_response(e)

        return Response(data, status=200)

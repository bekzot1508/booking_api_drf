from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model
from common.exceptions import AuthError
from .jwt import jwt_decode

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Authorization: Bearer <token>
    token payload: { "sub": "<user_id>", "exp": <unix>, "iat": <unix> }
    """

    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth:
            return None  # anonymous

        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthError("Invalid Authorization header. Use 'Bearer <token>'.")

        token = parts[1]
        payload = jwt_decode(token)

        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Token payload missing 'sub'")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise AuthError("User not found")

        return (user, None)

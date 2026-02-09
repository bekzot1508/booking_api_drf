import time
from django.conf import settings
from django.contrib.auth import get_user_model
from common.exceptions import ValidationError, AuthError
from .jwt import jwt_encode

User = get_user_model()


def register_user(email: str, password: str, full_name: str) -> User:
    email = (email or "").strip().lower()
    full_name = (full_name or "").strip()

    if not email or not password or not full_name:
        raise ValidationError("email, password, full_name are required")

    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already registered", details={"email": email})

    return User.objects.create_user(email=email, password=password, full_name=full_name)


def login_user(email: str, password: str) -> dict:
    email = (email or "").strip().lower()
    if not email or not password:
        raise ValidationError("email and password are required")

    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        raise AuthError("Invalid credentials")

    if not user.check_password(password):
        raise AuthError("Invalid credentials")

    now = int(time.time())
    payload = {
        "sub": str(user.id),
        "iat": now,
        "exp": now + settings.JWT_ACCESS_TTL,
    }
    token = jwt_encode(payload)

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": settings.JWT_ACCESS_TTL,
    }

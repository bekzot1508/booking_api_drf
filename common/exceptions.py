class AppError(Exception):
    code = "APP_ERROR"
    status = 400

    def __init__(self, message="Error", details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status = 400


class AuthError(AppError):
    code = "AUTH_ERROR"
    status = 401


class PermissionDenied(AppError):
    code = "FORBIDDEN"
    status = 403


class BusinessRuleViolation(AppError):
    code = "BUSINESS_RULE_VIOLATION"
    status = 400

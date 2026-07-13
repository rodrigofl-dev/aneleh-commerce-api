from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base domain exception. All business exceptions inherit from this.

    I've already structured the `detail` in the format expected by the handler in `core/errors.py`
    ({"code", "message", "details"}) — so no other part of the code needs to construct this dictionary manually.
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "APPLICATION_ERROR"
    message: str = "Unexpected error."

    def __init__(self, message: str | None = None, details: dict | None = None):
        super().__init__(
            status_code=self.status_code,
            detail={
                "code": self.code,
                "message": message or self.message,
                "details": details or {},
            },
        )


# --- Auth ---

class AuthenticationRequiredError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "AUTHENTICATION_REQUIRED"
    message = "Authentication is required to access this resource. Please sign in and try again."


class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"
    message = "Incorrect email or password."


class InvalidTokenOrExpiredError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_OR_EXPIRED_TOKEN"
    message = "Your authentication token is invalid or expired. Please sign in again."


class TokenRevokedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "TOKEN_REVOKED"
    message = "Your session is no longer valid. Please sign in again."


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "INSUFFICIENT_PERMISSIONS"
    message = "You do not have permission to perform this action."


# --- Users ---

class EmailAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "EMAIL_ALREADY_EXISTS"
    message = "An account with this email is already registered. Please sign in or use the password recovery option."


class LastAdminCannotBeDemotedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "LAST_ADMIN_CANNOT_BE_DEMOTED"
    message = "The last administrator account cannot be demoted."


class InvalidRoleError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "INVALID_ROLE"
    message = "Invalid role."


# --- Generic ---

class ResourceNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "RESOURCE_NOT_FOUND"
    message = "The requested resource could not be found."


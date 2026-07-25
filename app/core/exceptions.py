from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base domain exception. All business exceptions inherit from this.

    I've already structured the `detail` in the format
    expected by the handler in `core/errors.py` ({"code", "message", "details"})
    so no other part of the code needs to construct this dictionary manually.
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
    message = (
        "É necessário autenticação para acessar esse recurso."
        "Por favor faça login e tente novamente."
    )


class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"
    message = "Credenciais inválidas."


class InvalidTokenOrExpiredError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_OR_EXPIRED_TOKEN"
    message = (
        "Seu token de autenticação está inválido ou expirado."
        "Por favor faça um novo login."
    )


class TokenRevokedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "TOKEN_REVOKED"
    message = "Sua sessão não é mais válida. Por favor faça um novo login."


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "INSUFFICIENT_PERMISSIONS"
    message = "Você não tem permissão para realizar esta ação."


# --- Users ---


class EmailAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "EMAIL_ALREADY_EXISTS"
    message = (
        "Uma conta com este e-mail já está registrada. "
        "Por favor faça login ou use a opção de recuperação de senha."
    )


class LastAdminCannotBeDemotedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "LAST_ADMIN_CANNOT_BE_DEMOTED"
    message = "O último administrador não pode ser removido."


class InvalidRoleError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "INVALID_ROLE"
    message = "Papel inválido."


class UserNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "USER_NOT_FOUND"
    message = "Usuário não encontrado."


# --- Categories ---


class CategoryNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "CATEGORY_NOT_FOUND"
    message = "Categoria não encontrada."


class CategoryAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "CATEGORY_ALREADY_EXISTS"
    message = "Já existe uma categoria com este nome."


class CategoryHasProductsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "CATEGORY_HAS_PRODUCTS"
    message = "Não é possível remover uma categoria com produtos."


# --- Generic ---


class InternalConfigurationError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "INTERNAL_CONFIGURATION_ERROR"
    message = "Configuração ausente ou inválida. Por favor contate o suporte."

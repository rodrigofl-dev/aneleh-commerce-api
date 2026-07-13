from sqlalchemy.orm import Session

from app.core.config import settings

from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError

from app.core.security import hash_password, verify_password, create_access_token

from app.users.models import User
from app.users.repository import UserRepository
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def register(self, data: RegisterRequest) -> User:
        if self.repository.get_by_email(data.email) is not None:
            raise EmailAlreadyExistsError

        customer_role = self.repository.get_role_by_name("customer")

        user = User(
            name=data.name,
            email=data.email,
            role_id=customer_role.id,
            password_hash=hash_password(data.password),
        )

        return self.repository.save(user)

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            expires_in=settings.jwt_expiration_seconds,
            user=user,
        )

from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidRoleError,
    LastAdminCannotBeDemotedError,
    UserNotFoundError,
)

from app.core.security import hash_password, decode_access_token
from app.core.token_blacklist import blacklist_token
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserRoleUpdate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def update_profile(self, user: User, data: UserUpdate, token: str) -> User:
        if data.email and data.email != user.email:
            existing = self.repository.get_by_email(data.email)
            if existing:
                raise EmailAlreadyExistsError
            user.email = data.email

        if data.name:
            user.name = data.name

        if data.password:
            user.password_hash = hash_password(data.password)
            payload = decode_access_token(token)
            blacklist_token(token, payload["exp"])

        return self.repository.save(user)

    def get_by_id(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(
                details={
                    "user_id": user_id,
                }
            )

        return user

    def update_role(self, user_id: int, data: UserRoleUpdate) -> User:
        user = self.get_by_id(user_id)

        if user.role.name == "admin" and data.role != "admin":
            if self.repository.count_admins() <= 1:
                raise LastAdminCannotBeDemotedError

        new_role = self.repository.get_role_by_name(data.role)
        if not new_role:
            raise InvalidRoleError(
                details={
                    "role": data.role,
                }
            )

        user.role = new_role

        return self.repository.save(user)

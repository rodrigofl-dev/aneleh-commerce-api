import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationRequiredError,
    ForbiddenError,
    InvalidTokenOrExpiredError,
)
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.users.models import User

# auto_error=False: because HTTPBearer raise 403 instead of 401
bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthenticationRequiredError()

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise InvalidTokenOrExpiredError()

    # TODO (módulo AUTH, RF-AUTH-03): checar blacklist no Redis antes de aceitar o token.

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise InvalidTokenOrExpiredError()

    return user


def require_role(role_name: str):
    """Use on router: dependencies=[Depends(require_role("admin"))]"""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name != role_name:
            raise ForbiddenError()
        return current_user

    return dependency

from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyExistsError
)

from app.core.security import hash_password
from app.users.models import User
from app.users.repository import UserRepository
from app.auth.schemas import RegisterRequest

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)
    
    def register(self, data: RegisterRequest) -> User:
        email = data.email.lower()

        if self.repository.get_by_email(email) is not None:
            raise EmailAlreadyExistsError()
        
        customer_role = self.repository.get_role_by_name("customer")

        user = User(
            name=data.name,
            email=email,
            role_id=customer_role.id,
            password_hash=hash_password(data.password),
        )

        return self.repository.save(user)

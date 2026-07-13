from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.users.schemas import UserOut
from app.auth.schemas import RegisterRequest
from app.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_account(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    service = AuthService(db)
    return service.register(data)

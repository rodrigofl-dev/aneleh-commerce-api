from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_role
from app.users.models import User
from app.users.schemas import UserOut, UserRoleUpdate, UserUpdate
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])#, dependencies=[Depends(get_current_user)])


@router.get("/me", response_model=UserOut)
def read_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.update_profile(current_user, data)


@router.get(
    "/{user_id}",
    response_model=UserOut,
    #dependencies=[Depends(require_role("admin"))],
)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_by_id(user_id)


@router.patch(
    "/{user_id}/role",
    response_model=UserOut,
    dependencies=[Depends(require_role("admin"))],
)
def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.update_role(user_id, data)

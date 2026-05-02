"""Ендпоїнти для адміна сервісу — керування користувачами і ролями."""
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import User
from app.security import hash_password

router = APIRouter(prefix="/admin/users", tags=["admin_users"])

Role = Literal["student", "teacher", "db_admin", "system_admin"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None
    role: Role = "student"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: Role
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[UserOut])
def list_users(
    _: User = Depends(require_role("system_admin")),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.id).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _: User = Depends(require_role("system_admin")),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(409, "Користувач з такою поштою вже існує")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    payload: UserUpdate,
    user_id: int = Path(..., ge=1),
    current: User = Depends(require_role("system_admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Користувача не знайдено")

    if user.id == current.id and payload.is_active is False:
        raise HTTPException(400, "Не можна заблокувати самого себе")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def block_user(
    user_id: int = Path(..., ge=1),
    current: User = Depends(require_role("system_admin")),
    db: Session = Depends(get_db),
):
    """Блокує користувача (м'яке видалення — is_active=False)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Користувача не знайдено")
    if user.id == current.id:
        raise HTTPException(400, "Не можна заблокувати самого себе")

    user.is_active = False
    db.commit()
    return None
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import Token, UserOut, UserRegister
from app.security import create_access_token, hash_password, verify_password
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з такою поштою вже існує",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        initial_time_budget_seconds=payload.initial_time_budget_minutes * 60,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірна пошта або пароль",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Користувача заблоковано",
        )

    token = create_access_token(user_id=user.id, role=user.role)
    return Token(access_token=token, user=UserOut.model_validate(user))
class GoogleAuthIn(BaseModel):
    credential: str


@router.post("/google", response_model=Token)
def google_auth(payload: GoogleAuthIn, db: Session = Depends(get_db)):
    """Авторизація через Google ID token."""
    if not settings.google_client_id:
        raise HTTPException(500, "Google авторизацію не налаштовано на сервері")

    try:
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as e:
        raise HTTPException(401, f"Невалідний Google-токен: {e}")

    email = idinfo.get("email")
    if not email or not idinfo.get("email_verified"):
        raise HTTPException(401, "Email не підтверджений у Google")

    full_name = idinfo.get("name")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        # Перший вхід через Google — створюємо користувача
        user = User(
            email=email,
            password_hash=None,
            full_name=full_name,
            role="student",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_active:
        raise HTTPException(403, "Користувача заблоковано")

    # Якщо у користувача не було повного імені — оновлюємо з Google
    if not user.full_name and full_name:
        user.full_name = full_name
        db.commit()
        db.refresh(user)

    token = create_access_token(user_id=user.id, role=user.role)
    return Token(access_token=token, user=UserOut.model_validate(user))
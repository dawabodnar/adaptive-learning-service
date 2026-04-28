from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Role = Literal["student", "teacher", "db_admin", "system_admin"]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = None
    role: Role = "student"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: Role
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class SessionStart(BaseModel):
    time_budget_seconds: int = Field(ge=60, le=7200, default=1800)
    # від 1 хвилини до 2 годин, типово 30 хв


class TaskOut(BaseModel):
    id: int
    content: str
    estimated_time_seconds: int

    class Config:
        from_attributes = True


class SessionStartResponse(BaseModel):
    session_id: int
    time_budget_seconds: int
    total_estimated_seconds: int
    total_utility: float
    tasks: list[TaskOut]
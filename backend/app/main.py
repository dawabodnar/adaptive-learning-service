from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.dependencies import get_current_user
from app.models import User
from app.routers import auth, sessions
from app.schemas import UserOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Adaptive Learning Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sessions.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/me", response_model=UserOut, tags=["users"])
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://dasha@localhost:5432/adaptive_learning"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://veto:veto@localhost:5432/veto"
    redis_url: str = "redis://localhost:6379/0"
    demo_user_id: str = "demo-user"  # replaced by JWT subject in Phase 3


settings = Settings()

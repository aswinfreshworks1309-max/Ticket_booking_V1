from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    # Feature flag to enable Claude Haiku 4.5 for all clients
    CLAUDE_HAIKU_ENABLED: bool = True
    CLAUDE_HAIKU_VERSION: str = "4.5"

    class Config:
        env_file = ".env"

settings = Settings()

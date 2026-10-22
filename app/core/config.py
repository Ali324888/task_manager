from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Task Management API"
    DEBUG: bool = False
    DATABASE_URL: str = "task_manager.db"

    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
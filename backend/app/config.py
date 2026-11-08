from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Agent Factory API"
    database_url: str | None = None
    redis_url: str | None = None


settings = Settings()

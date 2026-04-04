from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "mini-paas"
    app_host: str = "0.0.0.0"
    app_port: int = 8081

    postgres_db: str = "mini_paas"
    postgres_user: str = "mini_paas"
    postgres_password: str = "mini_paas"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
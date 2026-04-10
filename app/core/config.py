from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "mini-paas"
    app_host: str = "0.0.0.0"
    app_port: int = 8081
    debug: bool = False

    postgres_db: str = "mini_paas"
    postgres_user: str = "mini_paas"
    postgres_password: str = "mini_paas"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    docker_network: str = "mini-paas_default"
    nginx_container_name: str = "mini-paas-nginx"
    nginx_dynamic_dir: str = "/app/nginx/dynamic"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()

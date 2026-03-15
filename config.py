"""
Application configuration — reads from environment / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env:   str = "development"
    app_host:  str = "0.0.0.0"
    app_port:  int = 8888
    app_debug: bool = True

    deepseek_api_key:  str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model:    str = "deepseek-chat"


settings = Settings()

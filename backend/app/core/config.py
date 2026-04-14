from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "awai-lp-contact-api"
    contact_from_email: str = Field(..., alias="CONTACT_FROM_EMAIL")
    contact_to_email: str = Field(..., alias="CONTACT_TO_EMAIL")
    resend_api_key: str = Field(..., alias="RESEND_API_KEY")
    contact_allowed_origins: str = Field(
        "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080,http://127.0.0.1:8080",
        alias="CONTACT_ALLOWED_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        raw_value = self.contact_allowed_origins.strip()
        if raw_value == "*":
            return ["*"]

        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

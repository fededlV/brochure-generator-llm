from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: Optional[str] = Field(default=None, validation_alias="GEMINI_API_KEY")
    google_api_key: Optional[str] = Field(default=None, validation_alias="GOOGLE_API_KEY")
    api_key_generic: Optional[str] = Field(default=None, validation_alias="API_KEY")

    gemini_model: str = Field(default="gemini-3.5-flash-lite", alias="GEMINI_MODEL")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True
    )

    @property
    def effective_api_key(self) -> Optional[str]:
        return self.gemini_api_key or self.google_api_key or self.api_key_generic

    def is_api_key_valid(self) -> bool:
        key = self.effective_api_key
        return bool(key and len(key.strip()) > 10)


settings = Settings()

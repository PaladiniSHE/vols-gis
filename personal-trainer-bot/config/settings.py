"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    bot_token: str = Field(..., env="BOT_TOKEN")
    admin_ids: List[int] = Field(default_factory=list, env="ADMIN_IDS")
    
    # AI
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    ai_model: str = Field(default="gpt-4o-mini", env="AI_MODEL")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./database/trainer.db",
        env="DATABASE_URL"
    )
    
    # Timezone
    default_timezone: str = Field(default="Europe/Moscow", env="DEFAULT_TIMEZONE")
    
    # Debug
    debug: bool = Field(default=False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "admin_ids":
                return [int(x.strip()) for x in raw_val.split(",") if x.strip()]
            return raw_val


def get_settings() -> Settings:
    """Получить настройки приложения"""
    return Settings()


settings = get_settings()

__all__ = ["settings", "configure_logging"]

import logging

from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    DEBUG: bool = False
    TELEGRAM_API_TOKEN: str
    DATABASE_URL: PostgresDsn


settings = Settings()


def configure_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )

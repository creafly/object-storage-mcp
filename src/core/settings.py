import logging
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения для работы с AWS S3."""

    APP_NAME: str = Field(
        default="Object Storage S3", description="Название приложения"
    )

    AWS_ACCESS_KEY_ID: str = Field(
        default="", description="AWS Access Key ID для доступа к S3"
    )
    AWS_SECRET_ACCESS_KEY: str = Field(
        default="", description="AWS Secret Access Key для доступа к S3"
    )
    AWS_REGION: str = Field(default="us-east-1", description="AWS регион")
    S3_ENDPOINT_URL: Optional[str] = Field(
        default=None,
        description="""
        Кастомный endpoint URL для S3-совместимых
        хранилищ (MinIO, Yandex Object Storage и т.д.)
        """,
    )
    S3_BUCKET_NAME: str = Field(default="", description="Имя бакета S3 по умолчанию")

    PORT: int = Field(
        default=8000, ge=1024, le=65535, description="Порт для запуска MCP сервера"
    )
    HOST: str = Field(default="0.0.0.0", description="Хост для запуска MCP сервера")
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")

    MAX_FILE_SIZE_MB: int = Field(
        default=100,
        ge=1,
        le=5000,
        description="Максимальный размер файла для загрузки в МБ",
    )
    MAX_LIST_OBJECTS: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Максимальное количество объектов при листинге",
    )
    ALLOWED_EXTENSIONS: Optional[str] = Field(
        default=None,
        description="""
        Разрешённые расширения файлов через запятую
        (если не задано — все разрешены)
        """,
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def allowed_extensions_list(self) -> list[str] | None:
        """Список разрешённых расширений файлов."""
        if self.ALLOWED_EXTENSIONS:
            return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
        return None

    @property
    def max_file_size_bytes(self) -> int:
        """Максимальный размер файла в байтах."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def validate_required_fields(self) -> None:
        """Проверка обязательных полей."""
        if not self.AWS_ACCESS_KEY_ID:
            raise ValueError("AWS_ACCESS_KEY_ID is required")
        if not self.AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS_SECRET_ACCESS_KEY is required")
        if not self.S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME is required")


@lru_cache()
def get_settings() -> Settings:
    """Получить экземпляр настроек (с кешированием)."""
    return Settings()


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Настройка логирования."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return logging.getLogger("mcp_object_storage")

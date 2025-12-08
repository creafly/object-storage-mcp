import logging
from typing import Optional

from fastmcp import Context
from pydantic import Field

from src.core.settings import get_settings
from src.core.validators import PathValidationError
from src.entrypoints.mcp_instance import mcp
from src.services.s3_service import S3Service

logger = logging.getLogger("mcp_object_storage")


@mcp.tool(
    name="list_files",
    description="""Получение списка файлов из S3 Object Storage.

Этот инструмент позволяет получить список файлов в бакете S3 с возможностью фильтрации по префиксу.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно узнать какие файлы есть в хранилище
- Когда нужно найти файлы в определённой директории
- Когда нужно получить метаданные нескольких файлов

ФИЛЬТРАЦИЯ:
- Используйте prefix для фильтрации по пути (например: 'documents/' для всех файлов в папке documents)
- Можно ограничить количество результатов через max_keys

ВОЗВРАЩАЕМЫЕ ДАННЫЕ:
- Список файлов с ключами, размерами, датами изменения
- Общее количество найденных файлов
- Суммарный размер всех файлов
""",  # noqa: E501
)
async def list_files(
    prefix: str = Field(
        default="",
        description="Префикс для фильтрации файлов "
        + "(например: 'documents/', 'images/2024/')."
        "Оставьте пустым для получения всех файлов.",
    ),
    bucket: Optional[str] = Field(
        default=None,
        description="Имя бакета S3 (необязательно). Если не указано, используется бакет из настроек.",  # noqa: E501
    ),
    max_keys: Optional[int] = Field(
        default=None,
        description="Максимальное количество файлов в ответе. "
        "По умолчанию используется значение из настроек (обычно 1000).",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """
    Получение списка файлов из S3 Object Storage.

    Args:
        prefix: Префикс для фильтрации
        bucket: Имя бакета (опционально)
        max_keys: Максимальное количество файлов
        ctx: Контекст MCP

    Returns:
        Список файлов с метаданными
    """
    if ctx:
        filter_msg = f" с префиксом '{prefix}'" if prefix else ""
        await ctx.info(f"Получаем список файлов{filter_msg}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(
        f"[list_files] Вызван с prefix={prefix}, bucket={bucket}, max_keys={max_keys}"
    )

    try:
        settings = get_settings()
        settings.validate_required_fields()

        s3_service = S3Service(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = s3_service.list_files(
            prefix=prefix,
            bucket=bucket,
            max_keys=max_keys,
        )

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Найдено файлов: {result['total_count']}")

        return {
            "success": True,
            "message": f"Найдено {result['total_count']} файлов",
            "data": result,
        }

    except PathValidationError as e:
        if ctx:
            await ctx.error(f"Ошибка валидации: {e}")
        return {"success": False, "error": "validation_error", "message": str(e)}
    except Exception as e:
        if ctx:
            await ctx.error(f"Ошибка получения списка: {e}")
        return {"success": False, "error": "list_error", "message": str(e)}

from typing import Optional

from fastmcp import Context
from pydantic import Field

from src.core.settings import get_settings
from src.core.validators import PathValidationError
from src.entrypoints.mcp_instance import mcp
from src.services.s3_service import S3Service


@mcp.tool(
    name="get_file_info",
    description="""Получение информации о файле в S3 Object Storage.

Этот инструмент позволяет получить метаданные файла без скачивания его содержимого.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно узнать размер файла
- Когда нужно проверить существование файла
- Когда нужно получить дату последнего изменения
- Когда нужно узнать тип содержимого (MIME type)

ВОЗВРАЩАЕМЫЕ ДАННЫЕ:
- Размер файла в байтах
- MIME тип файла
- Дата последнего изменения
- ETag (хеш содержимого)
- Класс хранения
- Пользовательские метаданные

ВАЖНО:
- Не скачивает содержимое файла (экономит трафик)
- Быстрее чем download_file для проверки метаданных
""",
)
async def get_file_info(
    key: str = Field(
        ...,
        description="Путь к файлу в бакете (например: 'documents/report.pdf'). "
        "Должен точно соответствовать ключу объекта в S3.",
    ),
    bucket: Optional[str] = Field(
        default=None,
        description="Имя бакета S3 (необязательно). Если не указано, используется бакет из настроек.",  # noqa: E501
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """
    Получение информации о файле в S3 Object Storage.

    Args:
        key: Путь к файлу в бакете
        bucket: Имя бакета (опционально)
        ctx: Контекст MCP

    Returns:
        Метаданные файла
    """
    if ctx:
        await ctx.info(f"Получаем информацию о файле: {key}")
        await ctx.report_progress(progress=0, total=100)

    try:
        settings = get_settings()
        settings.validate_required_fields()

        s3_service = S3Service(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = s3_service.get_file_info(
            key=key,
            bucket=bucket,
        )

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            size_kb = result["size_bytes"] / 1024
            await ctx.info(f"Файл найден: {result['key']} ({size_kb:.2f} КБ)")

        return {
            "success": True,
            "message": f"Информация о файле '{result['key']}' получена",
            "data": result,
        }

    except PathValidationError as e:
        if ctx:
            await ctx.error(f"Ошибка: {e}")
        return {"success": False, "error": "validation_error", "message": str(e)}
    except Exception as e:
        if ctx:
            await ctx.error(f"Ошибка получения информации: {e}")
        return {"success": False, "error": "info_error", "message": str(e)}

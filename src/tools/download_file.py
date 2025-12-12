from typing import Optional

from fastmcp import Context
from pydantic import Field

from src.core.settings import get_settings
from src.core.validators import PathValidationError
from src.entrypoints.mcp_instance import mcp
from src.services.s3_service import S3Service


@mcp.tool(
    name="download_file",
    description="""Скачивание файла из S3 Object Storage.

Этот инструмент позволяет получить содержимое файла из облачного хранилища S3.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно получить содержимое файла из хранилища
- Когда нужно прочитать ранее сохранённый документ
- Когда нужно получить данные для обработки

ФОРМАТ ОТВЕТА:
- Текстовые файлы возвращаются как UTF-8 строки
- Бинарные файлы возвращаются в base64 формате
- Можно явно запросить base64 формат через параметр as_base64

ВАЖНО:
- Путь должен точно соответствовать ключу объекта в S3
- Пути не должны содержать '..' или начинаться с '/'
""",
)
async def download_file(
    key: str = Field(
        ...,
        description="Путь к файлу в бакете (например: 'documents/report.pdf'). "
        "Должен точно соответствовать ключу объекта в S3.",
    ),
    bucket: Optional[str] = Field(
        default=None,
        description="Имя бакета S3 (необязательно). Если не указано, используется бакет из настроек.",  # noqa: E501
    ),
    as_base64: bool = Field(
        default=False,
        description="Вернуть содержимое в base64 формате. "
        "Полезно для бинарных файлов или когда нужен единый формат.",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """
    Скачивание файла из S3 Object Storage.

    Args:
        key: Путь к файлу в бакете
        bucket: Имя бакета (опционально)
        as_base64: Вернуть как base64
        ctx: Контекст MCP

    Returns:
        Содержимое файла и метаданные
    """
    if ctx:
        await ctx.info(f"Скачиваем файл: {key}")
        await ctx.report_progress(progress=0, total=100)

    try:
        settings = get_settings()
        settings.validate_required_fields()

        s3_service = S3Service(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = s3_service.download_file(
            key=key,
            bucket=bucket,
            as_base64=as_base64,
        )

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Файл успешно скачан: {result['key']} ({result['size_bytes']} байт)")

        return {
            "success": True,
            "message": f"Файл '{result['key']}' успешно скачан",
            "data": result,
        }

    except PathValidationError as e:
        if ctx:
            await ctx.error(f"Ошибка: {e}")
        return {"success": False, "error": "validation_error", "message": str(e)}
    except Exception as e:
        if ctx:
            await ctx.error(f"Ошибка скачивания: {e}")
        return {"success": False, "error": "download_error", "message": str(e)}

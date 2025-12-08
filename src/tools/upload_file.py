import logging
from typing import Optional

from fastmcp import Context
from pydantic import Field

from src.core.settings import get_settings
from src.core.validators import ConflictError, PathValidationError
from src.entrypoints.mcp_instance import mcp
from src.services.s3_service import S3Service

logger = logging.getLogger("mcp_object_storage")


@mcp.tool(
    name="upload_file",
    description="""Загрузка файла в S3 Object Storage.

Этот инструмент позволяет загружать файлы в облачное хранилище S3. Поддерживает:
- Загрузку текстовых файлов напрямую
- Загрузку бинарных файлов через base64 кодирование
- Проверку на существование файла (conflict detection)
- Валидацию пути для защиты от directory traversal атак

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно сохранить файл в облачное хранилище
- Когда нужно создать резервную копию файла
- Когда нужно поделиться файлом между системами

ВАЖНО:
- По умолчанию перезапись существующих файлов запрещена
- Для перезаписи установите параметр overwrite=true
- Пути не должны содержать '..' или начинаться с '/'
""",
)
async def upload_file(
    key: str = Field(
        ...,
        description="Путь к файлу в бакете "
        + "(например: 'documents/report.pdf', 'images/logo.png')."
        "Не может содержать '..' или начинаться с '/'.",
    ),
    content: str = Field(
        ...,
        description="Содержимое файла. Для текстовых файлов — обычная строка. "
        "Для бинарных файлов — base64 закодированная строка (установите is_base64=true).",  # noqa: E501
    ),
    content_type: str = Field(
        default="application/octet-stream",
        description="MIME тип файла (например: 'text/plain', 'application/pdf', 'image/png')",  # noqa: E501
    ),
    bucket: Optional[str] = Field(
        default=None,
        description="Имя бакета S3 (необязательно). Если не указано, используется бакет из настроек.",  # noqa: E501
    ),
    overwrite: bool = Field(
        default=False,
        description="Разрешить перезапись существующего файла. "
        "По умолчанию False — если файл существует, будет возвращена ошибка.",
    ),
    is_base64: bool = Field(
        default=False,
        description="Если True, параметр content интерпретируется как base64-закодированные данные.",  # noqa: E501
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """
    Загрузка файла в S3 Object Storage.

    Args:
        key: Путь к файлу в бакете
        content: Содержимое файла
        content_type: MIME тип файла
        bucket: Имя бакета (опционально)
        overwrite: Разрешить перезапись
        is_base64: Содержимое в base64
        ctx: Контекст MCP

    Returns:
        Информация о загруженном файле
    """
    if ctx:
        await ctx.info(f"Загружаем файл: {key}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(
        f"[upload_file] Вызван с key={key}, "
        + f"bucket={bucket}, overwrite={overwrite}"
    )

    try:
        settings = get_settings()
        settings.validate_required_fields()

        s3_service = S3Service(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = s3_service.upload_file(
            key=key,
            content=content,
            content_type=content_type,
            bucket=bucket,
            overwrite=overwrite,
            is_base64=is_base64,
        )

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Файл успешно загружен: {result['key']}")

        return {
            "success": True,
            "message": f"Файл '{result['key']}' успешно загружен",
            "data": result,
        }

    except PathValidationError as e:
        if ctx:
            await ctx.error(f"Ошибка валидации пути: {e}")
        return {"success": False, "error": "validation_error", "message": str(e)}
    except ConflictError as e:
        if ctx:
            await ctx.error(f"Конфликт: {e}")
        return {"success": False, "error": "conflict_error", "message": str(e)}
    except Exception as e:
        if ctx:
            await ctx.error(f"Ошибка загрузки: {e}")
        return {"success": False, "error": "upload_error", "message": str(e)}

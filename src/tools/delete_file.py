from typing import Optional

from fastmcp import Context
from pydantic import Field

from src.core.settings import get_settings
from src.core.validators import PathValidationError
from src.entrypoints.mcp_instance import mcp
from src.services.s3_service import S3Service


@mcp.tool(
    name="delete_file",
    description="""Удаление файла из S3 Object Storage.

Этот инструмент позволяет удалить файл из облачного хранилища S3.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно освободить место в хранилище
- Когда файл больше не нужен
- Когда нужно удалить устаревшие данные

ПРЕДУПРЕЖДЕНИЕ:
- Удаление необратимо!
- Убедитесь, что файл действительно нужно удалить
- Рекомендуется сначала сделать резервную копию

ВАЖНО:
- Файл должен существовать (иначе будет ошибка)
- Пути не должны содержать '..' или начинаться с '/'
""",
)
async def delete_file(
    key: str = Field(
        ...,
        description="Путь к файлу в бакете для удаления  "
        + "(например: 'documents/old_report.pdf')."
        "Должен точно соответствовать ключу объекта в S3.",
    ),
    bucket: Optional[str] = Field(
        default=None,
        description="Имя бакета S3 (необязательно). Если не указано, используется бакет из настроек.",  # noqa: E501
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """
    Удаление файла из S3 Object Storage.

    Args:
        key: Путь к файлу в бакете
        bucket: Имя бакета (опционально)
        ctx: Контекст MCP

    Returns:
        Информация об удалённом файле
    """
    if ctx:
        await ctx.info(f"Удаляем файл: {key}")
        await ctx.report_progress(progress=0, total=100)

    try:
        settings = get_settings()
        settings.validate_required_fields()

        s3_service = S3Service(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = s3_service.delete_file(
            key=key,
            bucket=bucket,
        )

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Файл успешно удалён: {result['key']}")

        return {
            "success": True,
            "message": f"Файл '{result['key']}' успешно удалён",
            "data": result,
        }

    except PathValidationError as e:
        if ctx:
            await ctx.error(f"Ошибка: {e}")
        return {"success": False, "error": "validation_error", "message": str(e)}
    except Exception as e:
        if ctx:
            await ctx.error(f"Ошибка удаления: {e}")
        return {"success": False, "error": "delete_error", "message": str(e)}

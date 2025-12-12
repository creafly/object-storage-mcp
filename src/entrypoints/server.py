import traceback

from src.core.settings import get_settings, setup_logging
from src.entrypoints.mcp_instance import mcp

settings = get_settings()
logger = setup_logging(settings.LOG_LEVEL)


def main():
    from src.tools import (  # noqa: F401
        delete_file,
        download_file,
        get_file_info,
        list_files,
        upload_file,
    )

    """Запуск MCP сервера с HTTP транспортом."""
    logger.info("=" * 60)
    logger.info(f"Бакет по умолчанию: {settings.S3_BUCKET_NAME or 'не задан'}")
    logger.info(f"Регион: {settings.AWS_REGION}")
    if settings.S3_ENDPOINT_URL:
        logger.info(f"Endpoint: {settings.S3_ENDPOINT_URL}")

    tool_count = len(mcp._tool_manager._tools) if hasattr(mcp, "_tool_manager") else "unknown"
    logger.info(f"Зарегистрировано инструментов: {tool_count}")
    logger.info("=" * 60)

    try:
        mcp.run(
            transport="streamable-http",
            host=settings.HOST,
            port=settings.PORT,
        )
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
        logger.info("Выполняем graceful shutdown...")
        logger.info("Сервер остановлен")
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

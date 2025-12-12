import os
import re
from pathlib import PurePosixPath


class PathValidationError(Exception):
    """Ошибка валидации пути."""

    pass


class ConflictError(Exception):
    """Ошибка конфликта при перезаписи файла."""

    pass


def validate_path_safety(path: str) -> str:
    """
    Валидация пути для предотвращения directory traversal атак.

    Проверяет:
    - Отсутствие '..' в пути
    - Отсутствие абсолютных путей (начинающихся с /)
    - Отсутствие null-байтов
    - Корректность символов в пути

    Args:
        path: Путь для валидации

    Returns:
        Нормализованный безопасный путь

    Raises:
        PathValidationError: Если путь небезопасен
    """
    if not path:
        raise PathValidationError("Путь не может быть пустым")

    if "\x00" in path:
        raise PathValidationError("Путь содержит недопустимые символы (null-байт)")

    if path.startswith("/") or path.startswith("\\"):
        raise PathValidationError("Абсолютные пути не разрешены. Используйте относительный путь")

    if ".." in path:
        raise PathValidationError("Directory traversal атака обнаружена: '..' не разрешено в пути")

    normalized = PurePosixPath(path).as_posix()

    if normalized.startswith("/"):
        raise PathValidationError("Путь после нормализации стал абсолютным")

    if re.search(r'[<>:"|?*\x00-\x1f]', normalized):
        raise PathValidationError("Путь содержит недопустимые символы")

    if len(normalized) > 1024:
        raise PathValidationError("Путь слишком длинный (максимум 1024 символа)")

    return normalized


def validate_file_extension(filename: str, allowed_extensions: list[str] | None) -> None:
    """
    Проверка расширения файла.

    Args:
        filename: Имя файла
        allowed_extensions: Список разрешённых расширений (без точки, в нижнем регистре)

    Raises:
        PathValidationError: Если расширение не разрешено
    """
    if allowed_extensions is None:
        return

    _, ext = os.path.splitext(filename)
    ext = ext.lstrip(".").lower()

    if not ext and allowed_extensions:
        raise PathValidationError(
            "Файл без расширения не разрешён. "
            + f"Разрешённые расширения: {', '.join(allowed_extensions)}"
        )

    if ext not in allowed_extensions:
        raise PathValidationError(
            f"Расширение '.{ext}' не разрешено. "
            + f"Разрешённые расширения: {', '.join(allowed_extensions)}"
        )


def validate_file_size(size_bytes: int, max_size_bytes: int) -> None:
    """
    Проверка размера файла.

    Args:
        size_bytes: Размер файла в байтах
        max_size_bytes: Максимальный разрешённый размер в байтах

    Raises:
        PathValidationError: Если размер превышает лимит
    """
    if size_bytes <= 0:
        raise PathValidationError("Размер файла должен быть положительным числом")

    if size_bytes > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        actual_mb = size_bytes / (1024 * 1024)
        raise PathValidationError(
            f"Размер файла ({actual_mb:.2f} МБ) "
            + f"превышает максимально допустимый ({max_mb:.0f} МБ)"
        )


def validate_bucket_name(bucket_name: str) -> str:
    """
    Валидация имени бакета S3.

    Args:
        bucket_name: Имя бакета

    Returns:
        Валидированное имя бакета

    Raises:
        PathValidationError: Если имя бакета некорректно
    """
    if not bucket_name:
        raise PathValidationError("Имя бакета не может быть пустым")

    if len(bucket_name) < 3 or len(bucket_name) > 63:
        raise PathValidationError("Имя бакета должно содержать от 3 до 63 символов")

    if not re.match(r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$", bucket_name):
        raise PathValidationError(
            "Имя бакета должно содержать только строчные буквы, цифры и дефисы, "
            "начинаться и заканчиваться буквой или цифрой"
        )

    if "--" in bucket_name:
        raise PathValidationError("Имя бакета не может содержать последовательные дефисы")

    return bucket_name

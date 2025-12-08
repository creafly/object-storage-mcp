import base64
import logging
from datetime import datetime
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.core.settings import Settings
from src.core.validators import (
    ConflictError,
    PathValidationError,
    validate_file_extension,
    validate_file_size,
    validate_path_safety,
)

logger = logging.getLogger("mcp_object_storage")


class S3Service:
    """Сервис для работы с AWS S3."""

    def __init__(self, settings: Settings):
        """
        Инициализация S3 сервиса.

        Args:
            settings: Настройки приложения
        """
        self.settings = settings
        self._client = None

    @property
    def client(self):
        """Lazy инициализация S3 клиента."""
        if self._client is None:
            client_kwargs = {
                "aws_access_key_id": self.settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": self.settings.AWS_SECRET_ACCESS_KEY,
                "region_name": self.settings.AWS_REGION,
            }
            if self.settings.S3_ENDPOINT_URL:
                client_kwargs["endpoint_url"] = self.settings.S3_ENDPOINT_URL

            self._client = boto3.client("s3", **client_kwargs)
        return self._client

    def check_file_exists(self, key: str, bucket: str | None = None) -> bool:
        """
        Проверка существования файла в S3.

        Args:
            key: Ключ объекта
            bucket: Имя бакета (опционально, по умолчанию из настроек)

        Returns:
            True если файл существует, False если нет
        """
        bucket = bucket or self.settings.S3_BUCKET_NAME
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def upload_file(
        self,
        key: str,
        content: str | bytes,
        content_type: str = "application/octet-stream",
        bucket: str | None = None,
        overwrite: bool = False,
        is_base64: bool = False,
    ) -> dict[str, Any]:
        """
        Загрузка файла в S3.

        Args:
            key: Путь к файлу в бакете
            content: Содержимое файла (строка или байты)
            content_type: MIME тип файла
            bucket: Имя бакета (опционально)
            overwrite: Разрешить перезапись существующего файла
            is_base64: Если True, content является base64-encoded строкой

        Returns:
            Информация о загруженном файле

        Raises:
            PathValidationError: При невалидном пути
            ConflictError: При попытке перезаписи без флага overwrite
        """
        bucket = bucket or self.settings.S3_BUCKET_NAME

        safe_key = validate_path_safety(key)

        validate_file_extension(safe_key, self.settings.allowed_extensions_list)

        if is_base64:
            try:
                file_bytes = base64.b64decode(content)
            except Exception as e:
                raise PathValidationError(f"Некорректные base64 данные: {e}")
        elif isinstance(content, str):
            file_bytes = content.encode("utf-8")
        else:
            file_bytes = content

        validate_file_size(len(file_bytes), self.settings.max_file_size_bytes)

        if not overwrite and self.check_file_exists(safe_key, bucket):
            raise ConflictError(
                f"Файл '{safe_key}' уже существует. "
                "Используйте параметр overwrite=true для перезаписи"
            )

        self.client.put_object(
            Bucket=bucket,
            Key=safe_key,
            Body=file_bytes,
            ContentType=content_type,
        )

        logger.info(f"Файл '{safe_key}' загружен в бакет '{bucket}'")

        return {
            "key": safe_key,
            "bucket": bucket,
            "size_bytes": len(file_bytes),
            "content_type": content_type,
            "uploaded_at": datetime.utcnow().isoformat(),
        }

    def download_file(
        self,
        key: str,
        bucket: str | None = None,
        as_base64: bool = False,
    ) -> dict[str, Any]:
        """
        Скачивание файла из S3.

        Args:
            key: Путь к файлу в бакете
            bucket: Имя бакета (опционально)
            as_base64: Вернуть содержимое как base64 строку

        Returns:
            Информация о файле и его содержимое

        Raises:
            PathValidationError: При невалидном пути
        """
        bucket = bucket or self.settings.S3_BUCKET_NAME

        safe_key = validate_path_safety(key)

        try:
            response = self.client.get_object(Bucket=bucket, Key=safe_key)
            content = response["Body"].read()

            result = {
                "key": safe_key,
                "bucket": bucket,
                "size_bytes": response["ContentLength"],
                "content_type": response.get("ContentType", "application/octet-stream"),
                "last_modified": (
                    response["LastModified"].isoformat()
                    if response.get("LastModified")
                    else None
                ),
                "etag": response.get("ETag", "").strip('"'),
            }

            if as_base64:
                result["content"] = base64.b64encode(content).decode("utf-8")
                result["encoding"] = "base64"
            else:
                try:
                    result["content"] = content.decode("utf-8")
                    result["encoding"] = "utf-8"
                except UnicodeDecodeError:
                    result["content"] = base64.b64encode(content).decode("utf-8")
                    result["encoding"] = "base64"

            logger.info(f"Файл '{safe_key}' скачан из бакета '{bucket}'")
            return result

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise PathValidationError(
                    f"Файл '{safe_key}' не найден в бакете '{bucket}'"
                )
            raise

    def list_files(
        self,
        prefix: str = "",
        bucket: str | None = None,
        max_keys: int | None = None,
    ) -> dict[str, Any]:
        """
        Получение списка файлов из S3.

        Args:
            prefix: Префикс для фильтрации
            bucket: Имя бакета (опционально)
            max_keys: Максимальное количество объектов

        Returns:
            Список файлов с метаданными
        """
        bucket = bucket or self.settings.S3_BUCKET_NAME
        max_keys = min(
            max_keys or self.settings.MAX_LIST_OBJECTS, self.settings.MAX_LIST_OBJECTS
        )

        if prefix:
            prefix = validate_path_safety(prefix)

        paginator = self.client.get_paginator("list_objects_v2")

        files = []
        total_size = 0

        page_iterator = paginator.paginate(
            Bucket=bucket, Prefix=prefix, PaginationConfig={"MaxItems": max_keys}
        )

        for page in page_iterator:
            for obj in page.get("Contents", []):
                file_info = {
                    "key": obj["Key"],
                    "size_bytes": obj["Size"],
                    "last_modified": (
                        obj["LastModified"].isoformat()
                        if obj.get("LastModified")
                        else None
                    ),
                    "etag": obj.get("ETag", "").strip('"'),
                    "storage_class": obj.get("StorageClass", "STANDARD"),
                }
                files.append(file_info)
                total_size += obj["Size"]

                if len(files) >= max_keys:
                    break

            if len(files) >= max_keys:
                break

        logger.info(f"Получен список из {len(files)} файлов из бакета '{bucket}'")

        return {
            "bucket": bucket,
            "prefix": prefix,
            "files": files,
            "total_count": len(files),
            "total_size_bytes": total_size,
        }

    def get_file_info(
        self,
        key: str,
        bucket: str | None = None,
    ) -> dict[str, Any]:
        """
        Получение информации о файле.

        Args:
            key: Путь к файлу в бакете
            bucket: Имя бакета (опционально)

        Returns:
            Метаданные файла

        Raises:
            PathValidationError: При невалидном пути или если файл не найден
        """
        bucket = bucket or self.settings.S3_BUCKET_NAME

        # Валидация пути
        safe_key = validate_path_safety(key)

        try:
            response = self.client.head_object(Bucket=bucket, Key=safe_key)

            logger.info(
                f"Получена информация о файле '{safe_key}' из бакета '{bucket}'"
            )

            return {
                "key": safe_key,
                "bucket": bucket,
                "size_bytes": response["ContentLength"],
                "content_type": response.get("ContentType", "application/octet-stream"),
                "last_modified": (
                    response["LastModified"].isoformat()
                    if response.get("LastModified")
                    else None
                ),
                "etag": response.get("ETag", "").strip('"'),
                "metadata": response.get("Metadata", {}),
                "storage_class": response.get("StorageClass", "STANDARD"),
                "exists": True,
            }

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise PathValidationError(
                    f"Файл '{safe_key}' не найден в бакете '{bucket}'"
                )
            raise

    def delete_file(
        self,
        key: str,
        bucket: str | None = None,
    ) -> dict[str, Any]:
        """
        Удаление файла из S3.

        Args:
            key: Путь к файлу в бакете
            bucket: Имя бакета (опционально)

        Returns:
            Информация об удалённом файле

        Raises:
            PathValidationError: При невалидном пути
        """
        bucket = bucket or self.settings.S3_BUCKET_NAME

        safe_key = validate_path_safety(key)

        if not self.check_file_exists(safe_key, bucket):
            raise PathValidationError(
                f"Файл '{safe_key}' не найден в бакете '{bucket}'"
            )

        self.client.delete_object(Bucket=bucket, Key=safe_key)

        logger.info(f"Файл '{safe_key}' удалён из бакета '{bucket}'")

        return {
            "key": safe_key,
            "bucket": bucket,
            "deleted": True,
            "deleted_at": datetime.utcnow().isoformat(),
        }

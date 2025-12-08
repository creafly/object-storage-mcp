import base64

import boto3
import pytest
from moto import mock_aws

from src.core.validators import ConflictError, PathValidationError
from src.services.s3_service import S3Service


class TestS3ServiceUpload:
    """Тесты загрузки файлов."""

    @mock_aws
    def test_upload_text_file(self, settings):
        """Загрузка текстового файла."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)
        result = service.upload_file(
            key="test/hello.txt",
            content="Hello, World!",
            content_type="text/plain",
        )

        assert result["key"] == "test/hello.txt"
        assert result["bucket"] == "test-bucket"
        assert result["size_bytes"] == 13
        assert result["content_type"] == "text/plain"
        assert "uploaded_at" in result

    @mock_aws
    def test_upload_base64_file(self, settings):
        """Загрузка файла в base64."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)
        content = base64.b64encode(b"Binary content").decode()

        result = service.upload_file(
            key="test/binary.bin",
            content=content,
            is_base64=True,
        )

        assert result["key"] == "test/binary.bin"
        assert result["size_bytes"] == 14  # len("Binary content")

    @mock_aws
    def test_upload_conflict_without_overwrite(self, settings):
        """Конфликт при попытке перезаписи без overwrite."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)

        # Первая загрузка
        service.upload_file(key="test/file.txt", content="First")

        # Вторая загрузка без overwrite
        with pytest.raises(ConflictError, match="уже существует"):
            service.upload_file(key="test/file.txt", content="Second")

    @mock_aws
    def test_upload_with_overwrite(self, settings):
        """Перезапись файла с флагом overwrite."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)

        # Первая загрузка
        service.upload_file(key="test/file.txt", content="First")

        # Вторая загрузка с overwrite
        result = service.upload_file(
            key="test/file.txt", content="Second", overwrite=True
        )
        assert result["size_bytes"] == 6  # len("Second")

    @mock_aws
    def test_upload_directory_traversal_blocked(self, settings):
        """Блокировка directory traversal атаки."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)

        with pytest.raises(PathValidationError, match="Directory traversal"):
            service.upload_file(key="../../../etc/passwd", content="hack")

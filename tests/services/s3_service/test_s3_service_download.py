import base64

import boto3
import pytest
from moto import mock_aws

from src.core.validators import PathValidationError
from src.services.s3_service import S3Service


class TestS3ServiceDownload:
    """Тесты скачивания файлов."""

    @mock_aws
    def test_download_text_file(self, settings):
        """Скачивание текстового файла."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        client.put_object(Bucket="test-bucket", Key="test/hello.txt", Body=b"Hello!")

        service = S3Service(settings)
        result = service.download_file(key="test/hello.txt")

        assert result["key"] == "test/hello.txt"
        assert result["content"] == "Hello!"
        assert result["encoding"] == "utf-8"

    @mock_aws
    def test_download_as_base64(self, settings):
        """Скачивание файла в base64."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        client.put_object(Bucket="test-bucket", Key="test/data.bin", Body=b"Binary")

        service = S3Service(settings)
        result = service.download_file(key="test/data.bin", as_base64=True)

        assert result["encoding"] == "base64"
        decoded = base64.b64decode(result["content"])
        assert decoded == b"Binary"

    @mock_aws
    def test_download_nonexistent_file(self, settings):
        """Скачивание несуществующего файла."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)

        with pytest.raises(PathValidationError, match="не найден"):
            service.download_file(key="nonexistent.txt")


class TestS3ServiceList:
    """Тесты листинга файлов."""

    @mock_aws
    def test_list_files(self, settings):
        """Получение списка файлов."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        client.put_object(Bucket="test-bucket", Key="docs/file1.txt", Body=b"1")
        client.put_object(Bucket="test-bucket", Key="docs/file2.txt", Body=b"2")
        client.put_object(Bucket="test-bucket", Key="images/img.png", Body=b"3")

        service = S3Service(settings)
        result = service.list_files()

        assert result["total_count"] == 3
        assert len(result["files"]) == 3

    @mock_aws
    def test_list_files_with_prefix(self, settings):
        """Фильтрация по префиксу."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        client.put_object(Bucket="test-bucket", Key="docs/file1.txt", Body=b"1")
        client.put_object(Bucket="test-bucket", Key="docs/file2.txt", Body=b"2")
        client.put_object(Bucket="test-bucket", Key="images/img.png", Body=b"3")

        service = S3Service(settings)
        result = service.list_files(prefix="docs/")

        assert result["total_count"] == 2
        assert all(f["key"].startswith("docs/") for f in result["files"])

    @mock_aws
    def test_list_files_with_max_keys(self, settings):
        """Ограничение количества результатов."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        for i in range(10):
            client.put_object(Bucket="test-bucket", Key=f"file{i}.txt", Body=b"x")

        service = S3Service(settings)
        result = service.list_files(max_keys=5)

        assert result["total_count"] == 5

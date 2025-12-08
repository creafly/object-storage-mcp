import boto3
import pytest
from moto import mock_aws

from src.core.validators import PathValidationError
from src.services.s3_service import S3Service


class TestS3ServiceInfo:
    """Тесты получения информации о файле."""

    @mock_aws
    def test_get_file_info(self, settings):
        """Получение информации о файле."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        client.put_object(
            Bucket="test-bucket",
            Key="test/doc.pdf",
            Body=b"PDF content",
            ContentType="application/pdf",
        )

        service = S3Service(settings)
        result = service.get_file_info(key="test/doc.pdf")

        assert result["key"] == "test/doc.pdf"
        assert result["size_bytes"] == 11
        assert result["content_type"] == "application/pdf"
        assert result["exists"] is True

    @mock_aws
    def test_get_file_info_nonexistent(self, settings):
        """Информация о несуществующем файле."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)

        with pytest.raises(PathValidationError, match="не найден"):
            service.get_file_info(key="nonexistent.txt")

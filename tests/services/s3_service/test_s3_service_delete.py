import boto3
import pytest
from moto import mock_aws

from src.core.validators import PathValidationError
from src.services.s3_service import S3Service


class TestS3ServiceDelete:
    """Тесты удаления файлов."""

    @mock_aws
    def test_delete_file(self, settings):
        """Удаление файла."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        client.put_object(Bucket="test-bucket", Key="to_delete.txt", Body=b"x")

        service = S3Service(settings)
        result = service.delete_file(key="to_delete.txt")

        assert result["key"] == "to_delete.txt"
        assert result["deleted"] is True

        assert not service.check_file_exists("to_delete.txt")

    @mock_aws
    def test_delete_nonexistent_file(self, settings):
        """Удаление несуществующего файла."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)

        with pytest.raises(PathValidationError, match="не найден"):
            service.delete_file(key="nonexistent.txt")

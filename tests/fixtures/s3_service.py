import boto3
import pytest
from moto import mock_aws

from src.services.s3_service import S3Service


@pytest.fixture
def s3_service(settings, s3_bucket):
    """S3 сервис для тестов."""
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        service = S3Service(settings)
        yield service

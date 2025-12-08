import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def s3_client(aws_credentials):
    """Создаёт моковый S3 клиент."""
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        yield client

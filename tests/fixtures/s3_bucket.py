import pytest


@pytest.fixture
def s3_bucket(s3_client):
    """Создаёт тестовый бакет."""
    s3_client.create_bucket(Bucket="test-bucket")
    return "test-bucket"
